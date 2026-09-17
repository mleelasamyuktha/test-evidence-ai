import csv
import io
import time

from utilitycode.azure_blob import AzureBlobClient
from utilitycode.azure_sql import AzureSQLClient
from utilitycode.logger import get_logger


logger = get_logger(__name__)


class IngestionPipeline:

    PIPELINE_NAME = "CustomerDataIngestion"

    def __init__(self):
        self.blob_client = AzureBlobClient()
        self.sql_client = AzureSQLClient()

    def ingest_csv_to_table(self, source_file="SourceFolder/customer_data.csv", target_table="dbo.customer_data"):

        start_time = time.perf_counter()

        logger.info(
            "Starting ingestion | source_file=%s | target_table=%s",
            source_file,
            target_table
        )

        try:
            csv_data = self.blob_client.download_blob(source_file).decode("utf-8-sig")

            reader = csv.DictReader(io.StringIO(csv_data))
            rows = list(reader)

            if not rows:
                duration = time.perf_counter() - start_time

                return {
                    "Status": "PASS",
                    "Message": "Source file contains no data",
                    "RowsInserted": 0,
                    "Duration": duration
                }

            columns = reader.fieldnames

            if not columns:
                raise ValueError("CSV does not contain headers")

            column_names = ", ".join(f"[{column}]" for column in columns)
            placeholders = ", ".join("?" for _ in columns)

            query = f"""
                INSERT INTO {target_table} ({column_names})
                VALUES ({placeholders})
            """

            cursor = self.sql_client.connection.cursor()

            for row in rows:
                values = [
                    value if value != "" else None
                    for value in row.values()
                ]

                cursor.execute(query, values)

            self.sql_client.connection.commit()
            time.sleep(40)  # Wait for 40 seconds to ensure data is committed

            duration = time.perf_counter() - start_time

            logger.info(
                "Ingestion completed | rows_inserted=%s | duration=%.3f seconds",
                len(rows),
                duration
            )

            return {
                "Status": "PASS",
                "Message": "CSV data ingested successfully",
                "RowsInserted": len(rows),
                "TargetTable": target_table,
                "Duration": duration
            }

        except Exception:
            self.sql_client.connection.rollback()

            duration = time.perf_counter() - start_time

            logger.exception("Ingestion pipeline failed")

            return {
                "Status": "ERROR",
                "Message": "Error during CSV ingestion",
                "Duration": duration
            }

        finally:
            self.sql_client.close()