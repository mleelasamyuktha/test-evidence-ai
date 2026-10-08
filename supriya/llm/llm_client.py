import os

from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAI


load_dotenv()


class LLMClient:
    def __init__(self, model):
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")

        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is not set.")

        if not endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is not set.")

        if ".services.ai.azure.com" in endpoint or endpoint.rstrip("/").endswith("/openai/v1"):
            base_url = endpoint.rstrip("/")
            if not base_url.endswith("/openai/v1"):
                base_url += "/openai/v1"
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url,
            )
        else:
            self.client = AzureOpenAI(
                api_key=api_key,
                azure_endpoint=endpoint,
                api_version=api_version
            )
        self.model = model

        self.search_enabled = os.getenv("AZURE_SEARCH_USE_MCP", "true").lower() in {"1", "true", "yes", "on"}
        self.tools = []

        if self.search_enabled:
            search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
            search_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
            api_version = os.getenv("AZURE_SEARCH_API_VERSION", "2026-08-01-preview")

            if search_endpoint and search_key:
                knowledge_bases = []
                context_kb = os.getenv("AZURE_SEARCH_CONTEXT_KB_NAME") or os.getenv("AZURE_SEARCH_KNOWLEDGE_BASE_NAME")
                sql_kb = os.getenv("AZURE_SEARCH_SQL_KB_NAME")

                if context_kb:
                    knowledge_bases.append(context_kb)
                if sql_kb:
                    knowledge_bases.append(sql_kb)

                for index, kb_name in enumerate(knowledge_bases):
                    self.tools.append({
                        "type": "mcp",
                        "server_label": (
                            f"azure_search_knowledge_base_{index + 1}"
                            if len(knowledge_bases) > 1
                            else os.getenv("AZURE_SEARCH_MCP_SERVER_LABEL", "azure_search_knowledge_base")
                        ),
                        "server_url": (
                            f"{search_endpoint}/knowledgebases/{kb_name}/mcp"
                            f"?api-version={api_version}"
                        ),
                        "allowed_tools": [
                            os.getenv("AZURE_SEARCH_ALLOWED_TOOLS", "knowledge_base_retrieve")
                        ],
                        "headers": {
                            "api-key": search_key
                        },
                        "require_approval": "never",
                    })

    def generate(self, prompt, use_context=True):
        context_enabled = use_context and bool(self.tools)
        context_instruction = (
            "Use Azure AI Search knowledge-base context for prior validation rules, test-case patterns, and SQL metadata."
            if context_enabled
            else
            "Do not use Azure AI Search or any external knowledge-base context. Use only the supplied document and live contract/schema."
        )
        payload = {
            "model": self.model,
            "input": prompt,
            "instructions": (
                f"You are a test automation assistant. {context_instruction} "
                "Use the supplied target table schema as the source of truth for table and column names. Do not invent column names, table names, or file paths. "
                "When generating DataQuality.QueryAssertion or related SQL validations, prefer read-only SELECT statements and only use table/column names confirmed by the target schema."
            ),
        }

        if context_enabled:
            payload["tools"] = self.tools

        try:
            response = self.client.responses.create(**payload)
        except Exception as error:
            if not context_enabled:
                self._raise_configuration_error(error)
            self.tools = []
            fallback_payload = dict(payload)
            fallback_payload.pop("tools", None)
            fallback_payload["instructions"] = (
                "You are a test automation assistant. Do not use Azure AI Search or any external knowledge-base context. "
                "Use only the supplied document and live contract/schema. "
                "Use the supplied target table schema as the source of truth for table and column names. "
                "Do not invent column names, table names, or file paths. "
                "When generating DataQuality.QueryAssertion or related SQL validations, prefer read-only SELECT statements and only use table/column names confirmed by the target schema."
            )
            try:
                response = self.client.responses.create(**fallback_payload)
            except Exception as fallback_error:
                self._raise_configuration_error(fallback_error)

        return response.output_text

    def _raise_configuration_error(self, error):
        if getattr(error, "status_code", None) == 404:
            raise RuntimeError(
                "Azure OpenAI resource not found. Verify AZURE_OPENAI_ENDPOINT, "
                "AZURE_OPENAI_DEPLOYMENT, and AZURE_OPENAI_API_VERSION in .env. "
                f"Configured deployment: {self.model}."
            ) from error
        raise error