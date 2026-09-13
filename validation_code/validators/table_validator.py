from utilitycode.azure_sql import AzureSQLClient
from utilitycode.logger import get_logger


logger = get_logger(__name__)


class TableValidator:

    @staticmethod
    def validate_exists(validation_input):

        logger.info("Starting table existence validation")

        try:
            table_name = validation_input["TableName"]

            logger.info(
                "Table existence validation input | table=%s",
                table_name
            )

            sql_client = AzureSQLClient()

            query = """
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = ?
                AND TABLE_NAME = ?
            """

            if "." in table_name:
                schema_name, table_name_only = table_name.split(".", 1)
            else:
                schema_name = "dbo"
                table_name_only = table_name

            result = sql_client.execute_query(
                query,
                (schema_name, table_name_only)
            )

            sql_client.close()

            table_exists = result[0][0] > 0

            logger.info(
                "Table existence result | table=%s | exists=%s",
                table_name,
                table_exists
            )

            if table_exists:
                return {
                    "Status": "PASS",
                    "Message": "Table exists",
                    "Evidence": {
                        "TableName": table_name,
                        "TableExists": True
                    }
                }

            return {
                "Status": "FAIL",
                "Message": "Table does not exist",
                "Evidence": {
                    "TableName": table_name,
                    "TableExists": False
                }
            }

        except KeyError as e:

            logger.error(
                "Table existence validation failed | missing input=%s",
                e
            )

            return {
                "Status": "ERROR",
                "Message": f"Missing required validation input: {e}",
                "Evidence": {}
            }

        except Exception as e:

            logger.exception(
                "Unexpected error during table existence validation"
            )

            return {
                "Status": "ERROR",
                "Message": f"Unexpected error during table existence validation: {e}",
                "Evidence": {}
            }

    @staticmethod
    def validate_count(validation_input):

        logger.info("Starting table count validation")

        try:
            table_name = validation_input["TableName"]

            logger.info(
                "Table count validation input | table=%s",
                table_name
            )

            query = f"SELECT COUNT(*) FROM {table_name}"

            logger.info(
                "Executing table count query | query=%s",
                query
            )

            sql_client = AzureSQLClient()

            result = sql_client.execute_query(query)

            sql_client.close()

            actual_count = result[0][0]

            logger.info(
                "Actual table record count | table=%s | count=%s",
                table_name,
                actual_count
            )

            if "ExpectedCount" not in validation_input:

                logger.info(
                    "Expected count not supplied | returning actual count"
                )

                return {
                    "Status": "PASS",
                    "Message": "Table record count successfully calculated",
                    "Evidence": {
                        "TableName": table_name,
                        "ActualCount": actual_count
                    }
                }

            expected_count = validation_input["ExpectedCount"]

            count_match = actual_count == expected_count

            logger.info(
                "Table count comparison | expected=%s | actual=%s | match=%s",
                expected_count,
                actual_count,
                count_match
            )

            if count_match:

                return {
                    "Status": "PASS",
                    "Message": "Table record count matches expected count",
                    "Evidence": {
                        "TableName": table_name,
                        "ExpectedCount": expected_count,
                        "ActualCount": actual_count,
                        "CountMatch": True
                    }
                }

            return {
                "Status": "FAIL",
                "Message": "Table record count does not match expected count",
                "Evidence": {
                    "TableName": table_name,
                    "ExpectedCount": expected_count,
                    "ActualCount": actual_count,
                    "CountMatch": False
                }
            }

        except KeyError as e:

            logger.error(
                "Table count validation failed | missing input=%s",
                e
            )

            return {
                "Status": "ERROR",
                "Message": f"Missing required validation input: {e}",
                "Evidence": {}
            }

        except Exception as e:

            logger.exception(
                "Unexpected error during table count validation"
            )

            return {
                "Status": "ERROR",
                "Message": f"Unexpected error during table count validation: {e}",
                "Evidence": {}
            }

    @staticmethod
    def validate_schema(validation_input):

        logger.info("Starting table schema validation")

        try:
            table_name = validation_input["TableName"]

            if "." in table_name:
                schema_name, table_name_only = table_name.split(".", 1)
            else:
                schema_name = "dbo"
                table_name_only = table_name

            query = """
                SELECT
                    COLUMN_NAME,
                    DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = ?
                AND TABLE_NAME = ?
                ORDER BY ORDINAL_POSITION
            """

            sql_client = AzureSQLClient()

            result = sql_client.execute_query(
                query,
                (schema_name, table_name_only)
            )

            sql_client.close()

            actual_schema = [
                {
                    "ColumnName": row[0],
                    "DataType": row[1]
                }
                for row in result
            ]

            logger.info(
                "Actual table schema retrieved | table=%s | columns=%s",
                table_name,
                len(actual_schema)
            )

            if not actual_schema:

                return {
                    "Status": "FAIL",
                    "Message": "Table does not exist or contains no columns",
                    "Evidence": {
                        "TableName": table_name,
                        "ActualSchema": actual_schema
                    }
                }

            if "ExpectedSchema" not in validation_input:

                return {
                    "Status": "PASS",
                    "Message": "Table schema successfully retrieved",
                    "Evidence": {
                        "TableName": table_name,
                        "ActualSchema": actual_schema
                    }
                }

            expected_schema = validation_input["ExpectedSchema"]

            schema_match = actual_schema == expected_schema

            logger.info(
                "Schema comparison | table=%s | match=%s",
                table_name,
                schema_match
            )

            if schema_match:

                return {
                    "Status": "PASS",
                    "Message": "Table schema matches expected schema",
                    "Evidence": {
                        "TableName": table_name,
                        "ExpectedSchema": expected_schema,
                        "ActualSchema": actual_schema,
                        "SchemaMatch": True
                    }
                }

            return {
                "Status": "FAIL",
                "Message": "Table schema does not match expected schema",
                "Evidence": {
                    "TableName": table_name,
                    "ExpectedSchema": expected_schema,
                    "ActualSchema": actual_schema,
                    "SchemaMatch": False
                }
            }

        except KeyError as e:

            logger.error(
                "Table schema validation failed | missing input=%s",
                e
            )

            return {
                "Status": "ERROR",
                "Message": f"Missing required validation input: {e}",
                "Evidence": {}
            }

        except Exception as e:

            logger.exception(
                "Unexpected error during table schema validation"
            )

            return {
                "Status": "ERROR",
                "Message": f"Unexpected error during table schema validation: {e}",
                "Evidence": {}
            }

    @staticmethod
    def validate_null(validation_input):

        logger.info("Starting table null validation")

        try:
            table_name = validation_input["TableName"]
            column_names = validation_input["ColumnNames"]

            sql_client = AzureSQLClient()

            evidence = {}
            overall_status = "PASS"

            for column_name in column_names:

                query = f"""
                    SELECT COUNT(*)
                    FROM {table_name}
                    WHERE {column_name} IS NULL
                """

                result = sql_client.execute_query(query)

                null_count = result[0][0]

                logger.info(
                    "NULL count retrieved | table=%s | column=%s | count=%s",
                    table_name,
                    column_name,
                    null_count
                )

                status = "PASS" if null_count == 0 else "FAIL"

                if status == "FAIL":
                    overall_status = "FAIL"

                evidence[column_name] = {
                    "NullCount": null_count,
                    "Status": status
                }

            sql_client.close()

            if overall_status == "PASS":

                return {
                    "Status": "PASS",
                    "Message": "All specified columns contain no NULL values",
                    "Evidence": {
                        "TableName": table_name,
                        "Columns": evidence
                    }
                }

            return {
                "Status": "FAIL",
                "Message": "One or more specified columns contain NULL values",
                "Evidence": {
                    "TableName": table_name,
                    "Columns": evidence
                }
            }

        except KeyError as e:

            logger.error(
                "Table null validation failed | missing input=%s",
                e
            )

            return {
                "Status": "ERROR",
                "Message": f"Missing required validation input: {e}",
                "Evidence": {}
            }

        except Exception as e:

            logger.exception(
                "Unexpected error during table null validation"
            )

            return {
                "Status": "ERROR",
                "Message": f"Unexpected error during table null validation: {e}",
                "Evidence": {}
            }

    @staticmethod
    def validate_duplicate(validation_input):

        logger.info("Starting table duplicate validation")

        try:
            table_name = validation_input["TableName"]
            column_names = validation_input["ColumnNames"]

            if not column_names:

                return {
                    "Status": "ERROR",
                    "Message": "At least one column must be provided",
                    "Evidence": {}
                }

            columns = ", ".join(column_names)

            query = f"""
                SELECT COUNT(*)
                FROM (
                    SELECT {columns}
                    FROM {table_name}
                    GROUP BY {columns}
                    HAVING COUNT(*) > 1
                ) AS duplicate_groups
            """

            sql_client = AzureSQLClient()

            result = sql_client.execute_query(query)

            sql_client.close()

            actual_duplicate_count = result[0][0]

            logger.info(
                "Duplicate groups retrieved | table=%s | columns=%s | count=%s",
                table_name,
                columns,
                actual_duplicate_count
            )

            if "ExpectedDuplicateCount" not in validation_input:

                logger.info(
                    "Expected duplicate count not supplied | returning actual count"
                )

                return {
                    "Status": "PASS",
                    "Message": "Duplicate record count successfully calculated",
                    "Evidence": {
                        "TableName": table_name,
                        "ColumnNames": column_names,
                        "ActualDuplicateCount": actual_duplicate_count
                    }
                }

            expected_duplicate_count = validation_input["ExpectedDuplicateCount"]

            duplicate_match = actual_duplicate_count == expected_duplicate_count

            logger.info(
                "Duplicate count comparison | expected=%s | actual=%s | match=%s",
                expected_duplicate_count,
                actual_duplicate_count,
                duplicate_match
            )

            if duplicate_match:

                return {
                    "Status": "PASS",
                    "Message": "Duplicate record count matches expected count",
                    "Evidence": {
                        "TableName": table_name,
                        "ColumnNames": column_names,
                        "ExpectedDuplicateCount": expected_duplicate_count,
                        "ActualDuplicateCount": actual_duplicate_count,
                        "DuplicateCountMatch": True
                    }
                }

            return {
                "Status": "FAIL",
                "Message": "Duplicate record count does not match expected count",
                "Evidence": {
                    "TableName": table_name,
                    "ColumnNames": column_names,
                    "ExpectedDuplicateCount": expected_duplicate_count,
                    "ActualDuplicateCount": actual_duplicate_count,
                    "DuplicateCountMatch": False
                }
            }

        except KeyError as e:

            logger.error(
                "Table duplicate validation failed | missing input=%s",
                e
            )

            return {
                "Status": "ERROR",
                "Message": f"Missing required validation input: {e}",
                "Evidence": {}
            }

        except Exception as e:

            logger.exception(
                "Unexpected error during table duplicate validation"
            )

            return {
                "Status": "ERROR",
                "Message": f"Unexpected error during table duplicate validation: {e}",
                "Evidence": {}
            }