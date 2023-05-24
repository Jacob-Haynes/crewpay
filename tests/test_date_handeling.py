from unittest.mock import patch, Mock

import pytest

from api.v1.crewplanner.dto_cp_ShiftsByUser import CPShiftsByUser
from api.v1.staffology.date_handeling import compute_report_dates
from api.v1.staffology.dto_so_pay_options_import import PayLine, Line
from api.v1.staffology.pay_line import create_pay_line


@patch("api.v1.staffology.pay_line.Employee")
def test_create_pay_line(mock_employee: Mock):
    # Mock
    mock_employee.objects.get.return_value.payroll_code = "EMP123"
    # Arrange
    user_shifts = CPShiftsByUser(
        user_id=123,
        shifts=[
            {
                "id": 1,
                "date": "2023-01-01",
                "start_time": "09:00",
                "end_time": "11:00",
                "present": "true",
                "slot": {
                    "id": 1,
                    "department": {
                        "id": 1
                    },
                    "function": {
                        "id": 1,
                        "name": "Waiter"
                    }
                },
                "wage": {
                    "type": "hourly",
                    "total": 10.0,
                    "value": 15.0
                },
                "timesheet": {
                    "planned": {
                        "start": "09:00",
                        "end": "11:00",
                        "minutes": 120
                    },
                    "registered": {
                        "start": "09:00",
                        "end": "11:00",
                        "gross_minutes": 120,
                        "netto_minutes": 120
                    }
                },
                "worker": {
                    "id": 1,
                    "name": "John Smith",
                    "contract_type": "EMP",
                    "user": {
                        "id": 1,
                        "first_name": "John",
                        "last_name": "Smith",
                        "email": "john@smith.com",
                        "date_of_birth": "2000-01-01"
                    }
                },
                "project": {
                    "id": 1,
                    "name": "Project A",
                    "date": "2023-01-01",
                    "company": {
                        "id": 1,
                        "name": "Company A"
                    }
                }
            },
            # Add more shifts if needed
        ]
    )

    expected_payline = PayLine(
        payrollCode="EMP123",
        lines=[
            Line(
                value=10.0,
                rate=15.0,
                multiplier=2.0,
                description="2023-01-01 - Company A - Project A",
                code="BASICHOURLY"
            )
            # Add more expected lines if needed
        ]
    )

    # Act
    actual_payline = create_pay_line(user_shifts)

    # Assert
    assert actual_payline == expected_payline

    # Additional assertion for specific fields
    assert actual_payline.payrollCode == "EMP123"
    assert len(actual_payline.lines) == len(expected_payline.lines)


@pytest.mark.parametrize("payrun_start_date, payrun_end_date, pay_period, arrears, expected_start, expected_end",
                         [("2023-01-01", "2023-01-31", "Monthly", 1, "2022-12-01", "2022-12-31"),
                          ("2023-01-01", "2023-01-31", "Monthly", 2, "2022-11-01", "2022-11-30"),
                          ("2023-01-01", "2023-01-31", "Monthly", 3, "2022-10-01", "2022-10-31"),
                          ("2023-04-01", "2023-04-30", "Monthly", 1, "2023-03-01", "2023-03-31"),
                          ("2023-04-01", "2023-04-30", "Monthly", 2, "2023-02-01", "2023-02-28"),
                          ("2023-04-01", "2023-04-30", "Monthly", 3, "2023-01-01", "2023-01-31"),
                          ("2023-01-01", "2023-01-07", "Weekly", 1, "2022-12-25", "2022-12-31"),
                          ("2023-01-01", "2023-01-14", "Fortnightly", 1, "2022-12-18", "2022-12-31"),
                          ("2023-01-01", "2023-01-14", "Fortnightly", 2, "2022-12-04", "2022-12-17"),
                          ("2023-01-01", "2023-01-02", "Daily", 1, "2022-12-31", "2023-01-01"),
                          ("2023-01-01", "2023-01-02", "Daily", 2, "2022-12-30", "2022-12-31"),
                          ("2023-01-01", "2023-01-02", "Daily", 3, "2022-12-29", "2022-12-30"),
                          ("2024-02-01", "2024-02-29", "Monthly", 1, "2024-01-01", "2024-01-31"),
                          ("2024-02-01", "2024-02-29", "Monthly", 2, "2023-12-01", "2023-12-31"),
                          ("2024-02-01", "2024-02-29", "Monthly", 3, "2023-11-01", "2023-11-30"),
                          ("2023-01-01", "2023-01-31", "Monthly", 0, "2023-01-01", "2023-01-31"),
                          ("2023-04-01", "2023-04-30", "Monthly", 0, "2023-04-01", "2023-04-30"),
                          ("2023-02-01", "2023-02-28", "Monthly", 0, "2023-02-01", "2023-02-28"),
                          ("2023-01-01", "2023-01-07", "Weekly", 0, "2023-01-01", "2023-01-07"),
                          ("2023-01-01", "2023-01-14", "Fortnightly", 0, "2023-01-01", "2023-01-14"),
                          ("2023-01-01", "2023-01-02", "Daily", 0, "2023-01-01", "2023-01-02"),
                          ("2024-02-01", "2024-02-29", "Monthly", 0, "2024-02-01", "2024-02-29"),
                          ("2023-01-01", "2023-01-07", "Weekly", 2, "2022-12-18", "2022-12-24"),
                          ("2023-01-01", "2023-01-07", "Weekly", 3, "2022-12-11", "2022-12-17"),
                          ("2023-04-01", "2023-04-07", "Weekly", 2, "2023-03-18", "2023-03-24"),
                          ("2023-04-01", "2023-04-07", "Weekly", 3, "2023-03-11", "2023-03-17"),
                          ("2023-02-01", "2023-02-07", "Weekly", 2, "2023-01-18", "2023-01-24"),
                          ],
                         ids=["over year boundary with monthly period",
                              "over year boundary 2 month arrears",
                              "over year boundary 3 month arrears",
                              "30th to 31st month end, 1 month arrears",
                              "30th to feb 28th",
                              "30th over feb 28th",
                              "weekly, 1 arrears",
                              "fortnightly, 1 arrears",
                              "fortnightly, 2 arrears",
                              "daily, 1 arrears",
                              "daily, 2 arrears",
                              "daily, 3 arrears",
                              "leap year, 1 month arrears",
                              "leap year, 2 month arrears",
                              "leap year, 3 month arrears",
                              "monthly, 0 arrears - case 1",
                              "monthly, 0 arrears - case 2",
                              "monthly, 0 arrears - case 3",
                              "weekly, 0 arrears",
                              "fortnightly, 0 arrears",
                              "daily, 0 arrears",
                              "leap year, 0 arrears",
                              "weekly, 2 arrears - case 1",
                              "weekly, 3 arrears - case 1",
                              "weekly, 2 arrears - case 2",
                              "weekly, 3 arrears - case 2",
                              "weekly, 2 arrears - case 3",
                              ])
def test_compute_report_dates(payrun_start_date, payrun_end_date, pay_period, arrears, expected_start, expected_end):
    # Act
    earnings_period_start, earnings_period_end = compute_report_dates(payrun_start_date, payrun_end_date, pay_period,
                                                                      arrears)
    # Asset
    assert earnings_period_start == expected_start
    assert earnings_period_end == expected_end
