import json
from typing import Optional

from pydantic import ValidationError

from api.v1.crewplanner.api.employee import CPEmployeeAPI
from api.v1.crewplanner.dto.dto_cp_employee import CPEmployee
from crewpay.models import CrewplannerUser, Employer, InvalidEmployee


def get_valid_cp_employees(user: CrewplannerUser) -> list[Optional[CPEmployee]]:
    """Get all CP employees and validates them for interfacing, returning a list of CPEmployees."""
    results = CPEmployeeAPI(user=user).get_employees()
    return [validate_employee(user.stub, employee) for employee in results.json()]


def validate_employee(stub: str, employee: dict) -> Optional[CPEmployee]:
    """Validates a CrewPlanner employee by checking for missing required fields. Saves the invalid employee creation
    attempt to the DB with the reason for failure."""
    try:
        # format custom fields
        for field in ["payroll_employee_statement", "payroll_student_loan_plan", "payroll_postgrad_loan"]:
            field_value = employee["custom_fields"].get(field, [])
            if isinstance(field_value, list) and len(field_value) > 0:
                employee["custom_fields"][field] = field_value[0]
            else:
                employee["custom_fields"][field] = None
        # transform to a CPEmployee object
        cp_employee = CPEmployee(**employee)
        return cp_employee
    # save validation errors for later
    except ValidationError as e:
        name = f"{employee['first_name']} {employee['last_name']}"
        invalid_employee = InvalidEmployee(
            employee_id=employee["id"],
            name=name,
            error=json.dumps(e.errors()),
            employer=Employer.objects.get(user__crewplanner_user__stub=stub),
        )
        invalid_employee.save()
        return None
