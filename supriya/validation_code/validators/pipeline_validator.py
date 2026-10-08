from utilitycode.logger import get_logger


logger = get_logger(__name__)


class PipelineValidator:

    @staticmethod
    def validate_execution_status(validation_input):

        pipeline_name = validation_input["PipelineName"]
        expected_status = validation_input.get("ExpectedStatus", "PASS")

        pipeline_result = validation_input.get("PipelineResult")

        if not pipeline_result:
            return {
                "Status": "ERROR",
                "Message": "Pipeline execution result was not provided"
            }

        actual_status = pipeline_result.get("Status")

        passed = actual_status == expected_status

        status = "PASS" if passed else "FAIL"

        logger.info(
            "Pipeline status validation | pipeline=%s | expected=%s | actual=%s | status=%s",
            pipeline_name,
            expected_status,
            actual_status,
            status
        )

        return {
            "Status": status,
            "Message": (
                f"Pipeline execution status is {actual_status}"
                if passed
                else f"Expected pipeline status {expected_status}, but got {actual_status}"
            ),
            "Evidence": {
                "PipelineName": pipeline_name,
                "ExpectedStatus": expected_status,
                "ActualStatus": actual_status
            }
        }
    @staticmethod
    def validate_duration(validation_input):

        pipeline_name = validation_input["PipelineName"]
        max_duration = validation_input.get("MaxDuration")

        pipeline_result = validation_input.get("PipelineResult")

        if not pipeline_result:
            return {
                "Status": "ERROR",
                "Message": "Pipeline execution result was not provided"
            }

        actual_duration_seconds = pipeline_result.get("Duration")

        if actual_duration_seconds is None:
            return {
                "Status": "ERROR",
                "Message": "Pipeline duration was not provided"
            }

        if max_duration is None:
            return {
                "Status": "ERROR",
                "Message": "MaxDuration is required for duration validation"
            }

        actual_duration_minutes = actual_duration_seconds / 60

        passed = actual_duration_minutes <= max_duration

        status = "PASS" if passed else "FAIL"

        logger.info(
            "Pipeline duration validation | pipeline=%s | actual=%.2f minutes | maximum=%.2f minutes | status=%s",
            pipeline_name,
            actual_duration_minutes,
            max_duration,
            status
        )

        return {
            "Status": status,
            "Message": (
                f"Pipeline completed within maximum duration"
                if passed
                else f"Pipeline exceeded maximum duration"
            ),
            "Evidence": {
                "PipelineName": pipeline_name,
                "ActualDurationMinutes": round(actual_duration_minutes, 2),
                "MaxDurationMinutes": max_duration
            }
        }