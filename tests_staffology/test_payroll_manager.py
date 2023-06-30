from unittest.mock import Mock, patch

import pytest

from api.v1.staffology.payroll.payroll_manager import PayrollManager


@pytest.fixture
def payroll_manager():
    payroll_manager = PayrollManager("employer", "tax_year", 0)
    return payroll_manager


@patch("api.v1.staffology.payroll_manager.update_employer_db")
@patch("api.v1.staffology.payroll_manager.Employer")
def test_update_employer(mock_employer: Mock, mock_update_employer_db: Mock, payroll_manager):
    # Act
    payroll_manager.update_employer()
    # Assert
    assert payroll_manager.employer_instance is not None
    assert payroll_manager.user is not None
    assert payroll_manager.pay_period is not None
    mock_update_employer_db.assert_called_once_with(payroll_manager.employer)


def test_get_pay_schedule(payroll_manager):
    with pytest.raises(ValueError):
        payroll_manager.get_pay_schedule()


#TODO: def test_activate_pay_runs():

#TODO: def test_get_full_pay_run():

#TODO: def test_compute_report_dates():

#TODO: def test_create_shift_lines():

#TODO: def test_group_shifts_by_user():

#TODO: def test_create_pay_lines():

#TODO: def test_import_pay_lines():

#TODO: def test_get_failed_imports():

#TODO: def test_process_payroll():


