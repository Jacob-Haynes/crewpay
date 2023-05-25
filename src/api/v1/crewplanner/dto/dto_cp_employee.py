from typing import Optional, Union

from pydantic import BaseModel, root_validator, Field


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
    type_: str = Field(alias="type")
    account_number: Optional[str] = None
    sort_code: Optional[str] = None
    iban: Optional[str] = None
    bic: Optional[str] = None

    @root_validator(allow_reuse=True)
    def validator_bank_type(cls, values):
        if values['type_'] == 'iban':
            assert values['iban']
            assert values['bic']
            assert values['account_number'] is None
            assert values['sort_code'] is None
            return values
        elif values['type_'] == 'account_number_sort_code':
            assert values['sort_code']
            assert values['account_number']
            assert values['iban'] is None
            assert values['bic'] is None
            return values

        raise ValueError(f"Invalid type: {values['type_']}. Type must be either 'iban', 'account_number_sort_code'")


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
