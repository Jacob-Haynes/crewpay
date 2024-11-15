import json
from pathlib import Path

import pytest
from pydantic import BaseModel, ValidationError

from api.v1.crewplanner.dto.dto_cp_employee import CPEmployee
from api.v1.crewplanner.employees import api_get_cp_employees, validate_employee
from api.v1.staffology.api.employees import StaffologyEmployeeAPI
from api.v1.staffology.dto.dto_so_employee import StaffologyEmployee
from api.v1.staffology.employees.employee_manager import EmployeeManager
from crewpay.models import CrewplannerUser


@pytest.fixture
def data_path() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture()
def expected_crewplanner_employee(data_path: Path) -> dict:
    with open(data_path / "expected_cp.json") as f:
        data = json.load(f)["data"]
    return data


@pytest.fixture
def address_error_crewplanner_employee(data_path: Path) -> dict:
    with open(data_path / "address_error_cp.json") as f:
        data = json.load(f)["data"]
    return data


@pytest.fixture
def details_error_crewplanner_employee(data_path: Path) -> dict:
    with open(data_path / "details_error_cp.json") as f:
        data = json.load(f)["data"]
    return data


@pytest.fixture
def lisa_hunt(data_path: Path) -> dict:
    with open(data_path / "lisa_hunt.json") as f:
        data = json.load(f)["data"]
    return data


def test_report_get():
    stub = "demo-4"
    access_token = CrewplannerUser.objects.get(stub=stub).access_key
    report = api_get_cp_employees(stub, access_token)
    return


def test_validation():
    stub = "demo-4"
    access_token = CrewplannerUser.objects.get(stub=stub).access_key
    results = api_get_cp_employees(stub, access_token)
    for employee in results:
        try:
            cp_employee = CPEmployee(**employee)
            return cp_employee
        except ValidationError as e:
            error = str(e)
            name = f"{employee['first_name']} {employee['last_name']}"
            print(f"{name}: {error}")


def test_employee_valid(expected_crewplanner_employee):
    stub = "TEST DATA"
    employee_list = [validate_employee(stub, expected_crewplanner_employee[0])]
    return


def test_employee_address_error(address_error_crewplanner_employee):
    stub = "TEST DATA"
    employee_list = [validate_employee(stub, address_error_crewplanner_employee[0])]
    return


def test_employee_details_error(details_error_crewplanner_employee):
    stub = "TEST DATA"
    employee_list = [validate_employee(stub, details_error_crewplanner_employee[0])]
    return


def test_employee_lisa_hunt(lisa_hunt):
    stub = "TEST DATA"
    employee_list = [validate_employee(stub, lisa_hunt[0])]

