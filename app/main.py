import json
from datetime import datetime
from pathlib import Path
from models.test_case import TestCase
from app.executor import TestExecutor
from app.result_builder import ResultBuilder
from utilitycode.logger import get_logger
from config.variables import llm_output_dir


logger = get_logger(__name__)


def main():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logger.info("TestEvidence AI execution started")

    # 2. Create executor
    executor = TestExecutor()

    json_files = sorted(Path(llm_output_dir).glob("*.json"))

    logger.info(
        "Found %d story files in LLM output directory",
        len(json_files)
    )

    for json_file in json_files:

        logger.info(
            "Processing story file | file=%s",
            json_file
        )

        # 1. Read test cases
        with open(json_file, "r") as file:
            data = json.load(file)
            story_id = data.get("StoryID")

            logger.info(
                "Processing story | story_id=%s",
                story_id
            )

        results = []

        # 3. Execute each test case
        for test_case_data in data["TestCases"]:

            test_case = TestCase(
                test_case_id=test_case_data["TestCaseID"],
                test_case_description=test_case_data["TestCaseDescription"],
                validation_category=test_case_data["ValidationCategory"],
                validation_type=test_case_data["ValidationType"],
                validation_input=test_case_data["ValidationInput"]
            )

            # 4. Execute test
            result = executor.execute(test_case)

            results.append({
                "TestCaseID": test_case.test_case_id,
                "Description": test_case.test_case_description,
                "Category": test_case.validation_category,
                "ValidationType": test_case.validation_type,
                "Status": result.get("Status"),
                "Message": result.get("Message"),
                "Evidence": result.get("Evidence", {})
            })

        # Build consolidated report
        report = ResultBuilder.build_report(results=results,story_id=data.get("StoryID"))

        # Save report
        report_file = ResultBuilder.save_report(report, name=json_file.stem, timestamp=timestamp)

        logger.info("Consolidated report generated | file=%s",report_file)

        logger.info("TestEvidence AI execution completed")


if __name__ == "__main__":
    main()
