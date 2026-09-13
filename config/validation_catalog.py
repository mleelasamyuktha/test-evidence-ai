# validation_catalog.py

from validation_code.validators.file_validator import FileValidator


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


    # "Table": {

    #     "Exists": {
    #         "description": "Validate that the expected database table exists.",
    #         "required_inputs": ["TableName"],
    #         "optional_inputs": []
    #     },

    #     "Count": {
    #         "description": "Validate the number of records in a database table, optionally against an expected count or another data source.",
    #         "required_inputs": ["TableName"],
    #         "optional_inputs": ["ExpectedCount", "CompareWith"]
    #     },

    #     "Schema": {
    #         "description": "Validate table schema either against an explicitly defined schema or by comparing it with another data source such as a source file.",
    #         "required_inputs": ["TableName"],
    #         "optional_inputs": ["ExpectedSchema", "CompareWith"]
    #     },

    #     "Null": {
    #         "description": "Validate NULL values in specified table columns.",
    #         "required_inputs": ["TableName", "ColumnName"],
    #         "optional_inputs": ["ExpectedNullCount"]
    #     },

    #     "Duplicate": {
    #         "description": "Validate duplicate records or keys in a table.",
    #         "required_inputs": ["TableName", "KeyColumns"],
    #         "optional_inputs": ["ExpectedDuplicateCount"]
    #     }
    # },


    # "DataQuality": {

    #     "QueryAssertion": {
    #         "description": "Execute a validation query and verify that its result satisfies an expected condition. The expected result may be explicitly provided or derived from the validation rule.",
    #         "required_inputs": ["Query"],
    #         "optional_inputs": [
    #             "Expected",
    #             "Operator"
    #         ]
    #     }
    # },


    # "Reconciliation": {

    #     "QueryComparison": {
    #         "description": "Compare results from two queries using specified keys and comparison rules.",
    #         "required_inputs": [
    #             "SourceQuery",
    #             "TargetQuery",
    #             "ComparisonKeys"
    #         ],
    #         "optional_inputs": [
    #             "Comparisons"
    #         ]
    #     }
    # },


    # "Pipeline": {

    #     "ExecutionStatus": {
    #         "description": "Validate that a pipeline execution completed with the expected status.",
    #         "required_inputs": ["PipelineName"],
    #         "optional_inputs": ["ExpectedStatus"]
    #     },

    #     "Duration": {
    #         "description": "Validate pipeline execution duration, optionally against an explicitly defined threshold.",
    #         "required_inputs": ["PipelineName"],
    #         "optional_inputs": ["MaxDuration"]
    #     }
    # },


    # "Performance": {

    #     "Duration": {
    #         "description": "Validate that an operation completed within the expected performance threshold.",
    #         "required_inputs": ["Operation"],
    #         "optional_inputs": ["MaxDuration"]
    #     }
    # }
}
