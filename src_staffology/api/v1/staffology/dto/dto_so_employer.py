from datetime import datetime as dt
from typing import Optional

from pydantic import BaseModel


class DefaultPayOptions(BaseModel):
    period: str


class LeaveSettings(BaseModel):
    holidayType: str
    accrueSetAmount: Optional[str]
    accrueHoursPerDay: Optional[str]
    showAllowanceOnPayslip: Optional[str]
    showAhpOnPayslip: Optional[str] = "false"
    accruePaymentInLieuRate: Optional[str] = "12.07"
    accruePaymentInLieuPayAutomatically: Optional[str]
    allowanceResetDate: Optional[str] = dt.today().strftime("%Y-%m-%d")
    accruePaymentInLieuAllGrossPay: Optional[str] = "true"


class StaffologyEmployer(BaseModel):
    name: str
    defaultPayOptions: DefaultPayOptions
    leaveSettings: LeaveSettings
