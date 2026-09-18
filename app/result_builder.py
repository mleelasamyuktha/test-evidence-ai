from datetime import datetime
from html import escape
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

        execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        overall_class = overall_status.lower()
        report = [
            "<!DOCTYPE html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>TestEvidence AI - Test Execution Report</title>",
            "<style>",
            ":root { color-scheme: light; font-family: Inter, Segoe UI, sans-serif; --navy: #16324f; --teal: #087f8c; --coral: #e76f51; --gold: #e9a23b; }",
            "body { margin: 0; background: radial-gradient(circle at top right, #d9f3f0 0, transparent 32%), linear-gradient(135deg, #f7f9fc 0%, #eef4f7 100%); color: #172033; }",
            ".page { max-width: 1100px; margin: 0 auto; padding: 32px 20px 48px; }",
            ".hero { padding: 28px 32px; border-radius: 16px; background: linear-gradient(120deg, #16324f 0%, #087f8c 100%); color: white; box-shadow: 0 12px 24px rgba(8, 127, 140, .18); }",
            ".hero h1 { margin: 0 0 12px; font-size: 30px; }",
            ".metadata { display: flex; flex-wrap: wrap; gap: 20px; color: #c7d8e8; }",
            ".summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 22px 0; }",
            ".metric, .test { background: rgba(255, 255, 255, .94); border: 1px solid #dce4ed; border-radius: 12px; box-shadow: 0 4px 14px rgba(22, 50, 79, .08); }",
            ".metric { padding: 18px; }",
            ".metric:nth-child(1) { border-top: 4px solid var(--teal); }",
            ".metric:nth-child(2) { border-top: 4px solid #25a55f; }",
            ".metric:nth-child(3) { border-top: 4px solid var(--coral); }",
            ".metric:nth-child(4) { border-top: 4px solid var(--gold); }",
            ".metric-label { color: #5e6c7e; font-size: 13px; text-transform: uppercase; letter-spacing: .06em; }",
            ".metric-value { margin-top: 6px; font-size: 28px; font-weight: 700; }",
            ".status { display: inline-block; padding: 5px 10px; border-radius: 999px; font-size: 13px; font-weight: 700; }",
            ".pass { color: #166534; background: #dcfce7; }",
            ".fail { color: #b91c1c; background: #fee2e2; }",
            ".error { color: #475569; background: #e2e8f0; }",
            ".test-list { display: grid; gap: 16px; }",
            ".test { padding: 22px; }",
            ".test-result-pass { border-left: 5px solid #25a55f; }",
            ".test-result-fail { border-left: 5px solid #fca5a5; }",
            ".test-result-error { border-left: 5px solid #cbd5e1; }",
            ".test-header { display: flex; justify-content: space-between; gap: 16px; align-items: center; border-bottom: 1px solid #e7edf3; padding-bottom: 14px; }",
            ".test h3 { margin: 0; font-size: 19px; }",
            ".label { color: #5e6c7e; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; }",
            ".detail { margin: 16px 0 0; line-height: 1.5; }",
            ".evidence { margin-top: 18px; padding: 14px; border-radius: 8px; background: #edf8f7; border: 1px solid #ccebe7; }",
            ".evidence-row { display: grid; grid-template-columns: minmax(120px, 220px) 1fr; gap: 12px; padding: 7px 0; border-bottom: 1px solid #cfe5e4; }",
            ".evidence-row:last-child { border-bottom: 0; }",
            "code { overflow-wrap: anywhere; color: #263b55; }",
            "@media (max-width: 700px) { .summary { grid-template-columns: repeat(2, 1fr); } .hero { padding: 22px; } .test-header { align-items: flex-start; flex-direction: column; } .evidence-row { grid-template-columns: 1fr; gap: 2px; } }",
            "</style>",
            "</head>",
            "<body>",
            '<main class="page">',
            '<section class="hero">',
            "<h1>TestEvidence AI - Test Execution Report</h1>",
            '<div class="metadata">',
            f"<span><strong>Execution time:</strong> {escape(execution_time)}</span>",
            f"<span><strong>Story ID:</strong> {escape(str(story_id or 'N/A'))}</span>",
            f'<span class="status {overall_class}">Overall: {escape(overall_status)}</span>',
            "</div>",
            "</section>",
            '<section class="summary" aria-label="Execution summary">',
            f'<div class="metric"><div class="metric-label">Total tests</div><div class="metric-value">{total_tests}</div></div>',
            f'<div class="metric"><div class="metric-label">Passed</div><div class="metric-value pass">{passed}</div></div>',
            f'<div class="metric"><div class="metric-label">Failed</div><div class="metric-value fail">{failed}</div></div>',
            f'<div class="metric"><div class="metric-label">Errors</div><div class="metric-value error">{errors}</div></div>',
            "</section>",
            "<h2>Test Results</h2>",
            '<section class="test-list">',
        ]

        for result in results:
            status = str(result.get("Status", "N/A"))
            status_class = status.lower() if status.lower() in {"pass", "fail", "error"} else "error"
            report.extend([
                f'<article class="test test-result-{status_class}">',
                '<div class="test-header">',
                f"<h3>{escape(str(result.get('TestCaseID', 'N/A')))}</h3>",
                f'<span class="status {status_class}">{escape(status)}</span>',
                "</div>",
                f'<div class="detail"><span class="label">Description</span><br>{escape(str(result.get("Description", "N/A")))}</div>',
                f'<div class="detail"><span class="label">Validation</span><br>{escape(str(result.get("Category", "N/A")))} &rarr; {escape(str(result.get("ValidationType", "N/A")))}</div>',
                f'<div class="detail"><span class="label">Result</span><br>{escape(str(result.get("Message", "N/A")))}</div>',
                '<div class="evidence"><div class="label">Evidence</div>',
            ])

            evidence = result.get("Evidence", {})
            if evidence:
                for key, value in evidence.items():
                    report.append(
                        f'<div class="evidence-row"><strong>{escape(str(key))}</strong>'
                        f"<code>{escape(str(value))}</code></div>"
                    )
            else:
                report.append("<p>No evidence available.</p>")

            report.extend(["</div>", "</article>"])

        report.extend(["</section>", "</main>", "</body>", "</html>"])
        return "\n".join(report)

    @staticmethod
    def save_report(report, name, timestamp):
        report_file_name = f"test_report_{name}_{timestamp}.html"

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
