import hashlib
import json
from datetime import datetime as dt
from typing import Dict, List, Optional, Union

import requests
from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.crewplanner.dto_cp_employee import CPEmployee
from api.v1.crewplanner.employees import crewplanner_employees_get
from api.v1.staffology.dto_so_employee import (
    StaffologyAddress,
    StaffologyBankDetails,
    StaffologyEmployee,
    StaffologyEmploymentDetails,
    StaffologyPayOptions,
    StaffologyPersonalDetails,
    StaffologyStarterDetails,
    StaffologyTaxAndNi,
)
from api.v1.staffology.employers import update_employer_db
from crewpay.models import (
    CrewplannerUser,
    Employee,
    Employer,
    InvalidEmployee,
    StaffologyUser,
)


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def sync_employees(request: Request) -> Response:  # pylint: disable=unused-argument
    """UI function to sync employees from crewplanner to staffology"""
    # check for employer updates
    update_employer_db(request.GET["employer"])
    return process_employees(request.GET["employer"])


def process_employees(employer_id: str) -> Response:  # pylint: disable=unused-argument
    """Main function to process employees. Firstly gets employees from CP. Then validates and creates new employees.
    Also marks leavers, rehires, and deletes employees. Finally, records failed employee imports in the database."""
    user = Employer.objects.get(id=employer_id).user
    access_token = CrewplannerUser.objects.get(user=user).access_key
    stub = CrewplannerUser.objects.get(user=user).stub
    # get cp employee list
    cp_employees_list = crewplanner_employees_get(stub, access_token)
    cp_employees = list(filter(lambda item: item is not None, cp_employees_list))
    failed_employees = len(cp_employees_list) - len(cp_employees)
    # check for employees that already exist in database
    stored_cp_employee_ids = Employee.objects.filter(employer=employer_id).values_list("crewplanner_id", flat=True)

    # check for new employees
    employees_to_update = []
    new_employee_count = 0
    for cp_employee in cp_employees:
        if cp_employee.id in stored_cp_employee_ids:
            # check for payload updates and if there are - store them to be updated
            to_update = is_employee_modified(cp_employee)
            if to_update:
                employees_to_update.append(cp_employee)
            continue
        if cp_employee.status == "ARCHIVED":
            # inactive and does not exist in staffology so can just skip
            continue
        # create new employee
        new_employee(cp_employee, employer_id)
        new_employee_count += 1

    # leavers
    leavers = mark_as_leaver(employees_to_update, employer_id)
    employees_to_update = [emp for emp in employees_to_update if emp.id not in leavers]

    # rehire
    rehires = mark_as_rehire(employees_to_update, employer_id)
    employees_to_update = [emp for emp in employees_to_update if emp.id not in rehires]

    # delete  ### this is for testing only ###
    run_delete = False
    deleted = []
    if run_delete:
        deleted = delete_employee(cp_employees, employer_id)
    employees_to_update = [emp for emp in employees_to_update if emp.id not in deleted]

    # update details in staffology
    for employee in employees_to_update:
        update_employee(employee, employer_id)
    # return totals
    failures = InvalidEmployee.objects.filter(employer=employer_id).order_by("-date_time")[:failed_employees]
    failures_list = []
    for failure in failures:
        failure_dict = {
            "employee_id": failure.employee_id,
            "name": failure.name,
            "error": failure.error,
            "date_time": failure.date_time,
        }
        failures_list.append(failure_dict)
    return Response(
        {
            "Employees Added": new_employee_count,
            "Failed to Sync": failed_employees,
            "Marked as Leaver": len(leavers),
            "Marked as Rehired": len(rehires),
            "Deleted Employees": len(deleted),
            "Updated Employees": len(employees_to_update),
            "Failed Syncs": failures_list,
        }
    )


# TODO: create this report in the UI - provide a way to view this with a user login?


