from typing import List, Optional

from pydantic import BaseModel, Field, root_validator


class CustomFields(BaseModel):
    open_field: Optional[str]
    single_option: Optional[dict]
    multiple_options: Optional[List[dict]]


class Address(BaseModel):
    id: int
    name: Optional[str]
    street: Optional[str]
    number: Optional[str]
    zip_code: str
    city: Optional[str]
    country: Optional[str]
    lat: Optional[str]
    lng: Optional[str]


class Company(BaseModel):
    id: int
    name: str
    vat_number: Optional[str]
    custom_fields: Optional[CustomFields]
    address: Optional[Address]


class Department(BaseModel):
    id: int
    group: Optional[dict]
    name: Optional[str]
    full_name: Optional[str]
    custom_fields: Optional[dict]


class Function(BaseModel):
    id: int
    name: str


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    date_of_birth: str
    employee_number: Optional[str]
    nino: Optional[str]
    bank_account: Optional[dict]
    civil_status: Optional[dict]
    custom_fields: Optional[dict]


class Worker(BaseModel):
    id: int
    name: str
    phone_number: Optional[str]
    contract_type: str
    user: User


class Slot(BaseModel):
    id: int
    department: Department
    function: Function


class Planned(BaseModel):
    start: str
    end: str
    minutes: int


class Clocked(BaseModel):
    start: str
    end: str
    minutes: int


class Registered(BaseModel):
    start: str
    end: str
    gross_minutes: int
    break_: Optional[int] = Field(alias="break")
    netto_minutes: int


class Timesheet(BaseModel):
    planned: Planned
    clocked: Optional[Clocked]
    registered: Registered


class Wage(BaseModel):
    type_: str = Field(alias="type")
    value: float
    day_rate_max_hours: Optional[int]
    total: float


class Cost(BaseModel):
    type_: Optional[str] = Field(alias="type")
    value: Optional[float]
    day_rate_max_hours: Optional[int]
    total: Optional[float]


class Payout(BaseModel):
    estimated_earnings: Optional[float]
    advance: Optional[float]


class Project(BaseModel):
    id: int
    name: str
    date: str
    company: Company


class CPShift(BaseModel):
    id: int
    project: Project
    slot: Slot
    present: bool
    worker: Worker
    timesheet: Timesheet
    wage: Optional[Wage]
    cost: Optional[Cost]
    payout: Optional[Payout]


class Totals(BaseModel):
    workers: Optional[int]
    projects: Optional[int]
    slots: Optional[int]
    companies: Optional[int]
    days: Optional[int]
    hours: Optional[float]
    travel_distance: Optional[float]


class CPReportMeta(BaseModel):
    totals: Totals
