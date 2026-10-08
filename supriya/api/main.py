from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response, status
from starlette.responses import RedirectResponse

from api.repository import CustomerRepository
from api.schemas import Customer, CustomerCreate, CustomerResponse, CustomerSummary, CustomerUpdate


app = FastAPI(
    title="TestEvidence Customer API",
    description="CRUD customer API backed by Azure SQL dbo.Customers. No bearer token is required for this hackathon service.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.get("/", tags=["System"])
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs", status_code=307)


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "customer-api"}


@app.get("/api/v1/customers/summary", response_model=CustomerSummary, tags=["Customers"])
def customer_summary() -> CustomerSummary:
    repository = CustomerRepository()
    try:
        return repository.summary()
    finally:
        repository.close()


@app.get("/api/v1/customers", response_model=list[CustomerResponse], tags=["Customers"])
def list_customers(region: Optional[str] = Query(default=None)) -> list[Customer]:
    repository = CustomerRepository()
    try:
        return repository.list_customers(region)
    finally:
        repository.close()


@app.get("/api/v1/customers/{customer_id}", response_model=CustomerResponse, tags=["Customers"])
def get_customer(customer_id: int) -> Customer:
    repository = CustomerRepository()
    try:
        customer = repository.get_customer(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    finally:
        repository.close()


@app.post("/api/v1/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED, tags=["Customers"])
def create_customer(customer: CustomerCreate) -> Customer:
    repository = CustomerRepository()
    try:
        if repository.get_customer(customer.customer_id):
            raise HTTPException(status_code=409, detail="Customer already exists")
        return repository.create_customer(customer.model_dump())
    finally:
        repository.close()


@app.put("/api/v1/customers/{customer_id}", response_model=CustomerResponse, tags=["Customers"])
def update_customer(customer_id: int, customer: CustomerUpdate) -> Customer:
    repository = CustomerRepository()
    try:
        if not repository.get_customer(customer_id):
            raise HTTPException(status_code=404, detail="Customer not found")
        updated = repository.update_customer(customer_id, customer.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Customer not found")
        return updated
    finally:
        repository.close()


@app.delete("/api/v1/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Customers"])
def delete_customer(customer_id: int) -> Response:
    repository = CustomerRepository()
    try:
        if not repository.get_customer(customer_id):
            raise HTTPException(status_code=404, detail="Customer not found")
        repository.delete_customer(customer_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    finally:
        repository.close()