def link_employee(cp_staff_list, employer_id: str) -> None:
    """this links an already existing staffology employee to a cp one via a csv.
    used primarily for importing fire but could be useful."""
    staffology_list = StaffologyEmployeeAPI().staffology_employees_get(employer_id)
    for person in cp_staff_list:
        payroll_code = person["payroll_code"]
        for staff in staffology_list:
            if staff["metadata"]["payrollCode"] == payroll_code and person["status"] == "Active":
                new_entry = Employee(
                    employer_id=employer_id,
                    crewplanner_id=person["id"],
                    staffology_id=staff["id"],
                    payroll_code=payroll_code,
                    status="ACTIVE",
                )
                new_entry.save()
            elif staff["metadata"]["payrollCode"] == payroll_code:
                new_entry = Employee(
                    employer_id=employer_id,
                    crewplanner_id=person["id"],
                    staffology_id=staff["id"],
                    payroll_code=payroll_code,
                    status="ARCHIVED",
                )
                new_entry.save()


def new_employee(cp_employee: CPEmployee, employer_id: str) -> None:
    """creates a new employee in staffology and the database"""
    new_employee_payload = cp_emp_to_staffology_emp(cp_employee, employer_id)
    created_staffology_employee = StaffologyEmployeeAPI().employee_create(employer_id, new_employee_payload)
    # create hash of employee payload for later comparison
    payload = cp_emp_to_staffology_emp(cp_employee, employer_id)
    payload_hash = consistent_hash(payload)

    new_entry = Employee(
        employer_id=employer_id,
        crewplanner_id=cp_employee.id,
        staffology_id=created_staffology_employee["id"],
        payroll_code=created_staffology_employee["employmentDetails"]["payrollCode"],
        status="ACTIVE",
        payload_hash=payload_hash,
    )
    new_entry.save()


def update_employee(cp_employee: CPEmployee, employer_id: str) -> None:
    """Updates employee data in staffology"""
    employee = Employee.objects.get(crewplanner_id=cp_employee.id)
    updated_payload = cp_emp_to_staffology_emp(cp_employee, employer_id)
    StaffologyEmployeeAPI().update_employees(employer_id, employee.staffology_id, updated_payload)
    # update hash of employee
    payload_hash = consistent_hash(updated_payload)
    employee.payload_hash = payload_hash
    employee.save()


def consistent_hash(payload: StaffologyEmployee):
    """Returns a consistent hash of the model"""
    instance_dict = payload.dict()
    sorted_dict = dict(sorted(instance_dict.items()))
    instance_str = str(sorted_dict)
    hash_object = hashlib.sha256(instance_str.encode())
    return hash_object.hexdigest()


def is_employee_modified(cp_employee: CPEmployee) -> bool:
    """Checks if the employee data is different from the stored hash"""
    employee = Employee.objects.get(crewplanner_id=cp_employee.id)
    employer_id = employee.employer.id
    new_payload = cp_emp_to_staffology_emp(cp_employee, employer_id)
    # Calculate the hash of the new payload using the same algorithm as before
    new_payload_hash = consistent_hash(new_payload)
    # Compare the new payload hash with the stored hash in the model
    if employee.payload_hash == new_payload_hash:
        return False  # Payload has not been modified
    else:
        return True  # Payload has been modified


def mark_as_leaver(existing_ids: List[CPEmployee], employer_id: str) -> List:
    """Marks archived cp employees as leavers"""
    leavers = []
    for cp_employee in existing_ids:
        if cp_employee.status == "ARCHIVED" and Employee.objects.get(crewplanner_id=cp_employee.id).status == "ACTIVE":
            leavers.append(Employee.objects.get(crewplanner_id=cp_employee.id).staffology_id)
        else:
            continue
    if len(leavers) > 0:
        StaffologyEmployeeAPI().mark_leavers(employer_id, leavers)
        Employee.objects.filter(staffology_id__in=leavers).update(status="ARCHIVED")
    return leavers


