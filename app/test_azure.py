# from azure.identity import DefaultAzureCredential
# from azure.storage.blob import BlobServiceClient

# storage_account_name = "testevidenceaistorage"
# account_url = f"https://{storage_account_name}.blob.core.windows.net"

# credential = DefaultAzureCredential()
# blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)

# container_client = blob_service_client.get_container_client("testevidenceaicontainer")

# for blob in container_client.list_blobs():
#     print(blob.name)

# from azure.identity import ClientSecretCredential
# from azure.storage.blob import BlobServiceClient
# import os

# storage_account_name = "testevidenceaistorage"
# account_url = f"https://{storage_account_name}.blob.core.windows.net"

# credential = ClientSecretCredential(
#     tenant_id=os.environ["AZURE_TENANT_ID"],
#     client_id=os.environ["AZURE_CLIENT_ID"],
#     client_secret=os.environ["AZURE_CLIENT_SECRET"]
# )

# blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)

# container_client = blob_service_client.get_container_client("testevidenceaicontainer")

# for blob in container_client.list_blobs():
#     print(blob.name)

# from utilitycode.azure_blob import AzureBlobClient


# blob_client = AzureBlobClient()

# for blob in blob_client.list_blobs():
#     print(blob)

# from validation_code.validators.file_validator import FileValidator


# result = FileValidator.validate_archive({
#     "SourcePath": "SourceFolder/customer_data.csv",
#     "ArchivePath": "ArchiveFolder"
# })

# print(result)

# from utilitycode.azure_sql import AzureSQLClient


# def main():

#     sql_client = AzureSQLClient()

#     result = sql_client.execute_query(
#         "SELECT COUNT(*) FROM dbo.customer_data"
#     )

#     print("Table count:", result[0][0])

#     sql_client.close()


# if __name__ == "__main__":
#     main()

from validation_code.validators.table_validator import TableValidator

result = TableValidator.validate_duplicate({
    "TableName": "dbo.customer_data",
    "ColumnNames": ["customer_id"]
})

print(result)