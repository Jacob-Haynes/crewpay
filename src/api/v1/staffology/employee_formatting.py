from datetime import datetime as dt

from api.v1.crewplanner.dto_cp_employee import CPEmployee
from api.v1.staffology.dto_so_employee import StaffologyEmployee, StaffologyPersonalDetails, StaffologyAddress, \
    StaffologyEmploymentDetails, StaffologyStarterDetails, StaffologyBankDetails, StaffologyPayOptions, \
    StaffologyTaxAndNi
from crewpay.models import Employer

"""Handles all functions that format employee data from CP to Staffology"""


def format_address(name: str, number: str, street: str) -> str:
    """Formats a cp address into a staffology address"""
    return " ".join([item for item in [name, number, street] if item is not None])


def format_start_date(created_at: str, start_date: str) -> str:
    """Chooses the start date for a cp employee"""
    if start_date is None:
        return created_at
    else:
        date_string = start_date
        date_format = "%Y-%m-%d"
        try:
            dt.strptime(date_string, date_format)
            return date_string
        except ValueError:
            return created_at


def format_marital_status(civil_status) -> str:
    """Formats marital status and deals with nullable"""
    options = ["Single", "Married", "Divorced", "Widowed", "CivilPartnership", "Unknown"]
    if civil_status is None:
        return "Unknown"
    elif civil_status in options:
        return civil_status
    else:
        return "Unknown"


def format_student_loan(s) -> str:
    """Replaces 'Plan 1', 'Plan 2', and 'Plan 4' with 'PlanOne', 'PlanTwo', and 'PlanFour', respectively."""
    s = s.replace("Plan 1", "PlanOne")
    s = s.replace("Plan 2", "PlanTwo")
    s = s.replace("Plan 4", "PlanFour")
    return s


def format_postgrad_loan(s: str) -> str:
    """Replaces Yes No string with true false string"""
    s = s.replace("Yes", "true")
    s = s.replace("No", "false")
    return s


def age(dob: str) -> int:
    """works out the workers age for ni table"""
    dob_dt = dt.strptime(dob, "%Y-%m-%d")
    today = dt.today()
    worker_age = abs(dob_dt - today)
    return int(worker_age.days / 365)


def format_ni_table(worker_age: int) -> str:
    if worker_age < 21:
        ni_table = "M"
    elif worker_age > 66:
        ni_table = "C"
    else:
        ni_table = "A"
    return ni_table


def cp_emp_to_staffology_emp(cp_emp: CPEmployee, employer_id) -> StaffologyEmployee:
    """Converts a cp employee to a staffology employee data structure"""
    return StaffologyEmployee(
        personalDetails=StaffologyPersonalDetails(
            firstName=cp_emp.first_name,
            lastName=cp_emp.last_name,
            dateOfBirth=cp_emp.date_of_birth,
            gender=cp_emp.gender,
            maritalStatus=format_marital_status(cp_emp.civil_status),
            email=cp_emp.email,
            emailPayslip="true",
            passwordProtectPayslip="true",
            pdfPasswordType="InitialsAndDob",
            photoUrl=cp_emp.profile_picture_url,
            telephone=cp_emp.phone_number,
            niNumber=cp_emp.registration_numbers.nino,
            passportNumber=cp_emp.registration_numbers.passport_number,
        ),
        address=StaffologyAddress(
            line1=format_address(cp_emp.address.name, cp_emp.address.number, cp_emp.address.street),
            line2=cp_emp.address.addition,
            line3=cp_emp.address.city,
            postCode=cp_emp.address.zip_code,
            country=cp_emp.address.country,
        ),
        employmentDetails=StaffologyEmploymentDetails(
            payrollCode=f"cp{cp_emp.id}",
            starterDetails=StaffologyStarterDetails(
                startDate=format_start_date(cp_emp.created_at, cp_emp.custom_fields.payroll_start_date),
                starterDeclaration=cp_emp.custom_fields.payroll_employee_statement.name[0],
            ),
        ),
        bankDetails=StaffologyBankDetails(
            accountNumber=cp_emp.bank_account.account_number,
            sortCode=cp_emp.bank_account.sort_code,
        ),
        payOptions=StaffologyPayOptions(
            period=Employer.objects.get(id=employer_id).pay_period,
            taxAndNi=StaffologyTaxAndNi(
                niTable=format_ni_table(age(cp_emp.date_of_birth)),
                postgradLoan=format_postgrad_loan(cp_emp.custom_fields.payroll_postgrad_loan.name),
                studentLoan=format_student_loan(cp_emp.custom_fields.payroll_student_loan_plan.name),
            ),
        ),
        # TODO: await address fix from mich
        # TODO: validate bank accounts using open banking? or from staffology
        # TODO: handle staffology data rejection eg invalid national insurance
        # TODO: Validation for if required custom fields do not exist isnt working
    )
