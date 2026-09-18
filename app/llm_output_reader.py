# from utilitycode.azure_blob import AzureBlobClient
# from utilitycode.logger import get_logger
# from config.variables import llm_output_folder


# logger = get_logger(__name__)


# class LLMOutputReader:

#     def __init__(self):
#         self.blob_client = AzureBlobClient()

#     def get_json_files(self):
#         logger.info("Reading LLM output files from Azure")

#         json_files = self.blob_client.list_json_blobs(f"{llm_output_folder}/")

#         logger.info(
#             "LLM output files found | count=%s",
#             len(json_files)
#         )

#         return json_files

#     def read_test_scenarios(self, blob_path):
#         logger.info(
#             "Reading LLM test scenarios | path=%s",
#             blob_path
#         )

#         data = self.blob_client.read_json(blob_path)

#         logger.info(
#             "LLM test scenarios successfully read | path=%s",
#             blob_path
#         )

#         return data

import json
import os
from pathlib import Path

from utilitycode.azure_blob import AzureBlobClient
from utilitycode.logger import get_logger
from config.variables import azure_llm_output_folder, local_llm_output_folder


logger = get_logger(__name__)


class LLMOutputReader:

    def __init__(self):
        self.storage_type = os.getenv("STORAGE_TYPE", "local")

        if self.storage_type == "azure":
            self.blob_client = AzureBlobClient()
            self.llm_output_folder = azure_llm_output_folder

        elif self.storage_type == "local":
            self.blob_client = None
            self.llm_output_folder = local_llm_output_folder

        else:
            raise ValueError(f"Invalid STORAGE_TYPE: {self.storage_type}")

    def get_json_files(self):
        logger.info("Reading LLM output files | storage=%s", self.storage_type)

        if self.storage_type == "azure":
            json_files = self.blob_client.list_json_blobs(f"{self.llm_output_folder}/")
        else:
            output_folder = Path(self.llm_output_folder)

            if not output_folder.exists():
                logger.info("LLM output folder does not exist | path=%s", output_folder)
                return []

            json_files = [str(file) for file in output_folder.glob("*.json")]

        logger.info("LLM output files found | count=%s", len(json_files))

        return json_files

    def read_test_scenarios(self, file_path):
        logger.info("Reading LLM test scenarios | path=%s", file_path)

        if self.storage_type == "azure":
            data = self.blob_client.read_json(file_path)
        else:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

        logger.info("LLM test scenarios successfully read | path=%s", file_path)

        return data
