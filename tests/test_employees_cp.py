import json
from pathlib import Path

import pytest

from api.v1.crewplanner.employees import validate_employee

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

