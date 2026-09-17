import json


def build_user_prompt(document_text, llm_catalog, table_schema):
    prompt = f"""
You are a test automation assistant for TestEvidenceAI.

Your task is to read the Acceptance Criteria (AC), the Handoff Document, and the Validation Catalog and generate test cases as JSON.

====================
ACCEPTANCE CRITERIA
====================

{document_text}

====================
HANDOFF DOCUMENT
====================

{document_text}

====================
VALIDATION CATALOG
====================

{json.dumps(llm_catalog, indent=2)}

====================
Target Table Schema:
====================

{table_schema}

====================
INSTRUCTIONS
====================

1. Read the Acceptance Criteria carefully.
2. Read the Handoff Document carefully.
3. Identify the validations required to verify each acceptance criterion.
4. Use ONLY validation types available in the Validation Catalog.
5. Do not invent validation types.
6. Use the required inputs defined by the selected validation.
7. Include optional inputs only when they are relevant.
8. Generate one or more test cases for each acceptance criterion.
9. Keep each test case focused on one validation.
10. Do not execute any validation. Only generate the test case definition.
11. Return ONLY valid JSON.
12. Do not include markdown code fences.
13. Do not include explanations outside the JSON.
14. Use the provided target table schema as the source of truth for database column names and data types. Do not invent column names that are not present in the schema.
DataQuality.QueryAssertion is a flexible validation that should be used when the story requires a data-quality, business-rule, record-level, or custom SQL validation that cannot be adequately represented by the other catalog validations.

When using DataQuality.QueryAssertion:
- Generate a valid read-only SQL SELECT query.
- Use only table names and column names provided in the supplied database schema.
- Do not invent columns or tables.
- Use Expected and Operator when the requirement provides enough information to determine an expected result.
- If an expected result cannot be determined from the requirement, omit Expected and return the query result as evidence.
IMPORTANT INPUT MAPPING RULES:

VALIDATION SELECTION RULES:

1. Understand the business and technical requirement from the document before selecting validations.

2. Select only validations that are applicable to the requirement. Do not generate test cases simply to cover every validation in the catalog.

3. The Validation Catalog is the source of truth for available validations, validation types, and their input names.

4. Use the actual source and target schemas provided in the prompt when generating queries. Never invent table names or column names.

5. For Reconciliation.QueryComparison:
   - Use this validation when the requirement requires source-to-target data reconciliation.
   - If the source is a file in Azure Blob Storage, use SourceFile.
   - If the source is another database query or table, use SourceQuery.
   - Always provide TargetQuery for the target database.
   - Select appropriate ComparisonKeys based on the available schema and requirement.
   - Use Comparisons when specific columns need to be compared.
   - Do not provide both SourceFile and SourceQuery.
   - Generate read-only SELECT queries only.
   For Reconciliation.QueryComparison, when Comparisons is used, it must be an array of objects containing:
- Column
- Operator

Example:

"Comparisons": [
    {{
        "Column": "customer_name",
        "Operator": "=="
    }},
    {{
        "Column": "department",
        "Operator": "=="
    }}
]

6. For DataQuality.QueryAssertion:
   - Use this validation for custom data-quality or business-rule checks that are not adequately covered by another catalog validation.
   - Generate a read-only SELECT query using only available tables and columns.
   - If the requirement provides a clear expected result, provide Expected and Operator.
   - If an expected result cannot be determined, omit Expected and return the query result as evidence.

PIPELINE VALIDATIONS:

Use Pipeline.ExecutionStatus when the requirement requires verifying that a pipeline completed successfully or completed with a specific execution status.

Use Pipeline.Duration when the requirement specifies a maximum allowed execution time or performance threshold for the pipeline.

Do not generate Pipeline.Duration when no execution-time threshold is stated in the requirement.

For Pipeline.ExecutionStatus:
- PipelineName is required.
- ExpectedStatus is optional.
- If the requirement explicitly specifies the expected status, use that value.
- If the requirement simply requires successful completion, use "PASS" as ExpectedStatus.

For Pipeline.Duration:
- PipelineName is required.
- MaxDuration is required when duration validation is selected.
- MaxDuration must represent the maximum allowed execution time in seconds.
- Only generate MaxDuration when the requirement explicitly provides a performance threshold.
- Do not invent a MaxDuration value.

7. Do not invent validation input names, tables, columns, expected values, or business rules that are not supported by the document or supplied metadata.
The generated JSON must follow this exact structure:

{{
    "StoryID": "string",
    "TestCases": [
        {{
            "TestCaseID": "string",
            "TestCaseDescription": "string",
            "ValidationCategory": "string",
            "ValidationType": "string",
            "ValidationInput": {{
                "required_input_name": "value",
                "optional_input_name": "value"
            }}
        }}
    ]
}}
"""

    return prompt


# import json


# def build_user_prompt(
#     acceptance_criteria,
#     handoff_document,
#     llm_catalog,
#     table_schema=None
# ):

#     schema_section = ""

#     if table_schema:
#         schema_section = f"""
# ====================
# DATABASE SCHEMA
# ====================

# The following database schema is provided as technical metadata.

# {json.dumps(table_schema, indent=2)}

# Use this schema only when the selected validation capability requires
# database schema information.

# Schema rules:

# - Treat the supplied schema as the source of truth.
# - Use only tables and columns present in the supplied schema.
# - Do not invent table names.
# - Do not invent column names.
# - Do not infer columns that are not present.
# """

#     prompt = f"""
# You are a test automation assistant for TestEvidenceAI.

# Your task is to read the Acceptance Criteria, Handoff Document, and
# Validation Catalog and generate executable test case definitions.

