import itertools
import json
from datetime import datetime as dt
from datetime import timedelta
from typing import Dict, Optional

from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.crewplanner.dto_cp_ShiftsByUser import CPShiftsByUser
from api.v1.crewplanner.report import create_shift_lines
from api.v1.staffology.dto_so_pay_options_import import Line, PayLine
from api.v1.staffology.employers import (
    StaffologyEmployerAPI,
    activate_payruns,
    update_employer_db,
)
from crewpay.models import Employee, Employer, InvalidShift


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def run_payroll(request: Request):
    """API endpoint"""
    employer = request.GET["employer"]
    tax_year = request.GET["tax_year"]
    arrears = int(request.GET["period_arrears"])
    return payroll_function(employer, tax_year, arrears)


def payroll_function(employer: str, tax_year: str, arrears: int):
    """imports the earnings reports into a staffology payrun"""
    # update employer options
    update_employer_db(employer)
    user = Employer.objects.get(id=employer).user
    pay_period = Employer.objects.get(id=employer).pay_period
    # get pay schedules
    schedule_to_run = StaffologyEmployerAPI().get_pay_schedule(employer, tax_year, pay_period)
    # activate/get the payrun
    pay_run = activate_payruns(schedule_to_run, employer, tax_year, pay_period)
    # get the full payrun to edit
    pay_run = StaffologyEmployerAPI().get_pay_run(employer, tax_year, pay_period, pay_run["metadata"]["periodNumber"])
    # get shift lines from CP
    earnings_period_start, earnings_period_end = compute_report_dates(
        pay_run["startDate"], pay_run["endDate"], pay_period, arrears
    )
    shift_lines, failed_shifts = create_shift_lines(user, earnings_period_start, earnings_period_end)
    # group by employee
    shifts_by_user = []
    for user_id, shifts in itertools.groupby(shift_lines, key=lambda x: x.worker.user.id):
        shifts_by_user.append(CPShiftsByUser(user_id=user_id, shifts=list(shifts)))
    # convert to Staffology pay lines
    pay_lines = []
    for user_shifts in shifts_by_user:
        pay_lines.append(create_pay_line(user_shifts))
    # post to staffology api
    payload = [pay_line.dict() for pay_line in pay_lines]
    StaffologyEmployerAPI().import_pay(employer, pay_period, payload)
    # totals
    shifts_added = len(shift_lines)
    users_added = len(pay_lines)
    failures = InvalidShift.objects.filter(employer=employer).order_by("date_time")[:failed_shifts]
    failures_list = []
    for failure in failures:
        failure_dict = {
            "project": failure.project,
            "employee": failure.employee,
            "error": failure.error,
            "date_time": failure.date_time,
        }
        failures_list.append(failure_dict)

    return Response(
        {
            "shifts_added": shifts_added,
            "users_added": users_added,
            "Failed Imports": failures_list,
        }
    )


def compute_report_dates(start_date: str, end_date: str, pay_period: str, arrears: int):
    """computes the dates required for the earnings report based on pay period and arrears"""
    payrun_start_date = dt.strptime(start_date, "%Y-%m-%d")
    payrun_end_date = dt.strptime(end_date, "%Y-%m-%d")
    if arrears == 0:
        earnings_period_start = start_date
        earnings_period_end = end_date
    else:
        if pay_period == "Monthly":
            report_start_date = payrun_start_date + relativedelta(months=-arrears)
            report_end_date = report_start_date + relativedelta(months=1, days=-1)
            earnings_period_start = report_start_date.strftime("%Y-%m-%d")
            earnings_period_end = report_end_date.strftime("%Y-%m-%d")
        else:
            delta = compute_timedelta(pay_period, arrears)
            report_start_date = payrun_start_date - delta
            report_end_date = payrun_end_date - delta
            earnings_period_start = report_start_date.strftime("%Y-%m-%d")
            earnings_period_end = report_end_date.strftime("%Y-%m-%d")
    return earnings_period_start, earnings_period_end


def compute_timedelta(pay_period: str, arrears: int) -> timedelta:
    """computes time deltas for various arrears and pay periods"""
    if pay_period == "Daily":
        return timedelta(days=arrears)
    elif pay_period == "Weekly":
        return timedelta(weeks=arrears)
    elif pay_period == "Fortnightly":
        return timedelta(weeks=(2 * arrears))
    elif pay_period == "Four Weekly":
        return timedelta(weeks=(4 * arrears))
    else:
        raise ValueError("Invalid pay period specified.")


def create_pay_line(user_shifts: CPShiftsByUser) -> PayLine:
    """Converts  cp shifts by user to a staffology Payline"""
    new_lines = []
    for shift in user_shifts.shifts:
        code = "BASICHOURLY" if shift.wage.type_ == "hourly" else "BASICDAILY"
        new_lines.append(
            Line(
                value=shift.wage.total,
                rate=shift.wage.value,
                multiplier=shift.timesheet.registered.netto_minutes / 60,
                description=f"{shift.project.date} - {shift.project.company.name} - {shift.project.name}",
                code=code,
            )
        )

    return PayLine(
        payrollCode=Employee.objects.get(crewplanner_id=user_shifts.user_id).payroll_code,
        lines=new_lines,
    )
