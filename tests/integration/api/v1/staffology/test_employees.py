from typing import Dict, List

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, APIClient

from api.v1.staffology.employees import process_employees, staffology_employees_list


@pytest.fixture
def admin_user() -> User:
    return User.objects.get(username="admin")


@pytest.fixture()
def expected_staffology_employee() -> List[Dict]:
    return [
        {
            "id": "1fbd28e4-f9c8-4e87-ab9b-adf163c078da",
            "metadata": {
                "aeNotEnroledWarning": False,
                "aeState": "Automatic",
                "basicPay": 0.0,
                "emailPayslip": False,
                "isDirector": False,
                "ordinal": 1,
                "payScheduleName": "Monthly",
                "payrollCode": "1",
                "period": "Monthly",
                "status": "Current",
                "subContractor": False,
                "taxCode": "1257L",
            },
            "name": "Mr Benedict Cumberbatch",
            "url": "https://api.staffology.co.uk/employers/14e264bf-28a2-4837-a920-290b27635e22/employees/1fbd28e4-f9c8-4e87-ab9b-adf163c078da",
        }
    ]


def test_staffology_employees_get(admin_user: User, expected_staffology_employee: List[Dict]):
    # Arrange
    user = User.objects.get(username="CP demo")

    # Act
    actual = staffology_employees_list(user.username, admin_user)

    # Assert
    assert actual == expected_staffology_employee


def test_process_employees():
    process_employees('UK Payroll Test')


def test_get_employees():
    staffology_employees_list('UK Payroll Test')

def test_sync_employees():
    test_sync_employees()
