from pathlib import Path
from datetime import datetime
from config.variables import reporting_dir


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
    def save_report(report, name, timestamp, output_path=reporting_dir):

        output_dir = Path(output_path)

        output_dir.mkdir(parents=True, exist_ok=True)

        report_file = (output_dir / f"test_report_{name}_{timestamp}.md")

        with open(
            report_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(report)

        return report_file
