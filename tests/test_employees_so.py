from typing import Dict, List

import pytest
from django.contrib.auth.models import User

from api.v1.staffology.employees import process_employees, staffology_employees_list
from crewpay.models import Employer


@pytest.fixture
def admin_user() -> User:
    return User.objects.get(username="admin")


def test_process_employees():
    employer = Employer.objects.get(user__username="UK Payroll Test").id
    process_employees(employer)


def test_get_employees():
    staffology_employees_list('UK Payroll Test')