# The most important part of your task is to understand the use case
# described in the documents before deciding what needs to be validated.

# The documents describe WHAT the system is expected to do.

# The Validation Catalog describes WHAT types of verification the
# automation framework is capable of performing and HOW the selected
# verification must be represented.

# Do not treat the catalog as a list of validations that must all be
# used.

# ====================
# ACCEPTANCE CRITERIA
# ====================

# {acceptance_criteria}

# ====================
# HANDOFF DOCUMENT
# ====================

# {handoff_document}

# ====================
# VALIDATION CATALOG
# ====================

# {json.dumps(llm_catalog, indent=2)}

# {schema_section}

# ====================
# REASONING PROCESS
# ====================

# Follow this reasoning process:

# 1. Read and understand the Acceptance Criteria.

# 2. Read and understand the Handoff Document.

# 3. Understand the overall use case and expected system behaviour.

# 4. Identify the individual behaviours, conditions, data, files,
#    outcomes, and business rules that the documents require to be
#    verified.

# 5. For each verification requirement, determine which capability in
#    the Validation Catalog is appropriate.

# 6. Select only the capabilities that are actually required to verify
#    the documented behaviour.

# 7. Generate executable test case definitions using the selected
#    catalog capabilities.

# The requirement documents determine WHAT needs to be verified.

# The Validation Catalog determines WHICH available automation
# capability can verify it and WHAT inputs that capability requires.

# ====================
# VALIDATION SELECTION RULES
# ====================

# - Use only capabilities available in the Validation Catalog.
# - Do not invent validation categories or validation types.
# - Do not generate test cases simply because a capability exists in the
#   catalog.
# - Do not attempt to use every capability in the catalog.
# - Select a capability only when it is relevant to the documented
#   requirement.
# - Select the most appropriate capability for the verification need.
# - Do not create a more complex validation when an available capability
#   adequately verifies the requirement.
# - A single requirement may require multiple test cases when multiple
#   independent aspects need to be verified.
# - Do not create duplicate test cases for the same verification
#   objective.

# ====================
# BUSINESS REQUIREMENT INTERPRETATION
# ====================

# Understand the requirement from the documents rather than relying on
# keywords.

# Do not infer additional requirements from implementation details.

# For example, if the documents state that data is loaded from a source
# into a target, determine what the documents actually require to be
# verified.

# Do not automatically assume that every technical step involved in
# processing the data must itself be validated.

# Only generate a test case when there is a documented verification
# objective.

# Do not add validations simply because they would be technically
# possible or useful.

# ====================
# INPUT RULES
# ====================

# For every selected catalog capability:

# - Use the exact input names defined by the catalog.
# - Provide all required inputs.
# - Provide optional inputs only when relevant.
# - Do not invent input names.
# - Do not invent expected values.
# - Do not invent business rules.
# - Do not invent thresholds.
# - Do not invent file paths.
# - Do not invent table names.
# - Do not invent column names.
# - Do not invent technical information that is not supported by the
#   documents or supplied metadata.

# ====================
# DATABASE AND SCHEMA RULES
# ====================

# When the selected capability requires database information:

# - Use the supplied database schema as the source of truth.
# - Use only tables and columns present in the supplied schema.
# - Do not invent database objects.
# - Do not assume columns that are not present.
# - Generate SQL only when required by the selected catalog capability.
# - SQL must be read-only.
# - Do not generate data-modifying statements.

# If a selected capability does not require database schema information,
# do not use the schema to invent additional validations or technical
# details.

# ====================
# TEST CASE DESIGN
# ====================

# Each test case must represent one clear verification objective.

# TestCaseDescription must:

# - Clearly describe what is being verified.
# - Be based on the documented requirement.
# - Be specific to the use case.
# - Avoid unnecessary implementation details.
# - Not describe an action that has not been requested by the
#   requirement.

# Generate sufficient test cases to verify the documented requirements,
# but do not generate unnecessary test cases.

# ====================
# IMPORTANT RULE
# ====================

# Do not infer additional validation requirements from the Validation
# Catalog.

# The catalog represents available automation capabilities.

# It does NOT represent requirements that must be tested.

# The documents are the only source for determining what behaviour needs
# to be verified.

# ====================
# EXECUTION
# ====================

# Do not execute any validation.

# Do not execute SQL queries.

# Do not modify data.

# Only generate the test case definitions.

# ====================
# OUTPUT FORMAT
# ====================

# Return ONLY valid JSON.

# Do not include markdown code fences.

# Do not include explanations outside the JSON.

# The generated JSON must follow this structure:

# {{
#     "StoryID": "string",
#     "TestCases": [
#         {{
#             "TestCaseID": "string",
#             "TestCaseDescription": "string",
#             "ValidationCategory": "string",
#             "ValidationType": "string",
#             "ValidationInput": {{
#                 "required_input_name": "value",
#                 "optional_input_name": "value"
#             }}
#         }}
#     ]
# }}

# ====================
# FINAL CHECK
# ====================

# Before returning the response, verify:

# 1. The Acceptance Criteria were understood.
# 2. The Handoff Document was understood.
# 3. The generated test cases are directly related to the documented
#    requirements.
# 4. Every selected capability exists in the Validation Catalog.
# 5. Every required input is provided.
# 6. Optional inputs are provided only when relevant.
# 7. No unnecessary validations were generated.
# 8. No requirement was invented.
# 9. No input was invented.
# 10. No table or column was invented.
# 11. Database information is used only when required by the selected
#     capability.
# 12. Generated SQL is read-only.
# 13. No validation was executed.
# 14. The response is valid JSON.
# 15. Return ONLY the JSON object.
# """

#     return prompt