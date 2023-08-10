import re
from typing import Optional, Union

from pydantic import BaseModel, Field, root_validator, validator


class CPRegistrationNumber(BaseModel):
    nino: Optional[str] = None
    passport_number: Optional[str] = None

    @validator("nino", pre=True)
    def validate_nino(cls, value):
        if value is not None:
            nino_pattern = r"^[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z]\d{6}[A-D\s]$"
            if not re.match(nino_pattern, value):
                raise ValueError("Invalid NI number format.")
        return value


class CPAddress(BaseModel):
    name: Optional[str]
    street: str
    number: str
    addition: Optional[str]
    zip_code: str
    city: str
    country: Optional[str]

    @validator("name", "street", "number", "addition", "zip_code", "city", "country")
    def validate_characters(cls, value):
        valid_characters_pattern = r"^$|^[A-Za-z0-9 .,\-(\\)/=!\"%&*;<>\'+:?’]+$"
        if value is not None and not re.match(valid_characters_pattern, value):
            raise ValueError("Invalid characters in address field.")
        return value


class CPBankAccount(BaseModel):
    type_: str = Field(alias="type")
    account_number: Optional[str] = None
    sort_code: Optional[str] = None
    iban: Optional[str] = None
    bic: Optional[str] = None

    @root_validator(allow_reuse=True)
    def validator_bank_type(cls, values):
        if values["type_"] == "iban":
            assert values["iban"]
            assert values["bic"]
            assert values["account_number"] is None
            assert values["sort_code"] is None

            # Validate IBAN format
            iban_pattern = r"^GB\d{2}[A-Z]{4}\d{14}$"
            if not re.match(iban_pattern, values["iban"]):
                raise ValueError("Invalid IBAN format.")

            # Validate GB bank IBAN
            if values["iban"][:2] != "GB":
                raise ValueError("IBAN must be for a GB bank.")

            return values

        elif values["type_"] == "account_number_sort_code":
            assert values["sort_code"]
            assert values["account_number"]
            assert values["iban"] is None
            assert values["bic"] is None

            # Validate account number format
            account_number_pattern = r"^\d{8}$"
            if not re.match(account_number_pattern, values["account_number"]):
                raise ValueError("Invalid account number format.")

            # Validate sort code format
            sort_code_pattern = r"^\d{2}-\d{2}-\d{2}$"
            if not re.match(sort_code_pattern, values["sort_code"]):
                raise ValueError("Invalid sort code format.")

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
