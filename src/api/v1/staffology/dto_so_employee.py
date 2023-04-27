from typing import Optional

from pydantic import BaseModel


class StaffologyPersonalDetails(BaseModel):
    title: Optional[str] = None
    firstName: str
    lastName: str
    dateOfBirth: str
    gender: str
    maritalStatus: str
    email: str
    emailPayslip: str
    passwordProtectPayslip: str
    pdfPasswordType: str
    photoUrl: Optional[str]
    telephone: Optional[str]
    niNumber: Optional[str]
    passportNumber: Optional[str]


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


# class StaffologyAutoEnrolment(BaseModel):
# TODO: with mike https://app.staffology.co.uk/api/docs/models/autoenrolment


# class StaffologyLeaveSettings(BaseModel):
# TODO: with mike https://app.staffology.co.uk/api/docs/models/leavesettings


# class StaffologyRightToWork(BaseModel):
# TODO: with mike https://app.staffology.co.uk/api/docs/models/righttowork


class StaffologyBankDetails(BaseModel):
    accountNumber: str
    sortCode: str


class StaffologyTaxAndNi(BaseModel):
    postgradLoan: str = "false"
    studentLoan: str = "None"


class StaffologyPayOptions(BaseModel):
    taxAndNi: StaffologyTaxAndNi


class StaffologyEmployee(BaseModel):
    personalDetails: StaffologyPersonalDetails
    address: StaffologyAddress
    employmentDetails: StaffologyEmploymentDetails
    # autoEnrolment: StaffologyAutoEnrolment
    # leaveSettings: StaffologyLeaveSettings
    # rightToWork: StaffologyRightToWork
    bankDetails: StaffologyBankDetails
    payOptions: StaffologyPayOptions
