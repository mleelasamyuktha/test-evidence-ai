from config.validation_catalog import VALIDATION_CATALOG
from utilitycode.logger import get_logger
from app.ingestion_pipeline import IngestionPipeline


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

            raise ValueError({
                "Status": "ERROR",
                "Message": f"Unknown validation category: {category}"
            })

        # Check whether the validation type exists
        if validation_type not in VALIDATION_CATALOG[category]:

            logger.error(
                "Unknown validation type | test_case_id=%s | category=%s | type=%s",
                test_case_id,
                category,
                validation_type
            )

            raise ValueError({
                "Status": "ERROR",
                "Message": (
                    f"Unknown validation type: "
                    f"{category} -> {validation_type}"
                )
            })

        # Get the validator implementation
        validator = VALIDATION_CATALOG[category][validation_type]["validator"]

        logger.info(
            "Validator found | test_case_id=%s | validator=%s",
            test_case_id,
            validator.__name__
        )

        try:

            validation_input = test_case.validation_input.copy()

            # Pipeline validations require the actual pipeline
            # execution result before validation.
            if category == "Pipeline":

                pipeline_name = validation_input["PipelineName"]
                # source_file = validation_input["SourceFile"]
                # target_table = validation_input["TargetTable"]

                logger.info(
                    "Starting pipeline | pipeline=%s",
                    pipeline_name
                    # source_file,
                    # target_table
                )

                pipeline = IngestionPipeline()

                pipeline_result = pipeline.ingest_csv_to_table(
                    # source_file=source_file,
                    # target_table=target_table
                )

                logger.info(
                    "Pipeline completed | pipeline=%s | status=%s | duration=%.3f",
                    pipeline_name,
                    pipeline_result.get("Status"),
                    pipeline_result.get("Duration", 0)
                )

                # Add actual runtime information for the validator
                validation_input["PipelineResult"] = pipeline_result

            # Execute the validator
            result = validator(validation_input)

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