from typing import Optional

from pydantic import BaseModel


class CPRegistrationNumber(BaseModel):
    nino: Optional[str]


class CPAddress(BaseModel):
    name: Optional[str]
    street: str
    number: str
    addition: Optional[str]
    zip_code: str
    city: str
    country: Optional[str]


class CPEmployee(BaseModel):
    id: str
    first_name: str
    last_name: str
    status: str
    civil_status: Optional[str]
    gender: str
    date_of_birth: str
    registration_numbers: CPRegistrationNumber
    address: CPAddress
    created_at: str


# TODO add custom fields?
