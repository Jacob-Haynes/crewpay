import csv
import json
from pathlib import Path

import pytest
from django.contrib.auth.models import User

from api.v1.staffology.dto.dto_so_employee_full import StaffologyEmployeeFull
from api.v1.staffology.employees.employee_handling import link_employee


@pytest.fixture
def admin_user() -> User:
    return User.objects.get(username="admin")


@pytest.fixture
def data_path() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture()
def so_employee_payload(data_path: Path) -> dict:
    with open(data_path / "so_employee_payload.json") as f:
        data = json.load(f)
    return data


def test_staffology_employee_full(so_employee_payload):
    so_employee_full = StaffologyEmployeeFull(**so_employee_payload)
    return
