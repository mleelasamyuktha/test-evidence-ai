
# from utilitycode.azure_blob import AzureBlobClient


# class DocumentReader:

#     def __init__(self):
#         self.blob_client = AzureBlobClient()

#     def read_text(self, blob_path):

#         document_data = self.blob_client.download_blob(blob_path)

#         return document_data.decode("utf-8-sig")

import os
from pathlib import Path

from utilitycode.azure_blob import AzureBlobClient


class DocumentReader:

    def __init__(self):
        self.storage_type = os.getenv("STORAGE_TYPE", "local")

        if self.storage_type == "azure":
            self.blob_client = AzureBlobClient()
        elif self.storage_type == "local":
            self.blob_client = None
        else:
            raise ValueError(
                f"Invalid STORAGE_TYPE: {self.storage_type}"
            )

    def read_text(self, blob_path):

        if self.storage_type == "azure":
            document_data = self.blob_client.download_blob(blob_path)
        else:
            with open(blob_path, "rb") as f:
                document_data = f.read()

        if isinstance(document_data, bytes):
            return document_data.decode("utf-8-sig")

        return str(document_data)
