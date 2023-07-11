from pydantic import BaseModel, Field


class CustomFields(BaseModel):
    open_field: str | None
    single_option: dict | None
    multiple_options: list[dict] | None


class Address(BaseModel):
    id: int
    name: str | None
    street: str | None
    number: str | None
    zip_code: str
    city: str | None
    country: str | None
    lat: str | None
    lng: str | None


class Company(BaseModel):
    id: int
    name: str
    vat_number: str | None
    custom_fields: CustomFields | None
    address: Address | None


class Department(BaseModel):
    id: int
    group: dict | None
    name: str | None
    full_name: str | None
    custom_fields: dict | None


class Function(BaseModel):
    id: int
    name: str


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    date_of_birth: str
    employee_number: dict | None
    nino: dict | None
    bank_account: dict | None
    civil_status: dict | None
    custom_fields: dict | None


class Worker(BaseModel):
    id: int
    name: str
    phone_number: str | None
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
    break_: int | None = Field(alias="break")
    netto_minutes: int


class Timesheet(BaseModel):
    planned: Planned
    clocked: Clocked | None
    registered: Registered


class Wage(BaseModel):
    type_: str = Field(alias="type")
    value: float
    day_rate_max_hours: int | None
    total: float


class Cost(BaseModel):
    type_: str | None = Field(alias="type")
    value: float | None
    day_rate_max_hours: int | None
    total: float | None


class Payout(BaseModel):
    estimated_earnings: float | None
    advance: float | None


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
    wage: Wage | None
    cost: Cost | None
    payout: Payout | None


class Totals(BaseModel):
    workers: int | None
    projects: int | None
    slots: int | None
    companies: int | None
    days: int | None
    hours: float | None
    travel_distance: float | None


class CPReportMeta(BaseModel):
    totals: Totals
