from email.mime import text
import json

from llm.document_reader import DocumentReader
from llm.get_llm_catalog import get_llm_catalog
from llm.prompt_builder import build_user_prompt
from llm.llm_client import LLMClient
from utilitycode.azure_blob import AzureBlobClient
from config.variables import llm_output_folder
from utilitycode.azure_sql import AzureSQLClient


class LLMTestGenerator:

    def __init__(self, model):
        self.llm_client = LLMClient(model=model)
        self.document_reader = DocumentReader()
        self.blob_client = AzureBlobClient()
        self.sql_client = AzureSQLClient()

    def generate(self, document_path):

        document_text = self.document_reader.read_text(document_path)

        catalog = get_llm_catalog()

        # First LLM call without database schema
        prompt = build_user_prompt(
            document_text,
            catalog,
            None
        )

        result = self.llm_client.generate(prompt)

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

        blob_path = f"{llm_output_folder}/{story_id}_TestScenarios.json"

        json_data = json.dumps(
            test_scenarios,
            indent=4
        )

        self.blob_client.upload_blob(
            blob_path,
            json_data.encode("utf-8"),
            overwrite=True
        )

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
