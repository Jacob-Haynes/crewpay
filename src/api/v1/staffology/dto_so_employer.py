from pydantic import BaseModel


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


class StaffologyEmployer(BaseModel):
    name: str
    defaultPayOptions: DefaultPayOptions
    leaveSettings: LeaveSettings
