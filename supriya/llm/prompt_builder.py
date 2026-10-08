import json


def build_user_prompt(document_text, llm_catalog, schema_context, rag_context=None):
    rag_section = f"""
HISTORICAL BUSINESS KNOWLEDGE (RAG):
{rag_context}
Use this historical knowledge to discover business relationships,
dependencies, and additional testable scenarios that are not explicitly
stated in the current requirement.
IMPORTANT RAG REASONING:
1. First identify test cases directly required by the current requirement.
2. Then analyze the historical business knowledge for relationships involving
   the entities in the current requirement.
3. If historical knowledge reveals a related business entity that is not
   explicitly mentioned in the current requirement, consider whether that
   relationship creates an additional testable scenario.
4. Use the database schema to determine whether the additional scenario can
   actually be validated.
5. If the schema supports the relationship, generate an additional test case.
6. Do not generate a test case merely because an entity appears in historical
   text. There must be a meaningful business relationship.
7. Do not invent columns, tables, identifiers, or relationships that are not
   supported by the schema.
8. RAG-derived tests must be additional tests, not replacements for tests
   required directly by the current requirement.
9. Prefer cross-entity consistency validations when historical knowledge
   establishes a business relationship between entities.
10. If historical knowledge suggests a relationship but the schema does not
    support validating it, do not invent a validation. Treat it as an
    unsupported scenario.
For example:
Current requirement:
"Every deposit should be associated with a valid account."
Historical knowledge:
"Deposits are associated with customer accounts.
A customer account belongs to a customer."
If the schema supports the relationship, the model should consider:
- Deposi→ Account validation
- Deposi→ Account → Customer consistency validation
The second test is a RAG-derived test because the current requirement did not
explicitly ask for customer validation.
"""    
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
RELEVANT DATABASE SCHEMAS
====================

{schema_context}

{rag_section}

====================
INSTRUCTIONS
====================
Use only tables and columns present in the supplied database schemas.

Do not invent table names or column names.

A business entity mentioned in the requirements or retrieved historical knowledge does not by itself authorize a physical table or column.

Only use a physical table when it is present in the supplied database schemas.

1. Read the Acceptance Criteria carefully.
2. Read the Handoff Document carefully.
3. Identify the validations required to verify each acceptance criterion.
4. Use ONLY validation types available in the Validation Catalog.
5. Do not invent validation types.
6. Use the required inputs defined by the selected validation.
7. Include optional inputs only when they are relevant.
8. Generate test cases only for acceptance criteria that can be executed with the supplied catalog and live schema.
9. Keep each test case focused on one validation.
10. Do not execute any validation. Only generate the test case definition.
11. Return ONLY valid JSON.
12. Do not include markdown code fences.
13. Do not include explanations outside the JSON.
14. Use the provided target table schema as the source of truth for database column names and data types. Do not invent column names that are not present in the schema.
15. Acceptance criteria may describe a business concept using a field name that does not exist in the live table. Treat that as an unsupported requirement: do not translate it into SQL using the story wording, do not guess a synonym, and do not use a column from the knowledge base instead.
16. Do not create a placeholder, pseudo-test, or unexecutable TestCase. Put unsupported requirements in UnsupportedRequirements instead.
17. Requirements about how the LLM should generate SQL, schema grounding, read-only safety, or query rejection are generation/execution policies, not database TestCases. Do not create TestCases for those policies.
DataQuality.QueryAssertion is a flexible validation that should be used when the story requires a data-quality, business-rule, record-level, or custom SQL validation that cannot be adequately represented by the other catalog validations.

For custom or bespoke business rules, the LLM is allowed to generate a read-only SQL SELECT statement directly for the selected validation type. Do not limit the SQL to only static validation templates when the acceptance criteria require custom logic.

When using DataQuality.QueryAssertion, CustomSQL, or GeneratedSQL:
- Generate a valid read-only SQL SELECT query.
- Use only table names and column names provided in the supplied database schema.
- Do not invent columns or tables.
- If a requested business field is absent from the supplied schema, do not generate a query that references it. Record the requirement in UnsupportedRequirements with the missing field and reason.
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
8. Every TestCase must be executable immediately: it must select a real catalog validator and contain all required inputs. Never use descriptions such as "placeholder", "unexecutable", or "not supported" in TestCases.
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
    ],
    "UnsupportedRequirements": [
        {{
            "Requirement": "string",
            "Reason": "string",
            "MissingSchemaObjects": ["string"]
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