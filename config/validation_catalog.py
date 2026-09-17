# validation_catalog.py

from validation_code.validators.data_quality_validator import DataQualityValidator
from validation_code.validators.file_validator import FileValidator
from validation_code.validators.table_validator import TableValidator
from validation_code.validators.reconciliation_validator import ReconciliationValidator
from validation_code.validators.pipeline_validator import PipelineValidator

VALIDATION_CATALOG = {

    "File": {

        "Exists": {
            "description": "Validate that the expected file exists.",
            "required_inputs": ["FilePath"],
            "optional_inputs": [],
            "validator": FileValidator.validate_exists
        },

        "Header": {
            "description": "Validate file headers either against explicitly expected headers or against another source such as a database table.",
            "required_inputs": ["FilePath"],
            "optional_inputs": ["ExpectedHeaders", "CompareWith"],
            "validator": FileValidator.validate_header
        },

        "Count": {
            "description": "Validate the number of records in a file, optionally against an expected count or another data source.",
            "required_inputs": ["FilePath"],
            "optional_inputs": ["ExpectedCount", "CompareWith"],
            "validator": FileValidator.validate_count
        },

        "Format": {
            "description": "Validate that a file has the expected format or extension.",
            "required_inputs": ["FilePath"],
            "optional_inputs": ["ExpectedFormat"],
            "validator": FileValidator.validate_format
        },

        "Archive": {
            "description": "Validate that a processed file is moved or copied to the expected archive location.",
            "required_inputs": ["SourcePath", "ArchivePath"],
            "optional_inputs": ["ExpectedStatus"],
            "validator": FileValidator.validate_archive
        }
    },


    "Table": {

        "Exists": {
            "description": "Validate that the expected database table exists.",
            "required_inputs": ["TableName"],
            "optional_inputs": [],
            "validator": TableValidator.validate_exists
        },

        "Count": {
            "description": "Validate the number of records in a database table, optionally against an expected count or another data source.",
            "required_inputs": ["TableName"],
            "optional_inputs": ["ExpectedCount", "CompareWith"],
            "validator": TableValidator.validate_count
        },

        "Schema": {
            "description": "Validate table schema either against an explicitly defined schema or by comparing it with another data source such as a source file.",
            "required_inputs": ["TableName"],
            "optional_inputs": ["ExpectedSchema", "CompareWith"],
            "validator": TableValidator.validate_schema
        },

        "Null": {
            "description": "Validate NULL values in specified table columns.",
            "required_inputs": ["TableName", "ColumnNames"],
            "optional_inputs": [],
            "validator": TableValidator.validate_null
        },

        "Duplicate": {
            "description": "Validate duplicate records or keys in a table.",
            "required_inputs": ["TableName", "ColumnNames"],
            "optional_inputs": ["ExpectedDuplicateCount"],
            "validator": TableValidator.validate_duplicate
        }
    },


    "DataQuality": {

        "QueryAssertion": {
            "description": "Execute a validation query and verify that its result satisfies an expected condition. The expected result may be explicitly provided or derived from the validation rule.",
            "required_inputs": ["Query"],
            "optional_inputs": ["Expected","Operator"],
            "requires_schema": True,
            "validator": DataQualityValidator.validate_query_assertion
        }
    },


    "Reconciliation": {
        "QueryComparison": {
            "description": "Compare source and target data. The source can be either a SQL query or a CSV file in Azure Blob Storage, and the target is a SQL query. Use SourceQuery for SQL-to-SQL comparison or SourceFile for CSV-to-SQL comparison.",
            "required_inputs": [
                "TargetQuery",
                "ComparisonKeys"
            ],
            "optional_inputs": [
                "SourceQuery",
                "SourceFile",
                "Comparisons"
            ],
            "requires_schema": True,
            "validator": ReconciliationValidator.validate_query_comparison
        }
    },


    "Pipeline": {

        "ExecutionStatus": {
            "description": "Validate that a pipeline execution completed with the expected status.",
            "required_inputs": ["PipelineName"],
            "optional_inputs": ["ExpectedStatus"],
            "validator": PipelineValidator.validate_execution_status
        },

        "Duration": {
            "description": "Validate pipeline execution duration, optionally against an explicitly defined threshold.",
            "required_inputs": ["PipelineName"],
            "optional_inputs": ["MaxDuration"],
            "validator": PipelineValidator.validate_duration
        }
    },
}
