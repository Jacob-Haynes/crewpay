from typing import Optional, Union

from pydantic import BaseModel


class CPRegistrationNumber(BaseModel):
    nino: Optional[str] = None
    passport_number: Optional[str] = None


class CPAddress(BaseModel):
    name: Optional[str]
    street: str
    number: str
    addition: Optional[str]
    zip_code: str
    city: str
    country: Optional[str]


class CPBankAccount(BaseModel):
    account_number: str
    sort_code: str


class CPCustomFieldList(BaseModel):
    id: int
    name: str


class CPCustomField(BaseModel):
    payroll_employee_statement: CPCustomFieldList
    payroll_student_loan_plan: CPCustomFieldList
    payroll_postgrad_loan: CPCustomFieldList
    payroll_start_date: Optional[str] = None


class CPEmployee(BaseModel):
    id: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    email: str
    profile_picture_url: Optional[str] = None
    status: str
    civil_status: Union[str, None]
    gender: str
    date_of_birth: str
    registration_numbers: CPRegistrationNumber
    address: CPAddress
    created_at: str
    bank_account: CPBankAccount
    custom_fields: CPCustomField
