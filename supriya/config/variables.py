from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"

# azure:
azure_document_folder = "Documents"
azure_llm_output_folder = "LLMOutput"
azure_reporting_dir = "ReportingFolder"

# local:
local_document_folder = str(BASE_DIR / "Data" / "Documents")
local_llm_output_folder = str(BASE_DIR / "Data" / "LLMOutput")
local_reporting_dir = str(BASE_DIR / "Data" / "ReportingFolder")
log_dir = str(LOG_DIR)

RAG_ENABLED = False
