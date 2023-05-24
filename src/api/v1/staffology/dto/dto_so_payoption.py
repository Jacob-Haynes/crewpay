from typing import List, Optional

from pydantic import BaseModel


class TaxAndNi(BaseModel):
    niTable: str
    postgradLoan: Optional[bool]
    postgraduateLoanStartDate: Optional[str]
    postgraduateLoanEndDate: Optional[str]
    studentLoan: Optional[str]
    studentLoanStartDate: Optional[str]
    studentLoanEndDate: Optional[str]
    taxCode: Optional[str]


class FpsFields(BaseModel):
    hoursNormallyWorked: str


class RegularPayLine(BaseModel):
    value: float
    rate: float
    multiplier: float
    description: str
    code: str
    tags: Optional[List[str]]
    effectiveFrom: str
    effectiveTo: str


class EmployeePay(BaseModel):
    period: str
    ordinal: Optional[int]
    payAmount: float
    basis: str
    nationalMinimumWage: Optional[bool]
    payAmountMultiplier: Optional[float]
    baseHourlyRate: float
    baseDailyRate: float
    autoAdjustForLeave: bool
    method: Optional[str]
    payCode: Optional[str]
    withholdTaxRefundIfPayIsZero: bool
    mileageVehicleType: Optional[str]
    mapsMiles: int
    taxAndNi: TaxAndNi
    fpsFields: FpsFields
    regularPayLines: List[RegularPayLine]
    tags: Optional[List[str]]
