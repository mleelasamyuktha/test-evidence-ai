from utilitycode.azure_sql import AzureSQLClient


class SchemaResolver:

    def __init__(self):
        self.sql_client = AzureSQLClient()

    def resolve_schemas(self, resolved_tables):
        schemas = {}

        for entity, table in resolved_tables.items():
            schema_name, table_name = table.split(".", 1)

            schemas[table] = self.sql_client.get_table_schema(
                table_name,
                schema_name
            )

        return schemas