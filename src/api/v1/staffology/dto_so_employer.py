from pydantic import BaseModel
from datetime import datetime as dt


class DefaultPayOptions(BaseModel):
    payPeriod: str


class LeaveSettings(BaseModel):
    holidayType: str
    accrueSetAmount: str
    accrueHoursPerDay: str = "0"
    showAllowanceOnPayslip: str
    showAhpOnPayslip: str
    accruePaymentInLieuRate: str = "12.07"
    accruePaymentInLieuPayAutomatically: str
    allowanceResetDate: str = dt.today().strftime("%Y-%m-%d")
    # TODO: this needs to be configurable and only if days/accrue days are chosen
    accruePaymentInLieuAllGrossPay: str = "true"
    # TODO: configure for if accrue money is chosen


class StaffologyEmployer(BaseModel):
    name: str
    defaultPayOptions: DefaultPayOptions
    leaveSettings: LeaveSettings
