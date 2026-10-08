from datetime import date
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    customer_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    region: str = Field(min_length=1, max_length=100)
    created_on: date


class CustomerCreate(CustomerBase):
    customer_id: int = Field(gt=0)


class CustomerUpdate(BaseModel):
    customer_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    region: Optional[str] = Field(default=None, min_length=1, max_length=100)
    created_on: Optional[date] = None


class Customer(CustomerCreate):
    model_config = ConfigDict(from_attributes=True)


class CustomerResponse(BaseModel):
    customer_id: int
    customer_name: str
    email: Optional[EmailStr] = None
    region: str
    created_on: date


class CustomerSummary(BaseModel):
    total_customers: int
    customers_by_region: Dict[str, int]