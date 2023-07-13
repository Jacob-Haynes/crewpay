import json
import os

import pytest

from api.v1.crewplanner.api.employee import CPEmployeeAPI
from api.v1.crewplanner.api.report import CPReportAPI
from crewpay.models import CrewplannerUser


@pytest.fixture
def fixture_example_employees() -> dict:
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cp_example_employees.json')
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


@pytest.fixture
def fixture_example_report() -> dict:
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cp_example_report.json')
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


@pytest.fixture
def fixture_uk_payroll_test() -> CrewplannerUser:
    stub = 'uk-payroll-test'
    access_key = '2Ifb8AoiSi7axPfXjyK0O330JRyByRftDWwcTv4gXJMsVr5LV3VAQVgPjWjZVSr4'
    return CrewplannerUser(stub=stub, access_key=access_key)


def test_get_employees(fixture_example_employees: dict, fixture_uk_payroll_test: CrewplannerUser) -> None:
    # Arrange
    expected_data = fixture_example_employees
    expected_status_code = 200

    # Act
    actual = CPEmployeeAPI(user=fixture_uk_payroll_test).get_employees()

    # Assert
    assert actual.status_code == expected_status_code
    assert actual.json() == expected_data


def test_get_report(fixture_example_report: dict, fixture_uk_payroll_test: CrewplannerUser) -> None:
    # Arrange
    start_date = '2023-01-01'
    end_date = '2023-12-31'
    expected_data = fixture_example_report
    expected_status_code = 200

    # Act
    actual = CPReportAPI(user=fixture_uk_payroll_test).get_report(start_date, end_date)

    # Assert
    assert actual.status_code == expected_status_code
    assert actual.json() == expected_data
