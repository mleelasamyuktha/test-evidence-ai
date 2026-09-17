import os

import pyodbc


class AzureSQLClient:

    def __init__(self):

        server = os.environ["AZURE_SQL_SERVER"]
        database = os.environ["AZURE_SQL_DATABASE"]
        username = os.environ["AZURE_SQL_USERNAME"]
        password = os.environ["AZURE_SQL_PASSWORD"]

        connection_string = (
            "Driver={ODBC Driver 18 for SQL Server};"
            f"Server=tcp:{server},1433;"
            f"Database={database};"
            f"Uid={username};"
            f"Pwd={password};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )

        self.connection = pyodbc.connect(connection_string)

    def execute_query(self, query, parameters=None):

        cursor = self.connection.cursor()

        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)

        return cursor.fetchall()

    def get_table_schema(self, table_name, schema_name="dbo"):

        query = """
            SELECT
                COLUMN_NAME,
                DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = ?
            AND TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """

        rows = self.execute_query(query, (schema_name, table_name))

        return [
            {
                "ColumnName": row[0],
                "DataType": row[1]
            }
            for row in rows
        ]

    def close(self):

        self.connection.close()