import csv
import io

from utilitycode.azure_blob import AzureBlobClient
from utilitycode.azure_sql import AzureSQLClient
from utilitycode.logger import get_logger


logger = get_logger(__name__)


class ReconciliationValidator:

    @staticmethod
    def validate_query_comparison(validation_input):

        source_query = validation_input.get("SourceQuery")
        source_file = validation_input.get("SourceFile")
        target_query = validation_input["TargetQuery"]
        comparison_keys = validation_input["ComparisonKeys"]
        comparisons = validation_input.get("Comparisons", [])

        if not source_query and not source_file:
            return {
                "Status": "ERROR",
                "Message": "Either SourceQuery or SourceFile must be provided"
            }

        if source_query and source_file:
            return {
                "Status": "ERROR",
                "Message": "Provide either SourceQuery or SourceFile, not both"
            }

        blob_client = AzureBlobClient() if source_file else None
        sql_client = AzureSQLClient()

        try:

            if source_file:

                logger.info(
                    "Reading reconciliation source file | file=%s",
                    source_file
                )

                csv_data = blob_client.download_blob(
                    source_file
                ).decode("utf-8-sig")

                reader = csv.DictReader(io.StringIO(csv_data))
                source_data = list(reader)

                logger.info(
                    "Source CSV read successfully | rows=%s",
                    len(source_data)
                )

            else:

                logger.info("Executing source query")

                source_cursor = sql_client.connection.cursor()
                source_cursor.execute(source_query)

                source_rows = source_cursor.fetchall()

                source_columns = [
                    column[0]
                    for column in source_cursor.description
                ]

                source_data = [
                    dict(zip(source_columns, row))
                    for row in source_rows
                ]

                logger.info(
                    "Source query executed successfully | rows=%s",
                    len(source_data)
                )

            logger.info("Executing target query")

            target_cursor = sql_client.connection.cursor()
            target_cursor.execute(target_query)

            target_rows = target_cursor.fetchall()

            target_columns = [
                column[0]
                for column in target_cursor.description
            ]

            target_data = [
                dict(zip(target_columns, row))
                for row in target_rows
            ]

            logger.info(
                "Target query executed successfully | rows=%s",
                len(target_data)
            )

            source_map = {
                tuple(
                    ReconciliationValidator._normalize_value(
                        row.get(key)
                    )
                    for key in comparison_keys
                ): row
                for row in source_data
            }

            target_map = {
                tuple(
                    ReconciliationValidator._normalize_value(
                        row.get(key)
                    )
                    for key in comparison_keys
                ): row
                for row in target_data
            }

            missing_in_target = [
                key
                for key in source_map
                if key not in target_map
            ]

            missing_in_source = [
                key
                for key in target_map
                if key not in source_map
            ]

            mismatches = []

            common_keys = source_map.keys() & target_map.keys()

            for key in common_keys:

                source_row = source_map[key]
                target_row = target_map[key]

                if comparisons:

                    for comparison in comparisons:

                        column = comparison["Column"]
                        operator = comparison.get("Operator", "==")

                        source_value = source_row.get(column)
                        target_value = target_row.get(column)

                        if not ReconciliationValidator._compare_values(
                            source_value,
                            target_value,
                            operator
                        ):
                            mismatches.append({
                                "Key": key,
                                "Column": column,
                                "SourceValue": source_value,
                                "TargetValue": target_value,
                                "Operator": operator
                            })

                else:

                    if source_row != target_row:
                        mismatches.append({
                            "Key": key,
                            "SourceRow": source_row,
                            "TargetRow": target_row
                        })

            passed = (
                not missing_in_target
                and not missing_in_source
                and not mismatches
            )

            status = "PASS" if passed else "FAIL"

            return {
                "Status": status,
                "Message": (
                    "Source and target data match"
                    if passed
                    else "Source and target data do not match"
                ),
                "Evidence": {
                    "SourceQuery": source_query,
                    "SourceFile": source_file,
                    "TargetQuery": target_query,
                    "ComparisonKeys": comparison_keys,
                    "SourceRowCount": len(source_data),
                    "TargetRowCount": len(target_data),
                    "MissingInTarget": missing_in_target,
                    "MissingInSource": missing_in_source,
                    "Mismatches": mismatches
                }
            }

        except Exception:
            logger.exception("Reconciliation validation failed")

            return {
                "Status": "ERROR",
                "Message": "Error during reconciliation validation",
                "Evidence": {
                    "SourceQuery": source_query,
                    "SourceFile": source_file,
                    "TargetQuery": target_query,
                    "ComparisonKeys": comparison_keys
                }
            }

        finally:
            sql_client.close()

    @staticmethod
    def _normalize_value(value):

        if value is None:
            return None

        value = str(value).strip()

        if value == "":
            return None

        return value

    @staticmethod
    def _compare_values(source_value, target_value, operator):

        source_value = ReconciliationValidator._normalize_value(
            source_value
        )

        target_value = ReconciliationValidator._normalize_value(
            target_value
        )

        if operator == "==":
            return source_value == target_value

        if operator == "!=":
            return source_value != target_value

        if operator == ">":
            return target_value > source_value

        if operator == ">=":
            return target_value >= source_value

        if operator == "<":
            return target_value < source_value

        if operator == "<=":
            return target_value <= source_value

        raise ValueError(
            f"Unsupported comparison operator: {operator}"
        )