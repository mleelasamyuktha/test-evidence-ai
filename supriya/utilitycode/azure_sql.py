import os

from dotenv import load_dotenv

try:
    import pyodbc
except ImportError:  # pragma: no cover - depends on native ODBC installation
    pyodbc = None


load_dotenv()


class AzureSQLClient:

    def __init__(self):
        if pyodbc is None:
            raise ImportError(
                "pyodbc is required for Azure SQL access. Install unixODBC and the Microsoft ODBC driver for SQL Server."
            )

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

    def commit(self):
        self.connection.commit()

    def execute_non_query(self, query, parameters=None):
        cursor = self.connection.cursor()
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        return cursor.rowcount

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

    def get_all_table_schemas(self):
        tables = self.get_tables()

        schemas = {}

        for table in tables:
            schema_name, table_name = table.split(".", 1)
            schemas[table] = self.get_table_schema(table_name, schema_name)

        return schemas

    def get_tables(self):
        query = """
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
        """

        cursor = self.connection.cursor()
        cursor.execute(query)

        return [
            f"{row[0]}.{row[1]}"
            for row in cursor.fetchall()
        ]

    def close(self):

        self.connection.close()