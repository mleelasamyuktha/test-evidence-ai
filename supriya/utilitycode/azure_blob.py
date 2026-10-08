import json
import os

from dotenv import load_dotenv
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


load_dotenv()


class AzureBlobClient:

    def __init__(self):
        storage_account_name = os.environ["AZURE_STORAGE_ACCOUNT_NAME"]
        container_name = os.environ["AZURE_STORAGE_CONTAINER_NAME"]

        account_url = f"https://{storage_account_name}.blob.core.windows.net"

        auth_type = os.getenv("AZURE_AUTH_TYPE", "default")
        tenant_id = os.getenv("AZURE_TENANT_ID")
        client_id = os.getenv("AZURE_CLIENT_ID")
        client_secret = os.getenv("AZURE_CLIENT_SECRET")

        if auth_type == "client":
            missing = [
                name for name, value in {
                    "AZURE_TENANT_ID": tenant_id,
                    "AZURE_CLIENT_ID": client_id,
                    "AZURE_CLIENT_SECRET": client_secret,
                }.items() if not value
            ]
            if missing:
                raise ValueError(
                    "AZURE_AUTH_TYPE=client requires AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET; missing: "
                    + ", ".join(missing)
                )
            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
            )
        elif auth_type == "default":
            has_full_env_sp = all([tenant_id, client_id, client_secret])
            credential = DefaultAzureCredential(
                exclude_environment_credential=not has_full_env_sp
            )
        else:
            raise ValueError(f"Invalid AZURE_AUTH_TYPE: {auth_type}")
        blob_service_client = BlobServiceClient(
            account_url=account_url,
            credential=credential
        )

        self.container_client = blob_service_client.get_container_client(container_name)

    def list_blobs(self, prefix=None):
        return [
            blob.name
            for blob in self.container_client.list_blobs(name_starts_with=prefix)
        ]

    def blob_exists(self, blob_path):
        blob_client = self.container_client.get_blob_client(blob_path)
        return blob_client.exists()

    def download_blob(self, blob_path):
        blob_client = self.container_client.get_blob_client(blob_path)
        return blob_client.download_blob().readall()

    def upload_blob(self, blob_path, data, overwrite=True):
        blob_client = self.container_client.get_blob_client(blob_path)
        blob_client.upload_blob(data, overwrite=overwrite)

    def delete_blob(self, blob_path):
        blob_client = self.container_client.get_blob_client(blob_path)
        blob_client.delete_blob()

    def move_blob(self, source_path, destination_path):
        source_blob = self.container_client.get_blob_client(source_path)
        destination_blob = self.container_client.get_blob_client(destination_path)

        destination_blob.start_copy_from_url(source_blob.url)
        source_blob.delete_blob()

    def read_json(self, blob_path):
        blob_data = self.download_blob(blob_path)
        return json.loads(blob_data.decode("utf-8-sig"))

    def list_json_blobs(self, prefix):
        return [
            blob_name
            for blob_name in self.list_blobs(prefix)
            if blob_name.lower().endswith(".json")
        ]