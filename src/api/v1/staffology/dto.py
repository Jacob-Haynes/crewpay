from typing import Optional

from pydantic import BaseModel


class StaffologyPersonalDetails(BaseModel):
    title: str
    firstName: str
    lastName: str
    dateOfBirth: str
    gender: str
    maritalStatus: Optional[str] = None


class StaffologyAddress(BaseModel):
    line1: str
    line2: Optional[str] = None
    line3: str
    postCode: str
    country: str


class StaffologyStarterDetails(BaseModel):
    startDate: str
    starterDeclaration: str


class StaffologyEmploymentDetails(BaseModel):
    payrollCode: str
    starterDetails: StaffologyStarterDetails


class StaffologyEmployee(BaseModel):
    personalDetails: StaffologyPersonalDetails
    address: StaffologyAddress
    employmentDetails: StaffologyEmploymentDetails
