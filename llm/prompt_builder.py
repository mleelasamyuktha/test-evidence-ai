import json


def build_user_prompt(document_text, llm_catalog):
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

IMPORTANT INPUT MAPPING RULES:

- The Validation Catalog is the source of truth for validation inputs.
- For each selected validation, inspect its required_inputs and optional_inputs.
- Every required input must be placed inside ValidationInput.
- Relevant optional inputs must also be placed inside ValidationInput.
- Use the exact input names defined in the Validation Catalog.
- Never put validation inputs at the TestCase level.
- Never combine validation inputs into Query.
- Do not invent validation input names.
- Query should only be included inside ValidationInput when Query is defined as an input for the selected validation.
- The ValidationInput object must contain only inputs relevant to the selected validation.

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