def mark_as_rehire(existing_ids: List[CPEmployee], employer_id: str) -> List:
    """Marks un-archived cp employees as rehires"""
    rehires = []
    for cp_employee in existing_ids:
        if (
            cp_employee.status != "ARCHIVED"
            and Employee.objects.get(crewplanner_id=cp_employee.id).status == "ARCHIVED"
        ):
            rehire = Employee.objects.get(crewplanner_id=cp_employee.id).staffology_id
            rehired = StaffologyEmployeeAPI().mark_rehires(employer_id, rehire)
            Employee.objects.filter(crewplanner_id=cp_employee.id).update(status="ACTIVE", staffology_id=rehired["id"])
            rehires.append(rehire)
        else:
            continue
    return rehires


def delete_employee(cp_employees: List[CPEmployee], employer_id: str) -> List:
    """Deletes non-existent cp employees from staffology and the db"""
    # update current employee list
    stored_cp_employee_ids = Employee.objects.filter(employer=employer_id).values_list("crewplanner_id", flat=True)
    # get list of stored employees not in cp
    id_list = [cp_employee.id for cp_employee in cp_employees]
    deleted = list(set(stored_cp_employee_ids).difference(id_list))
    to_delete = []
    # delete them from staffology and database
    if len(deleted) > 0:
        for cp_id in deleted:
            to_delete.append(Employee.objects.get(crewplanner_id=cp_id).staffology_id)
        StaffologyEmployeeAPI().delete_employees(employer_id, to_delete)
        Employee.objects.filter(crewplanner_id__in=to_delete).delete()
    return to_delete


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


class StaffologyEmployeeAPI:
    """Handles all staffology employee api calls"""

    def __init__(self, admin_user: str = "admin"):
        self.base_url = "https://api.staffology.co.uk/"
        self.admin_user = admin_user
        self.headers = {"content-type": "text/json"}
        access_key = StaffologyUser.objects.get(user__username=admin_user).staffology_key
        self.auth = ("username", access_key)

    def get(self, endpoint: str) -> requests.Response:
        response = requests.get(
            f"{self.base_url}{endpoint}",
            auth=self.auth,
            headers=self.headers,
        )
        if not response.ok:
            raise ValueError(response.text)
        return response

    def post(self, endpoint: str, data: str) -> requests.Response:
        response = requests.post(
            f"{self.base_url}{endpoint}",
            auth=self.auth,
            data=data,
            headers=self.headers,
        )
        if not response.ok:
            raise ValueError(response.text)
        return response

    def put(self, endpoint: str, data: str, params: Optional[Dict] = None) -> requests.Response:
        response = requests.put(
            f"{self.base_url}{endpoint}", auth=self.auth, data=data, headers=self.headers, params=params
        )
        if not response.ok:
            raise ValueError(response.text)
        return response

    def employee_create(self, employer: str, employee: StaffologyEmployee) -> Dict:
        return self.post(f"employers/{employer}/employees", data=employee.json()).json()

    def mark_leavers(self, employer: str, employees: List[str]) -> None:
        now = dt.today()
        params = {"date": now.strftime("%Y-%m-%d"), "emailP45": json.dumps(False)}
        self.put(f"employers/{employer}/employees/leavers", data=json.dumps(employees), params=params)

    def mark_rehires(self, employer: str, employee: str) -> Dict:
        return self.get(f"/employers/{employer}/employees/{employee}/rehire").json()

    def staffology_employees_get(self, employer: str) -> List[Dict]:
        return self.get(f"employers/{employer}/employees").json()

    def delete_employees(self, employer: str, employees: List[str]) -> None:
        self.post(f"/employers/{employer}/employees/delete", data=json.dumps(employees))

    def update_employees(self, employer: str, employee_id: str, employee: StaffologyEmployee) -> None:
        self.put(f"/employers/{employer}/employees/{employee_id}", data=employee.json()).json()
