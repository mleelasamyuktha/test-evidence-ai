
from utilitycode.azure_blob import AzureBlobClient


class DocumentReader:

    def __init__(self):
        self.blob_client = AzureBlobClient()

    def read_text(self, blob_path):

        document_data = self.blob_client.download_blob(blob_path)

        return document_data.decode("utf-8-sig")

