from unittest.mock import MagicMock, Mock, patch

import pytest
from django.db import transaction
from pydantic import ValidationError

from api.v1.crewplanner.api.base import CrewPlannerAPI
from api.v1.crewplanner.dto.dto_cp_employee import CPEmployee
from api.v1.crewplanner.employees import get_valid_cp_employees, validate_employee
from crewpay.models import Employer, InvalidEmployee


@pytest.fixture
def mock_user() -> Mock:
    user = MagicMock()
    user.stub = "example-stub"
    user.access_key = "example-access-key"
    return user


@pytest.fixture
def mock_employee() -> dict:
    mock = {
        "id": "123",
        "first_name": "John",
        "last_name": "Smith",
        "email": "john@smith.com",
        "status": "active",
        "civil_status": "single",
        "gender": "male",
        "date_of_birth": "2000-01-01",
        "registration_numbers": {
            "nino": "AB123456A",
        },
        "address": {
            "name": None,
            "street": "street",
            "number": "1",
            "addition": None,
            "zip_code": "zipcode",
            "city": "city",
            "country": None,
        },
        "created_at": "2020-01-01",
        "bank_account": {
            "type": "account_number_sort_code",
            "account_number": "12345678",
            "sort_code": "01-01-01",
        },
        "custom_fields": {
            "payroll_employee_statement": [
                {
                    "id": 1,
                    "name": "name",
                }
            ],
            "payroll_student_loan_plan": [
                {
                    "id": 1,
                    "name": "name",
                }
            ],
            "payroll_postgrad_loan": [
                {
                    "id": 1,
                    "name": "name",
                }
            ],
        },
    }
    return mock

@pytest.fixture
def mock_invalid_employee() -> dict:
    mock = {
        "id": "123",
        "first_name": "John",
        "last_name": "Smith",
        "email": "john@smith.com",
        "status": "active",
        "civil_status": "single",
        "gender": "male",
        "date_of_birth": "2000-01-01",
        "registration_numbers": {
            "nino": "AB16A",
        },
        "address": {
            "name": None,
            "street": "street",
            "number": "1",
            "addition": None,
            "zip_code": "zipcode",
            "city": "city",
            "country": None,
        },
        "created_at": "2020-01-01",
        "bank_account": {
            "type": "account_number_sort_code",
            "account_number": "12345678",
            "sort_code": "01-01-01",
        },
        "custom_fields": {
            "payroll_employee_statement": [
                {
                    "id": 1,
                    "name": "name",
                }
            ],
            "payroll_student_loan_plan": [
                {
                    "id": 1,
                    "name": "name",
                }
            ],
            "payroll_postgrad_loan": [
                {
                    "id": 1,
                    "name": "name",
                }
            ],
        },
    }
    return mock


def test_get_valid_cp_employees(mock_user: Mock) -> None:
    # Arrange
    mock_employees = [
        {"id": 1, "name": "John Doe"},
        {"id": "1", "name": "Jane Smith"},
        {"id": 3, "name": "Alice Johnson"}
    ]

    mock_validated_employees = [
        MagicMock(spec=CPEmployee),
        None,
        MagicMock(spec=CPEmployee)
    ]

    with patch('api.v1.crewplanner.api.employee.CPEmployeeAPI.get_employees') as mock_get_employees:
        with patch('api.v1.crewplanner.employees.validate_employee') as mock_validate_employee:
            mock_get_employees.return_value.json.return_value = mock_employees
            mock_validate_employee.side_effect = mock_validated_employees

            # Act
            result = get_valid_cp_employees(mock_user)

            # Assert
            assert len(result) == len(mock_employees)
            assert result == mock_validated_employees


@pytest.mark.django_db(transaction=True)
def test_validate_employee_success(mock_user: Mock, mock_employee: dict) -> None:
    # Arrange
    mock_cp_employee = {
        "id": "123",
        "first_name": "John",
        "last_name": "Smith",
        "phone_number": None,
        "email": "john@smith.com",
        "profile_picture_url": None,
        "status": "active",
        "civil_status": "single",
        "gender": "male",
        "date_of_birth": "2000-01-01",
        "registration_numbers": {
            "nino": "AB123456A",
            "passport_number": None
        },
        "address": {
            "name": None,
            "street": "street",
            "number": "1",
            "addition": None,
            "zip_code": "zipcode",
            "city": "city",
            "country": None
        },
        "created_at": "2020-01-01",
        "bank_account": {
            "type": "account_number_sort_code",
            "account_number": "12345678",
            "sort_code": "01-01-01",
            "iban": None,
            "bic": None
        },
        "custom_fields": {
            "payroll_employee_statement": {
                "id": 1,
                "name": "name"
            },
            "payroll_student_loan_plan": {
                "id": 1,
                "name": "name"
            },
            "payroll_postgrad_loan": {
                "id": 1,
                "name": "name"
            },
            "payroll_start_date": None
        }
    }

    mock_cp_employee_instance = CPEmployee(**mock_cp_employee)

    with patch.object(InvalidEmployee, 'save') as mock_save:

        # Act
        with transaction.atomic():
            result = validate_employee(mock_user.stub, mock_employee)

        # Assert
        assert result == mock_cp_employee_instance
        mock_save.assert_not_called()


@pytest.mark.django_db(transaction=True)
def test_validate_employee_failure(mock_user: Mock, mock_invalid_employee: dict) -> None:
    # Arrange
    mock_employer = Employer()

    with patch('crewpay.models.Employer.objects.get') as mock_get_employer:
        mock_get_employer.return_value = mock_employer
        with patch.object(InvalidEmployee, 'save') as mock_save:

            # Act
            with transaction.atomic():
                result = validate_employee(mock_user.stub, mock_invalid_employee)

            # Assert
            assert result is None
            mock_save.assert_called_once()
