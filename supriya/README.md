# TestEvidence AI

TestEvidence AI generates and executes file, database, and API validations from
acceptance criteria, HLDs, API notes, and Word documents.

The project supports:

- LLM-generated SQL validations grounded in live Azure SQL schema
- Azure AI Search knowledge-base context through MCP
- FastAPI customer CRUD endpoints backed by `dbo.Customers`
- Document-driven API test generation and execution
- Streamlit UI for generation, selection, execution, and context comparison
- Local file/output mode with Azure SQL and Azure OpenAI support

## ZIP Handoff

If using VS Code with GitHub Copilot, open the Command Palette or Copilot Chat
and run the workspace prompt:

```text
/setup-qaagent
```

It walks through dependency installation, environment setup, Azure resource
verification, `contextfile` knowledge-source upload, service startup, and smoke
tests. It asks for missing configuration values and never requires secrets in
chat.

After extracting the ZIP:

```bash
cd QAAgent
python3.9 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On macOS, install the SQL Server ODBC prerequisites:

```bash
brew install unixodbc
brew tap microsoft/mssql-release
brew install msodbcsql18
```

On Windows or Linux, install Microsoft ODBC Driver 18 for SQL Server using the
official Microsoft instructions for that operating system.

## Environment Configuration

Copy the template and fill in values supplied by the Azure administrator:

```bash
cp .env.example .env
```

Required configuration groups:

| Group | Important values |
|---|---|
| Storage | `STORAGE_TYPE`, `AZURE_STORAGE_ACCOUNT_NAME`, `AZURE_STORAGE_CONTAINER_NAME` |
| Azure OpenAI | `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_VERSION`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_KEY` |
| Azure AI Search | `AZURE_SEARCH_ENDPOINT`, KB names, API version, admin key |
| Azure SQL | server, database, username, password |

Never commit `.env`, API keys, SQL passwords, or client secrets. The repository
must use `.env.example` for placeholders only. Any credentials previously
shared in chat, committed to source control, or included in a ZIP should be
rotated before handoff.

## Azure Resources

The expected setup is:

1. Azure OpenAI or Azure AI Foundry deployment for the configured model.
2. Azure SQL Database containing `dbo.Customers`.
3. Azure Storage account with a Blob container named `contextfile` for the
	knowledge-source files.
4. Azure Storage container used by the application for documents, generated
	scenarios, and reports. This is configured independently with
	`AZURE_STORAGE_CONTAINER_NAME`.
5. Azure AI Search knowledge bases, for example `context-data` and the SQL
	knowledge base configured in `AZURE_SEARCH_SQL_KB_NAME`.

The names are intentionally separate:

- `contextfile` is the Blob source container requested for uploaded knowledge files.
- `context-data` is an Azure AI Search knowledge-base name.

Uploading files to Blob does not automatically make them retrievable by the
knowledge base unless an Azure AI Search indexer/knowledge-source pipeline is
configured. Confirm that the `contextfile` container is connected to the
`context-data` knowledge base and that indexing has completed.

## Upload Knowledge Sources

From the project root, upload the included corpus to the Blob container named
`contextfile`:

```bash
az login
az storage blob upload-batch \
  --account-name "$AZURE_STORAGE_ACCOUNT_NAME" \
  --destination contextfile \
  --source Data/knowledge_base_sources \
  --auth-mode login \
  --overwrite
```

If the account requires an account key or SAS instead of Entra ID, use the
approved credential method from the Azure administrator. Do not put the key in
this README or in a shell history that will be shared.

After upload:

1. Confirm the files exist in the `contextfile` container.
2. Run or wait for the Azure AI Search indexer/knowledge-source ingestion.
3. Verify retrieval from the `context-data` KB with a query about API test
	ordering, `dbo.Customers`, file reconciliation, or cleanup.
4. Confirm the SQL KB is still connected for SQL patterns.

The source corpus includes API contracts, API generation rules, API edge cases,
API-to-database historical tests, file validation rules, SQL patterns, and
banking data-quality rules.

## Current SQL Contract

The verified live table used by the customer API is:

```text
dbo.Customers
```

Current columns:

```text
customer_id     int
customer_name   nvarchar
email           nvarchar
region          nvarchar
created_on      date
```

The LLM must not invent columns such as `account_count` or
`registration_date` unless the live schema is changed and verified.

## Run the Project

### Start the FastAPI service

```bash
source .venv/bin/activate
PYTHONPATH=. uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Open:

- Swagger: http://localhost:8000/docs
- OpenAPI: http://localhost:8000/openapi.json
- Health: http://localhost:8000/health

### Start the Streamlit UI

In another terminal:

```bash
source .venv/bin/activate
PYTHONPATH=. streamlit run app/streamlit_app.py --server.port 8501
```

Open http://localhost:8501.

The UI supports:

- Data validation
- API testing from `.txt` or `.docx` input
- Local or Azure storage mode
- Select-all and per-test-case execution
- Context-on/context-off comparison

## Smoke Tests

```bash
source .venv/bin/activate
python -m py_compile api/*.py app/streamlit_app.py llm/*.py utilitycode/*.py
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/customers/summary
```

For a full API generation run, upload:

```text
Documents/customer_api_acceptance_criteria.txt
```

Select **API testing**, use `http://localhost:8000`, generate cases, and execute
the selected suite. Write tests use unique IDs and clean up created records.

## Troubleshooting

| Symptom | Check |
|---|---|
| `Target table is required` | Use Data validation with a `Target table:` line. Use API testing for API/HLD documents. |
| Invalid column name | Inspect `INFORMATION_SCHEMA.COLUMNS`; update the document or schema, never guess a column. |
| Azure SQL login timeout | Check firewall rules, server/database credentials, ODBC Driver 18, and network access. |
| KB context is missing | Confirm `contextfile` upload, indexer completion, KB name `context-data`, and MCP configuration. |
| Swagger is unavailable | Start Uvicorn on port 8000 before generating API tests. |
| Streamlit button appears stale | Refresh the page after changing mode or uploaded file. |

## Security Notes

- No bearer token is required for the hackathon API service, but production
  deployments must add authentication and authorization.
- Use least-privilege Azure identities where possible.
- Do not expose `.env` in screenshots, ZIP files, logs, or commits.
- API write tests must use disposable IDs and cleanup.