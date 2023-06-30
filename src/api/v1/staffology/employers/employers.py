from typing import Dict

from rest_framework.authtoken.admin import User

from api.v1.staffology.api.employers import StaffologyEmployerAPI
from api.v1.staffology.dto.dto_so_employer import (
    DefaultPayOptions,
    LeaveSettings,
    StaffologyEmployer,
)
from crewpay.models import Employer


def create_employer(
    user: User, pay_period: str, tax_year: str, period_end: str, payment_date: str, so_employer: StaffologyEmployer
) -> None:
    """Create a new employer in staffology and the db from their crewplanner data."""
    payload = so_employer.dict()
    employer_data = StaffologyEmployerAPI().create_employer(payload)
    schedule(employer_data["id"], pay_period, tax_year, period_end, payment_date)
    employer = Employer(user=user, id=employer_data["id"], pay_period=pay_period)
    employer.save()


def schedule(employer: str, pay_period: str, tax_year: str, period_end: str, payment_date: str) -> None:
    """Set up the pay schedule for a given employer."""
    payload = {"firstPeriodEndDate": period_end, "firstPaymentDate": payment_date}
    StaffologyEmployerAPI().update_pay_schedule(
        employer=employer, tax_year=tax_year, pay_period=pay_period, payload=payload
    )


def activate_payruns(schedule_to_run: Dict, employer: str, tax_year: str, pay_period: str) -> Dict:
    """Activate payruns for a given employers pay schedule."""
    # activate if needed
    if schedule_to_run["isRequired"] and not schedule_to_run["hasOpenPayRunPeriod"]:
        StaffologyEmployerAPI().start_next_payrun(employer, tax_year, pay_period)
    # get the next pay run
    pay_run = next_pay_run(StaffologyEmployerAPI().get_pay_schedule(employer, tax_year, pay_period))
    return pay_run


def next_pay_run(pay_schedule: Dict) -> Dict:
    """Identify the next pay run for a given pay schedule."""
    if "currentPayRun" in pay_schedule and not pay_schedule["currentPayRun"]["metadata"]["isClosed"]:
        return pay_schedule["currentPayRun"]
    elif not pay_schedule["nextPayRun"]["isClosed"]:
        return pay_schedule["nextPayRun"]
    return {}


def staffology_employer(request) -> StaffologyEmployer:
    """creates a staffology employer object from the ui create employer form"""
    leave_type = request.POST["leave_type"]
    show_allowance_on_pay_slip = request.POST["show_allowance_on_pay_slip"]
    accrue_payment_in_lieu_pay_automatically = request.POST["accrue_payment_in_lieu_pay_automatically"]
    accrue_payment_in_lieu_all_gross_pay = request.POST["accrue_payment_in_lieu_all_gross_pay"]
    accrue_payment_in_lieu_rate = request.POST["accrue_payment_in_lieu_rate"]
    show_ahp_on_pay_slip = request.POST["show_ahp_on_pay_slip"]

    if leave_type == "Accrual_Money":
        leave_settings = LeaveSettings(
            holidayType=leave_type,
            showAllowanceOnPayslip=show_allowance_on_pay_slip,
            accruePaymentInLieuPayAutomatically=accrue_payment_in_lieu_pay_automatically,
            accruePaymentInLieuAllGrossPay=accrue_payment_in_lieu_all_gross_pay,
            accruePaymentInLieuRate=accrue_payment_in_lieu_rate,
            showAhpOnPayslip=show_ahp_on_pay_slip,
        )
    elif leave_type == "Accrual_Days":
        allowance_reset_date = request.POST["allowance_reset_date"]
        accrue_set_amount = request.POST["accrue_set_amount"]
        accrue_hours_per_day = request.POST["accrue_hours_per_day"]

        leave_settings = LeaveSettings(
            holidayType=leave_type,
            allowanceResetDate=allowance_reset_date,
            showAllowanceOnPayslip=show_allowance_on_pay_slip,
            accrueSetAmount=accrue_set_amount,
            accruePaymentInLieuRate=accrue_payment_in_lieu_rate,
            accrueHoursPerDay=accrue_hours_per_day,
            showAhpOnPayslip=show_ahp_on_pay_slip,
        )
    else:
        allowance_reset_date = request.POST["allowance_reset_date"]
        accrue_set_amount = request.POST["accrue_set_amount"]

        leave_settings = LeaveSettings(
            holidayType=leave_type,
            allowanceResetDate=allowance_reset_date,
            showAllowanceOnPayslip=show_allowance_on_pay_slip,
            accrueSetAmount=accrue_set_amount,
            showAhpOnPayslip=show_ahp_on_pay_slip,
        )

    return StaffologyEmployer(
        name=request.POST["name"],
        defaultPayOptions=DefaultPayOptions(
            period=request.POST["pay_period"],
        ),
        leaveSettings=leave_settings,
    )


def update_employer_db(employer_id: str) -> None:
    """checks staffology for updates to an employers settings and updates them in the local db"""
    employer_data = StaffologyEmployerAPI().get_employer(employer_id)
    pay_period = employer_data["defaultPayOptions"]["period"]
    employer = Employer.objects.get(id=employer_id)
    employer.pay_period = pay_period
    employer.save()
