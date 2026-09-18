from datetime import datetime
import argparse
import os
from pathlib import Path

from models.test_case import TestCase
from app.executor import TestExecutor
from app.result_builder import ResultBuilder
from app.llm_output_reader import LLMOutputReader
from llm.testcase_generator import LLMTestGenerator
from utilitycode.logger import get_logger
from config.variables import azure_document_folder, local_document_folder


logger = get_logger(__name__)

def arg_parse():
    parser = argparse.ArgumentParser(description="TestEvidence AI")
    parser.add_argument(
        "--document_path",
        type=str,
        required=True,
        help="Path to the document for generating test scenarios"
    )
    return parser.parse_args()


def main():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    logger.info("TestEvidence AI execution started")

    args = arg_parse()

    generator = LLMTestGenerator(model="gpt-5.6-luna")

    # print(f"{generator.document_folder}/{args.document_path}")
    document_path = f"{generator.document_folder}/{args.document_path}"

    generated_file = generator.generate(document_path)

    logger.info("LLM test scenarios generated | file=%s", generated_file)

    # Create Azure LLM output reader
    reader = LLMOutputReader()

    # Create executor
    executor = TestExecutor()

    # Get JSON files from Azure LLMOutput folder
    json_files = reader.get_json_files()

    logger.info(
        "Found %d story files in Azure LLM output",
        len(json_files)
    )

    for json_file in json_files:

        logger.info(
            "Processing story file | file=%s",
            json_file
        )

        # Read test scenarios from Azure
        data = reader.read_test_scenarios(json_file)

        story_id = data.get("StoryID")

        logger.info(
            "Processing story | story_id=%s",
            story_id
        )

        results = []

        # Execute each test case
        for test_case_data in data["TestCases"]:

            test_case = TestCase(
                test_case_id=test_case_data["TestCaseID"],
                test_case_description=test_case_data["TestCaseDescription"],
                validation_category=test_case_data["ValidationCategory"],
                validation_type=test_case_data["ValidationType"],
                validation_input=test_case_data["ValidationInput"]
            )

            # Execute test
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
        report = ResultBuilder.build_report(
            results=results,
            story_id=story_id
        )

        # Save report
        if os.getenv("STORAGE_TYPE") == "azure":
            name = json_file.split("/")[-1].rsplit(".", 1)[0]
        elif os.getenv("STORAGE_TYPE") == "local":
            name = Path(json_file).stem
        else:
            raise ValueError(
                f"Invalid STORAGE_TYPE: {os.getenv('STORAGE_TYPE')}"
            )
        report_file = ResultBuilder.save_report(
            report,
            name=name,
            timestamp=timestamp
        )

        logger.info(
            "Consolidated report generated | file=%s",
            report_file
        )

    logger.info("TestEvidence AI execution completed")


if __name__ == "__main__":
    main()