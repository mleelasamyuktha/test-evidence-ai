from email.mime import text
import json
import os

from llm.document_reader import DocumentReader
from llm.get_llm_catalog import get_llm_catalog
from llm.prompt_builder import build_user_prompt
from llm.llm_client import LLMClient
from utilitycode.azure_blob import AzureBlobClient
from config.variables import azure_llm_output_folder, azure_document_folder, local_llm_output_folder, local_document_folder
from utilitycode.azure_sql import AzureSQLClient


class LLMTestGenerator:

    def __init__(self, model):
        self.llm_client = LLMClient(model=model)
        self.document_reader = DocumentReader()
        self.blob_client = AzureBlobClient()
        self.sql_client = AzureSQLClient()

        self.storage_type = os.getenv("STORAGE_TYPE", "local")

        if self.storage_type == "azure":
            self.blob_client = AzureBlobClient()
            self.sql_client = AzureSQLClient()
            self.llm_output_folder = azure_llm_output_folder
            self.document_folder = azure_document_folder

        elif self.storage_type == "local":
            self.blob_client = None
            self.sql_client = None

            self.llm_output_folder = local_llm_output_folder
            self.document_folder = local_document_folder

        else:
            raise ValueError(
                f"Invalid STORAGE_TYPE: {self.storage_type}"
            )

    def generate(self, document_path):

        document_text = self.document_reader.read_text(document_path)
        # print("DOCUMENT TEXT LENGTH:", len(document_text))


        catalog = get_llm_catalog()

        # First LLM call without database schema
        prompt = build_user_prompt(
            document_text,
            catalog,
            None
        )

        result = self.llm_client.generate(prompt)
        # print(result)

        test_scenarios = json.loads(result)

        # Check whether any generated validation requires database schema
        if self._requires_schema(test_scenarios, catalog):

            target_table = self._extract_target_table(document_text)

            if not target_table:
                raise ValueError(
                    "Target table is required for schema-based validation"
                )

            schema_name, table_name = target_table.split(".", 1)

            table_schema = self.sql_client.get_table_schema(
                table_name,
                schema_name
            )

            # Second LLM call with database schema
            prompt = build_user_prompt(
                document_text,
                catalog,
                table_schema
            )

            result = self.llm_client.generate(prompt)

            test_scenarios = json.loads(result)

        story_id = test_scenarios["StoryID"]

        blob_path = f"{self.llm_output_folder}/{story_id}_TestScenarios.json"

        json_data = json.dumps(
            test_scenarios,
            indent=4
        )

        if self.storage_type == "azure":
            self.blob_client.upload_blob(
                blob_path,
                json_data.encode("utf-8"),
                overwrite=True
            )
        else:
            os.makedirs(self.llm_output_folder, exist_ok=True)

            local_path = os.path.join(
                self.llm_output_folder,
                f"{story_id}_TestScenarios.json"
            )

            with open(local_path, "w", encoding="utf-8") as f:
                f.write(json_data)

            blob_path = local_path
        return blob_path

    def _extract_target_table(self, document_text):

        for line in document_text.splitlines():

            if line.lower().startswith("target table:"):
                return line.split(":", 1)[1].strip()

        return None

    def _requires_schema(self, test_scenarios, catalog):

        for test_case in test_scenarios["TestCases"]:

            category = test_case["ValidationCategory"]
            validation_type = test_case["ValidationType"]

            validation = catalog[category][validation_type]

            if validation.get("requires_schema", False):
                return True

        return False
