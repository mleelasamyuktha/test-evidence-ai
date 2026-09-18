from datetime import datetime
import os
from pathlib import Path

from utilitycode.azure_blob import AzureBlobClient
from config.variables import azure_reporting_dir, local_reporting_dir


class ResultBuilder:

    @staticmethod
    def build_report(results, story_id=None):

        total_tests = len(results)

        passed = sum(
            1 for result in results
            if result.get("Status") == "PASS"
        )

        failed = sum(
            1 for result in results
            if result.get("Status") == "FAIL"
        )

        errors = sum(
            1 for result in results
            if result.get("Status") == "ERROR"
        )

        # Determine overall status
        if errors > 0:
            overall_status = "ERROR"
        elif failed > 0:
            overall_status = "FAIL"
        else:
            overall_status = "PASS"

        # Create report
        report = []

        report.append("# TestEvidence AI - Test Execution Report\n")

        report.append(
            f"**Execution Time:** "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        report.append(
            f"**Story ID:** {story_id or 'N/A'}\n"
        )

        report.append("---\n")

        # Summary
        report.append("## Execution Summary\n")

        report.append(f"- **Total Tests:** {total_tests}")
        report.append(f"- **Passed:** {passed}")
        report.append(f"- **Failed:** {failed}")
        report.append(f"- **Errors:** {errors}")

        report.append(
            f"\n### Overall Status: **{overall_status}**\n"
        )

        report.append("---\n")

        # Individual test results
        report.append("## Test Results\n")

        for result in results:

            report.append(
                f"### {result.get('TestCaseID', 'N/A')}\n"
            )

            report.append(
                f"**Description:** "
                f"{result.get('Description', 'N/A')}\n"
            )

            report.append(
                f"**Validation:** "
                f"{result.get('Category', 'N/A')} → "
                f"{result.get('ValidationType', 'N/A')}\n"
            )

            report.append(
                f"**Status:** "
                f"**{result.get('Status', 'N/A')}**\n"
            )

            report.append(
                f"**Result:** "
                f"{result.get('Message', 'N/A')}\n"
            )

            # Evidence
            report.append("#### Evidence\n")

            evidence = result.get("Evidence", {})

            if evidence:

                for key, value in evidence.items():

                    report.append(
                        f"- **{key}:** `{value}`"
                    )

            else:

                report.append(
                    "No evidence available."
                )

            report.append("\n---\n")

        return "\n".join(report)

    @staticmethod
    def save_report(report, name, timestamp):
        report_file_name = f"test_report_{name}_{timestamp}.md"

        storage_type = os.getenv("STORAGE_TYPE", "local")

        if storage_type == "azure":
            blob_client = AzureBlobClient()
            blob_path = f"{azure_reporting_dir}/{report_file_name}"

            blob_client.upload_blob(blob_path, report.encode("utf-8"), overwrite=True)

            return blob_path

        elif storage_type == "local":
            output_folder = Path(local_reporting_dir)
            output_folder.mkdir(parents=True, exist_ok=True)

            print(output_folder)
            print(report_file_name)

            file_path = output_folder / report_file_name

            with open(file_path, "w", encoding="utf-8") as file:

                file.write(report)

            return str(file_path)

        else:
            raise ValueError(f"Invalid STORAGE_TYPE: {storage_type}")
