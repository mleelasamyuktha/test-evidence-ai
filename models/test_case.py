from dataclasses import dataclass
from typing import Any


@dataclass
class TestCase:
    test_case_id: str
    test_case_description: str
    validation_category: str
    validation_type: str
    validation_input: dict[str, Any]