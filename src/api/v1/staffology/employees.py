import datetime
import json
from typing import Dict, List, Optional

import requests
from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.crewplanner.dto import CPEmployee
from api.v1.crewplanner.employees import crewplanner_employees_get
from api.v1.staffology.dto import (
    StaffologyAddress,
    StaffologyEmployee,
    StaffologyEmploymentDetails,
    StaffologyPersonalDetails,
    StaffologyStarterDetails,
)
from crewpay.models import CrewplannerUser, Employee, Employer, StaffologyUser


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def sync_employees(request: Request) -> Response:  # pylint: disable=unused-argument
    return process_employees(request.GET["username"])


def process_employees(username) -> Response:  # pylint: disable=unused-argument
    # some code that gets CP list and existing database employees
    employer_id = Employer.objects.get(user__username=username).id
    access_token = CrewplannerUser.objects.get(user__username=username).access_key
    stub = CrewplannerUser.objects.get(user__username=username).stub
    cp_employees = crewplanner_employees_get(stub, access_token)
    stored_cp_employee_ids = Employee.objects.filter(employer=employer_id).values_list("crewplanner_id", flat=True)
    existing_ids = []

    # new employees
    new_employee_count = 0
    for cp_employee in cp_employees:
        if cp_employee.id in stored_cp_employee_ids:
            # add id to a list of existing employees to check for updates later
            existing_ids.append(cp_employee)
            continue
        if cp_employee.status == "ARCHIVED":
            # inactive and does not exist in staffology so can just skip
            continue
        new_employee_payload = cp_emp_to_staffology_emp(cp_employee)
        created_staffology_employee = StaffologyAPI().employee_create(employer_id, new_employee_payload)
        new_employee = Employee(
            employer_id=employer_id,
            crewplanner_id=cp_employee.id,
            staffology_id=created_staffology_employee["id"],
            status="ACTIVE",
        )
        new_employee.save()
        new_employee_count += 1

    # leavers
    leavers = []
    for cp_employee in existing_ids:
        if cp_employee.status == "ARCHIVED" and Employee.objects.get(crewplanner_id=cp_employee.id).status == "ACTIVE":
            leavers.append(Employee.objects.get(crewplanner_id=cp_employee.id).staffology_id)
        else:
            continue
    if len(leavers) > 0:
        StaffologyAPI().mark_leavers(employer_id, leavers)
        Employee.objects.filter(staffology_id__in=leavers).update(status="ARCHIVED")

    # rehire
    rehires = 0
    for cp_employee in existing_ids:
        if (
            cp_employee.status != "ARCHIVED"
            and Employee.objects.get(crewplanner_id=cp_employee.id).status == "ARCHIVED"
        ):
            rehire = Employee.objects.get(crewplanner_id=cp_employee.id).staffology_id
            rehired = StaffologyAPI().mark_rehires(employer_id, rehire)
            Employee.objects.filter(crewplanner_id=cp_employee.id).update(status="ACTIVE", staffology_id=rehired["id"])
            rehires += 1
        else:
            continue

    # delete
    # update current employee list
    stored_cp_employee_ids = Employee.objects.filter(employer=employer_id).values_list("crewplanner_id", flat=True)
    # get list of stored employees not in cp
    id_list = [cp_employee.id for cp_employee in cp_employees]
    deleted = list(set(stored_cp_employee_ids).difference(id_list))
    if len(deleted) > 0:
        to_delete = []
        for cp_id in deleted:
            to_delete.append(Employee.objects.get(crewplanner_id=cp_id).staffology_id)
        StaffologyAPI().delete_employees(employer_id, to_delete)
        Employee.objects.filter(crewplanner_id__in=to_delete).delete()

    # update details
    # TODO: update employee details - need to think of a way to efficently check for differences
    # return totals
    # TODO report errors in a way to display in ui and export
    return Response(
        {
            "Employees Added": new_employee_count,
            "Marked as Leaver": len(leavers),
            "Marked as Rehired": rehires,
            "Deleted Employees": len(deleted),
        }
    )


def format_address(name: str, number: str, street: str) -> str:
    return " ".join([item for item in [name, number, street] if item is not None])


def cp_emp_to_staffology_emp(cp_emp: CPEmployee) -> StaffologyEmployee:
    return StaffologyEmployee(
        personalDetails=StaffologyPersonalDetails(
            title="",
            # TODO: custom field titles
            firstName=cp_emp.first_name,
            lastName=cp_emp.last_name,
            dateOfBirth=cp_emp.date_of_birth,
            gender=cp_emp.gender,
            maritalStatus=cp_emp.civil_status,
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
                startDate=cp_emp.created_at,
                # TODO: custom field start date - if exists use custom field
                starterDeclaration="A",
                # TODO: custom field starter declaration
            ),
        ),
    )


def staffology_employees_list(username: str) -> List[Dict]:
    employer_id = Employer.objects.get(user__username=username).id
    staff_list = StaffologyAPI().staffology_employees_get(employer_id)
    return staff_list


class StaffologyAPI:
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

    def mark_leavers(self, employer: str, employees: List[str]) -> Dict:
        now = datetime.date.today()
        params = {"date": now.strftime("%Y-%m-%d"), "emailP45": json.dumps(False)}
        return self.put(f"employers/{employer}/employees/leavers", data=json.dumps(employees), params=params).text

    def mark_rehires(self, employer: str, employee: str) -> Dict:
        return self.get(f"/employers/{employer}/employees/{employee}/rehire").json()

    def staffology_employees_get(self, employer: str) -> List[Dict]:
        return self.get(f"employers/{employer}/employees").json()

    def delete_employees(self, employer: str, employees: List[str]) -> None:
        self.post(f"/employers/{employer}/employees/delete", data=json.dumps(employees))
