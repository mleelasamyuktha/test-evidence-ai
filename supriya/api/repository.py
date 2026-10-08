from datetime import date
from typing import Any, Optional

from utilitycode.azure_sql import AzureSQLClient


CUSTOMER_COLUMNS = (
    "customer_id, first_name, last_name, email, state, created_date"
)


def _customer_from_row(row) -> dict[str, Any]:
    return {
        "customer_id": row[0],
        "customer_name": " ".join(part for part in (row[1], row[2]) if part).strip(),
        "email": row[3],
        "region": row[4],
        "created_on": row[5],
    }


def _split_customer_name(customer_name: str) -> tuple[str, str]:
    parts = customer_name.strip().split(None, 1)
    return parts[0], parts[1] if len(parts) == 2 else ""


class CustomerRepository:
    def __init__(self):
        self.client = AzureSQLClient()

    def close(self):
        self.client.close()

    def list_customers(self, region: Optional[str] = None) -> list[dict[str, Any]]:
        query = f"SELECT {CUSTOMER_COLUMNS} FROM dbo.Customers"
        parameters = None
        if region:
            query += " WHERE state = ?"
            parameters = (region,)
        query += " ORDER BY customer_id"
        return [_customer_from_row(row) for row in self.client.execute_query(query, parameters)]

    def get_customer(self, customer_id: int) -> Optional[dict[str, Any]]:
        query = f"SELECT {CUSTOMER_COLUMNS} FROM dbo.Customers WHERE customer_id = ?"
        rows = self.client.execute_query(query, (customer_id,))
        return _customer_from_row(rows[0]) if rows else None

    def create_customer(self, customer: dict[str, Any]) -> dict[str, Any]:
        first_name, last_name = _split_customer_name(customer["customer_name"])
        query = """
            INSERT INTO dbo.Customers
                  (customer_id, first_name, last_name, email, state, created_date)
            OUTPUT INSERTED.customer_id, INSERTED.first_name, INSERTED.last_name,
                   INSERTED.email, INSERTED.state, INSERTED.created_date
                 VALUES (?, ?, ?, ?, ?)
        """
        values = (
            customer["customer_id"], first_name, last_name, customer["email"],
            customer["region"], customer["created_on"],
        )
        result = _customer_from_row(self.client.execute_query(query, values)[0])
        self.client.commit()
        return result

    def update_customer(self, customer_id: int, changes: dict[str, Any]) -> Optional[dict[str, Any]]:
        if not changes:
            return self.get_customer(customer_id)

        updates = []
        if "customer_name" in changes:
            first_name, last_name = _split_customer_name(changes["customer_name"])
            updates.extend([("first_name", first_name), ("last_name", last_name)])
        if "email" in changes:
            updates.append(("email", changes["email"]))
        if "region" in changes:
            updates.append(("state", changes["region"]))
        if "created_on" in changes:
            updates.append(("created_date", changes["created_on"]))
        assignments = ", ".join(f"{key} = ?" for key, _ in updates)
        values = [value for _, value in updates] + [customer_id]
        query = f"""
            UPDATE dbo.Customers
            SET {assignments}
            OUTPUT INSERTED.customer_id, INSERTED.first_name, INSERTED.last_name,
                   INSERTED.email, INSERTED.state, INSERTED.created_date
            WHERE customer_id = ?
        """
        rows = self.client.execute_query(query, values)
        self.client.commit()
        return _customer_from_row(rows[0]) if rows else None

    def delete_customer(self, customer_id: int) -> bool:
        query = "DELETE FROM dbo.Customers WHERE customer_id = ?"
        self.client.execute_non_query(query, (customer_id,))
        self.client.commit()
        return self.get_customer(customer_id) is None

    def summary(self) -> dict[str, Any]:
        count_rows = self.client.execute_query("SELECT COUNT(*) FROM dbo.Customers")
        region_rows = self.client.execute_query(
            "SELECT state, COUNT(*) FROM dbo.Customers GROUP BY state ORDER BY state"
        )
        return {
            "total_customers": count_rows[0][0],
            "customers_by_region": {row[0]: row[1] for row in region_rows},
        }