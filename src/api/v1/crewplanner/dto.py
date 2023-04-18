from typing import List, Optional

from pydantic import BaseModel


class CPRegistrationNumber(BaseModel):
    nino: Optional[str]


class CPAddress(BaseModel):
    name: Optional[str]
    street: Optional[str]
    number: Optional[str]
    addition: Optional[str]
    zip_code: str
    city: Optional[str]
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
