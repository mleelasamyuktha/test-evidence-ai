from config.validation_catalog import VALIDATION_CATALOG
from utilitycode.logger import get_logger


logger = get_logger(__name__)


class TestExecutor:

    def execute(self, test_case):

        test_case_id = test_case.test_case_id
        category = test_case.validation_category
        validation_type = test_case.validation_type

        logger.info(
            "Starting test execution | test_case_id=%s | category=%s | type=%s",
            test_case_id,
            category,
            validation_type
        )

        # Check whether the validation category exists
        if category not in VALIDATION_CATALOG:

            logger.error(
                "Unknown validation category | test_case_id=%s | category=%s",
                test_case_id,
                category
            )

            return {
                "Status": "ERROR",
                "Message": f"Unknown validation category: {category}"
            }

        # Check whether the validation type exists
        if validation_type not in VALIDATION_CATALOG[category]:

            logger.error(
                "Unknown validation type | test_case_id=%s | category=%s | type=%s",
                test_case_id,
                category,
                validation_type
            )

            return {
                "Status": "ERROR",
                "Message": (
                    f"Unknown validation type: "
                    f"{category} -> {validation_type}"
                )
            }

        # Get the validator implementation
        validator = VALIDATION_CATALOG[category][validation_type]["validator"]

        logger.info(
            "Validator found | test_case_id=%s | validator=%s",
            test_case_id,
            validator.__name__
        )

        # Execute the validator
        try:

            result = validator(test_case.validation_input)

            logger.info(
                "Test execution completed | test_case_id=%s | status=%s",
                test_case_id,
                result.get("Status")
            )

            return result

        except Exception:

            logger.exception(
                "Test execution failed unexpectedly | test_case_id=%s",
                test_case_id
            )

            return {
                "Status": "ERROR",
                "Message": "Unexpected error during test execution"
            }
