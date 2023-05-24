import itertools

from api.v1.crewplanner.dto.dto_cp_ShiftsByUser import CPShiftsByUser
from api.v1.crewplanner.report import create_shift_lines
from api.v1.staffology.api.employers import StaffologyEmployerAPI
from api.v1.staffology.employers.employers import activate_payruns, update_employer_db
from api.v1.staffology.payroll.date_handeling import compute_report_dates
from api.v1.staffology.payroll.pay_line import create_pay_line
from crewpay.models import Employer, InvalidShift


class PayrollManager:
    def __init__(self, employer: str, tax_year: str, arrears: int):
        self.employer = employer
        self.tax_year = tax_year
        self.arrears = arrears
        self.employer_instance = None
        self.user = None
        self.pay_period = None
        self.pay_run = None
        self.shift_lines = []
        self.failed_shifts = 0
        self.pay_lines = []

    def update_employer(self):
        """Update employer in the local database with any changes."""
        update_employer_db(self.employer)
        self.employer_instance = Employer.objects.get(id=self.employer)
        self.user = self.employer_instance.user
        self.pay_period = self.employer_instance.pay_period

    def get_pay_schedule(self):
        """Get pay schedules"""
        return StaffologyEmployerAPI().get_pay_schedule(self.employer, self.tax_year, self.pay_period)

    def activate_pay_runs(self, schedule_to_run):
        """Activate the payrun if needed"""
        return activate_payruns(schedule_to_run, self.employer, self.tax_year, self.pay_period)

    def get_full_pay_run(self):
        """Get the full payrun data"""
        period_number = self.pay_run["metadata"]["periodNumber"]
        return StaffologyEmployerAPI().get_pay_run(self.employer, self.tax_year, self.pay_period, period_number)

    def compute_report_dates(self):
        """Compute earnings period dates based on the selected arrears period"""
        start_date = self.pay_run["startDate"]
        end_date = self.pay_run["endDate"]
        earnings_period_start, earnings_period_end = compute_report_dates(
            start_date, end_date, self.pay_period, self.arrears
        )
        return earnings_period_start, earnings_period_end

    def create_shift_lines(self):
        """Get shift lines from CP based on earnings period"""
        earnings_period_start, earnings_period_end = self.compute_report_dates()
        self.shift_lines, self.failed_shifts = create_shift_lines(self.user, earnings_period_start, earnings_period_end)

    def group_shifts_by_user(self):
        """Group shift lines by employee"""
        shifts_by_user = []
        for user_id, shifts in itertools.groupby(self.shift_lines, key=lambda x: x.worker.user.id):
            shifts_by_user.append(CPShiftsByUser(user_id=user_id, shifts=list(shifts)))
        return shifts_by_user

    def create_pay_lines(self):
        """Convert the grouped CP shift lines to Staffology pay lines"""
        shifts_by_user = self.group_shifts_by_user()
        self.pay_lines = [create_pay_line(user_shifts) for user_shifts in shifts_by_user]

    def import_pay_lines(self):
        """Post pay lines to Staffology API"""
        payload = [pay_line.dict() for pay_line in self.pay_lines]
        StaffologyEmployerAPI().import_pay(self.employer, self.pay_period, payload)

    def get_failed_imports(self):
        """track failed imports"""
        failures = InvalidShift.objects.filter(employer=self.employer).order_by("date_time")[: self.failed_shifts]
        failures_list = []
        for failure in failures:
            failure_dict = {
                "project": failure.project,
                "employee": failure.employee,
                "error": failure.error,
                "date_time": failure.date_time,
            }
            failures_list.append(failure_dict)
        return failures_list

    def process_payroll(self):
        """wrapper function"""
        self.update_employer()
        schedule_to_run = self.get_pay_schedule()
        self.pay_run = self.activate_pay_runs(schedule_to_run)
        self.pay_run = self.get_full_pay_run()
        self.create_shift_lines()
        self.create_pay_lines()
        self.import_pay_lines()

        shifts_added = len(self.shift_lines)
        users_added = len(self.pay_lines)
        failures_list = self.get_failed_imports()

        return {
            "shifts_added": shifts_added,
            "users_added": users_added,
            "Failed Imports": failures_list,
        }


# # Usage:
# manager = PayrollManager(employer='your_employer_id', tax_year='2023', arrears=0)
# result = manager.process_payroll()
