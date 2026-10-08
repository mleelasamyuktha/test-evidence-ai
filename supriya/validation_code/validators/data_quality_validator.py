from utilitycode.azure_sql import AzureSQLClient
from utilitycode.logger import get_logger


logger = get_logger(__name__)


class DataQualityValidator:

    @staticmethod
    def validate_query_assertion(validation_input):

        query = (
            validation_input.get("Query")
            or validation_input.get("SQL")
            or validation_input.get("Sql")
            or validation_input.get("SelectQuery")
            or validation_input.get("GeneratedQuery")
        )

        if query is None:
            return {
                "Status": "ERROR",
                "Message": "Missing required validation input: Query/SQL",
                "Evidence": {}
            }

        query = str(query).strip()
        expected = validation_input.get("Expected")
        operator = validation_input.get("Operator", "==")

        logger.info(
            "Executing data quality query | query=%s",
            query
        )

        normalized = " ".join(query.strip().split())
        if not normalized.lower().startswith("select"):
            return {
                "Status": "ERROR",
                "Message": "Only SELECT queries are allowed",
                "Evidence": {
                    "Query": query
                }
            }

        client = AzureSQLClient()

        try:
            rows = client.execute_query(query)

            if not rows:
                return {
                    "Status": "FAIL",
                    "Message": "Query returned no results",
                    "Evidence": {
                        "Query": query
                    }
                }

            actual = rows[0][0]

            if expected is None:
                logger.info(
                    "Query executed successfully | actual=%s",
                    actual
                )

                return {
                    "Status": "PASS",
                    "Message": "Query executed successfully",
                    "Evidence": {
                        "Query": query,
                        "Actual": actual
                    }
                }

            if operator in ("=", "=="):
                passed = actual == expected
            elif operator == "!=":
                passed = actual != expected
            elif operator == ">":
                passed = actual > expected
            elif operator == ">=":
                passed = actual >= expected
            elif operator == "<":
                passed = actual < expected
            elif operator == "<=":
                passed = actual <= expected
            else:
                return {
                    "Status": "ERROR",
                    "Message": f"Unsupported operator: {operator}",
                    "Evidence": {
                        "Query": query,
                        "Expected": expected,
                        "Actual": actual,
                        "Operator": operator
                    }
                }

            status = "PASS" if passed else "FAIL"

            logger.info(
                "Data quality validation completed | status=%s | actual=%s | expected=%s",
                status,
                actual,
                expected
            )

            return {
                "Status": status,
                "Message": (
                    f"Validation passed: {actual} {operator} {expected}"
                    if passed
                    else f"Validation failed: {actual} {operator} {expected}"
                ),
                "Evidence": {
                    "Query": query,
                    "Expected": expected,
                    "Actual": actual,
                    "Operator": operator
                }
            }

        except Exception:
            logger.exception("Data quality validation failed")

            return {
                "Status": "ERROR",
                "Message": "Error executing data quality query",
                "Evidence": {
                    "Query": query
                }
            }

        finally:
            client.close()

