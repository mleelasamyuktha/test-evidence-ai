# Customer API HLD and API Testing Requirements

## 1. Purpose

Expose customer data from Azure SQL table `dbo.Customers` through a documented HTTP API and validate the API behavior from uploaded HLD, API notes, Word documents, or acceptance criteria.

## 2. Scope

The first release provides customer CRUD operations, a health endpoint, and a reporting summary endpoint. The API does not require bearer-token authentication for the hackathon environment.

## 3. Data source

The API uses the existing Azure SQL database configured by the project environment. The target table is `dbo.Customers` with these logical fields:

- `customer_id`
- `customer_name`
- `email`
- `region`
- `created_on`

## 4. High-level design

```text
Client / Swagger / Streamlit
          |
          v
FastAPI Customer API :8000
          |
          v
CustomerRepository with parameterized SQL
          |
          v
Azure SQL dbo.Customers
```

## 5. Endpoint contract

| Method | Endpoint | Purpose | Success |
|---|---|---|---|
| GET | `/health` | Service health check | 200 |
| GET | `/api/v1/customers` | List all customers | 200 |
| GET | `/api/v1/customers?region=North` | Filter customers by region | 200 |
| GET | `/api/v1/customers/{customer_id}` | Get one customer | 200 |
| GET | `/api/v1/customers/summary` | Total and regional counts | 200 |
| POST | `/api/v1/customers` | Create a customer | 201 |
| PUT | `/api/v1/customers/{customer_id}` | Update a customer | 200 |
| DELETE | `/api/v1/customers/{customer_id}` | Delete a customer | 204 |

Swagger UI is available at `/docs`; OpenAPI JSON is available at `/openapi.json`.

## 6. API testing requirements

1. The test runner must accept `.docx` documents containing HLD, API notes, or acceptance criteria.
2. The LLM must generate API test cases from the document and the live OpenAPI contract.
3. Generated tests must include method, path, request body when applicable, expected status, and response assertions.
4. Baseline tests must cover health, list, get, filter, summary, validation errors, not-found behavior, duplicate creation, update, and delete.
5. Write tests must use unique IDs and delete created records during cleanup.
6. Tests must display generated cases before execution and show response status, response body, and assertion outcome after execution.
7. No bearer token should be added or required in the hackathon environment.

## 7. Non-functional requirements

- SQL values must be parameterized.
- API errors must return JSON with an appropriate HTTP status.
- The API must be runnable locally with `uvicorn api.main:app --reload --port 8000`.
- The service must not expose database credentials through the API or OpenAPI document.