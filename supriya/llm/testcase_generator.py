import json
import os

from llm.document_reader import DocumentReader
from llm.get_llm_catalog import get_llm_catalog
from llm.prompt_builder import build_user_prompt
from llm.llm_client import LLMClient
from utilitycode.azure_blob import AzureBlobClient
from config.variables import azure_llm_output_folder, azure_document_folder, local_llm_output_folder, local_document_folder
from utilitycode.azure_sql import AzureSQLClient

from config import variables
from rag.retriever import RAGRetriever
from rag.context_builder import RAGContextBuilder
from rag.entity_resolver import EntityResolver
from rag.schema_resolver import SchemaResolver
from rag.schema_context_builder import SchemaContextBuilder


class LLMTestGenerator:

    def __init__(self, model, use_context=True):
        self.llm_client = LLMClient(model=model)
        self.use_context = use_context
        self.storage_type = os.getenv("STORAGE_TYPE", "local")
        self.document_reader = DocumentReader()
        self.sql_client = AzureSQLClient()

        if self.storage_type == "azure":
            self.blob_client = AzureBlobClient()
            self.llm_output_folder = azure_llm_output_folder
            self.document_folder = azure_document_folder

        elif self.storage_type == "local":
            self.blob_client = None

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

        schema_context = "No relevant database schemas were resolved."
        rag_context = None

        entity_resolver = EntityResolver()

        if variables.RAG_ENABLED:
            rag_retriever = RAGRetriever()
            rag_results = rag_retriever.retrieve(document_text, top_k=5)

            rag_context_builder = RAGContextBuilder()
            rag_context = rag_context_builder.build_context(rag_results)

            resolved_tables = entity_resolver.resolve_from_results(rag_results)

        else:
            resolved_tables = entity_resolver.resolve_from_text(document_text)

        schema_resolver = SchemaResolver()
        schemas = schema_resolver.resolve_schemas(resolved_tables)

        schema_context_builder = SchemaContextBuilder()
        schema_context = schema_context_builder.build_context(schemas)

        # Generate with live schema whenever a target table is provided.
        prompt = build_user_prompt(
            document_text,
            catalog,
            schema_context,
            rag_context)

        result = self.llm_client.generate(prompt, use_context=self.use_context)
        test_scenarios = json.loads(result)
        self._remove_non_executable_cases(test_scenarios)

        # # A schema-dependent test without a target table cannot be grounded.
        # if self._requires_schema(test_scenarios, catalog) and not table_schema:
        #     raise ValueError(
        #         "Target table is required for schema-based validation"
        #     )

        # if table_schema:
        #     # Re-run only if the model returned a schema-dependent plan that needs
        #     # the same grounded prompt after its initial interpretation.
        #     prompt = build_user_prompt(
        #         document_text,
        #         catalog,
        #         table_schema
        #     )

        #     result = self.llm_client.generate(prompt, use_context=self.use_context)

        #     test_scenarios = json.loads(result)
        #     self._remove_non_executable_cases(test_scenarios)

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
            if isinstance(line, bytes):
                line = line.decode("utf-8", errors="ignore")

            if isinstance(line, str) and line.lower().startswith("target table:"):
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

    def _remove_non_executable_cases(self, test_scenarios):
        unsupported_markers = (
            "unexecutable",
            "placeholder",
            "enforcement requirement",
            "generation requirement",
            "must reject queries",
            "uses live schema and is read-only",
            "ensure generated validation sql",
            "read-only generated query",
        )
        executable_cases = []
        removed_cases = []

        for case in test_scenarios.get("TestCases", []):
            description = str(
                case.get("TestCaseDescription", case.get("Description", ""))
            ).lower()
            if any(marker in description for marker in unsupported_markers):
                removed_cases.append({
                    "Requirement": case.get("TestCaseDescription", "Unsupported requirement"),
                    "Reason": "This requirement is a policy or cannot be executed against the generated validation contract.",
                    "MissingSchemaObjects": [],
                })
            else:
                executable_cases.append(case)

        test_scenarios["TestCases"] = executable_cases
        if removed_cases:
            test_scenarios.setdefault("UnsupportedRequirements", []).extend(removed_cases)
