from utilitycode.azure_blob import AzureBlobClient
from utilitycode.logger import get_logger
from config.variables import llm_output_folder


logger = get_logger(__name__)


class LLMOutputReader:

    def __init__(self):
        self.blob_client = AzureBlobClient()

    def get_json_files(self):
        logger.info("Reading LLM output files from Azure")

        json_files = self.blob_client.list_json_blobs(f"{llm_output_folder}/")

        logger.info(
            "LLM output files found | count=%s",
            len(json_files)
        )

        return json_files

    def read_test_scenarios(self, blob_path):
        logger.info(
            "Reading LLM test scenarios | path=%s",
            blob_path
        )

        data = self.blob_client.read_json(blob_path)

        logger.info(
            "LLM test scenarios successfully read | path=%s",
            blob_path
        )

        return data