import json
import os

import pytest

from api.v1.crewplanner.api.employee import CPEmployeeAPI
from crewpay.models import CrewplannerUser


@pytest.fixture
def fixture_example_employees():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cp_example_employees.json')
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def test_get_employees(fixture_example_employees: dict) -> None:
    # Arrange
    stub = 'uk-payroll-test'
    access_key = '2Ifb8AoiSi7axPfXjyK0O330JRyByRftDWwcTv4gXJMsVr5LV3VAQVgPjWjZVSr4'
    expected_data = fixture_example_employees
    expected_status_code = 200

    # Act
    actual = CPEmployeeAPI(user=CrewplannerUser(stub=stub, access_key=access_key)).get_employees()

    # Assert
    assert actual.status_code == expected_status_code
    assert actual.json() == expected_data

