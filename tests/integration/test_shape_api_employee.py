from typing import Any

import pytest

from api.v1.shape.api.employee import ShapeEmployeeAPI


@pytest.fixture
def fixture_example_employee() -> dict[str, Any]:
    return {'addressCity': '',
            'addressCountry': '',
            'addressLine1': '',
            'addressLine2': '',
            'addressLine3': '',
            'addressPostcode': '',
            'bankAccountName': '',
            'bankAccountNumber': '',
            'bankName': '',
            'bankSortCode': '',
            'company': {'id': 'c_TrDoQRg4JbyBiAmYSUfXHi',
                        'identity': 'c_TrDoQRg4JbyBiAmYSUfXHi',
                        'name': 'Integration Test Company'},
            'dateBecameDirector': None,
            'dateOfBirth': None,
            'departmentCode': '',
            'directorNiType': None,
            'email': '',
            'employeeCode': '',
            'firstCivilianEmploymentDate': None,
            'firstName': 'Integration',
            'gender': None,
            'hasInvitation': False,
            'hasP45': False,
            'hasPayslipPassword': False,
            'hasUser': False,
            'id': 'ee_YNaNnaw2sEqoDJLXQdx55G',
            'irregularPayments': True,
            'isDirector': False,
            'isMigrated': True,
            'isVeteran': False,
            'lastName': 'Employee',
            'leavingDate': None,
            'leavingRtiId': None,
            'middleName': 'Test',
            'mobile': None,
            'niCode': 'A',
            'niCodeXIsValid': False,
            'niNumber': '',
            'offPayrollWorker': False,
            'p60Years': [],
            'payBehaviour': 'manual',
            'payFrequency': 'W2',
            'payId': '1',
            'payslipNote': None,
            'phone': None,
            'postGraduateLoanType': None,
            'previousEmploymentGross': 0.0,
            'previousEmploymentLeavingDate': None,
            'previousEmploymentTax': 0.0,
            'previousPayId': None,
            'regularHours': 'other',
            'reportPayIdChanged': True,
            'startDate': None,
            'starterDeclaration': None,
            'studentLoanType': None,
            'taxCode': '257L',
            'title': 'Mr',
            'w1m1': False,
            'workReference': '1'}


@pytest.fixture
def fixture_example_list(fixture_example_employee: dict[str, Any]) -> dict[str, Any]:
    return {
        'itemCount': 1,
        'items': [
            fixture_example_employee
                  ],
        'page': 1,
        'pageCount': 1,
        'pageSize': 100
    }


@pytest.fixture
def fixture_employee_spec() -> dict[str, dict[str, str]]:
    return {
        "company": {
            "companyId": "c_TrDoQRg4JbyBiAmYSUfXHi"
        },
        "employee": {
            "employeeCode": "123456",
        }
    }


def test_patch_new_employee(fixture_employee_spec: dict) -> None:
    # Arrange
    # Employee is matched using CrewPlanner ID "employeeCode"
    new_employee = {
        "spec": fixture_employee_spec,
        "employee": {
            "firstName": "John",
            "lastName": "Smith",
            "gender": "male",
            "dateOfBirth": "1970-01-01",
            "niNumber": "AB123456A",
            "employeeCode": "123456",
            "studentLoanType": "none",
            "postgraduateLoanType": "none",
            "startDate": "1970-01-01",
            "starterDeclaration": "A",
            "email": "johnsmith@test.com",
            "phone": "07123456789",
            "addressLine1": "string",
            "addressLine2": "string",
            "addressLine3": "string",
            "addressCity": "string",
            "addressPostcode": "string",
            "addressCountry": "string",
            "bankSortCode": "01-01-01",
            "bankAccountNumber": "01234567",
        },
    }
    expected_data = {
        "action": "created",
        "employeeCode": "123456"
    }
    expected_status_code = 200

    # Act
    actual = ShapeEmployeeAPI().patch_employee(new_employee)
    actual_data = actual.json()
    actual_employee_id = actual_data.pop('employeeId')
    actual_pay_id = actual_data.pop('payId')

    # Assert
    assert actual.status_code == expected_status_code
    assert actual_data == expected_data
    assert isinstance(actual_employee_id, str)
    assert isinstance(actual_pay_id, str)


def test_patch_employee_update(fixture_employee_spec: dict) -> None:
    # Arrange
    update_employee = {
        "spec": fixture_employee_spec,
        "employee": {
            "addressLine1": "21 fenchurch street",
            "addressLine2": "",
            "addressLine3": "",
            "addressCity": "London",
            "addressPostcode": "EC3M 4BS",
            "addressCountry": "UK",
        },
    }
    expected_data = {
        "action": "updated",
        "employeeCode": "123456"
    }
    expected_status_code = 200

    # Act
    actual = ShapeEmployeeAPI().patch_employee(update_employee)
    actual_data = actual.json()
    actual_employee_id = actual_data.pop('employeeId')
    actual_pay_id = actual_data.pop('payId')

    # Assert
    assert actual.status_code == expected_status_code
    assert actual_data == expected_data
    assert isinstance(actual_employee_id, str)
    assert isinstance(actual_pay_id, str)

    # Cleanup & test Delete function
    delete_actual = ShapeEmployeeAPI().delete_employee(actual_employee_id)
    assert delete_actual.status_code == expected_status_code
    assert delete_actual.json() == {}


def test_get_employee(fixture_example_employee: dict) -> None:
    # Arrange
    employee_id = "ee_YNaNnaw2sEqoDJLXQdx55G"
    expected_data = fixture_example_employee
    expected_status_code = 200

    # Act
    actual = ShapeEmployeeAPI().get_employee(employee_id)

    # Assert
    assert actual.status_code == expected_status_code
    assert actual.json() == expected_data


def test_list_employees(fixture_example_list: dict) -> None:
    # Arrange
    company_id = "c_TrDoQRg4JbyBiAmYSUfXHi"
    expected_data = fixture_example_list
    expected_status_code = 200

    # Act
    actual = ShapeEmployeeAPI().list_employees(company_id)

    # Assert
    assert actual.status_code == expected_status_code
    assert actual.json() == expected_data
