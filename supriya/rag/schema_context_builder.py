class SchemaContextBuilder:

    def build_context(self, schemas):
        if not schemas:
            return "No relevant database schemas were resolved."

        context_parts = []

        for table, columns in schemas.items():
            column_lines = []

            for column in columns:
                column_lines.append(
                    f'- {column["ColumnName"]} ({column["DataType"]})'
                )

            context_parts.append(
                f"""Table: {table}
Columns:
{chr(10).join(column_lines)}"""
            )

        return "\n\n".join(context_parts)