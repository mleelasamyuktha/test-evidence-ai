import json

from llm.document_reader import DocumentReader
from llm.get_llm_catalog import get_llm_catalog
from llm.prompt_builder import build_user_prompt
from llm.llm_client import LLMClient
from utilitycode.azure_blob import AzureBlobClient
from config.variables import llm_output_folder


class LLMTestGenerator:

    def __init__(self, model):
        self.llm_client = LLMClient(model=model)
        self.document_reader = DocumentReader()
        self.blob_client = AzureBlobClient()

    def generate(self, document_path):

        document_text = self.document_reader.read_text(document_path)

        catalog = get_llm_catalog()

        prompt = build_user_prompt(
            document_text,
            catalog
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

