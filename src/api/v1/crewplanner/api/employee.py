import requests

from api.v1.crewplanner.api.base import CrewPlannerAPI


class CPEmployeeAPI(CrewPlannerAPI):
    def get_employees(self) -> requests.Response:
        """Get and validate CrewPlanner employees."""
        endpoint = "/employees"
        params = {"filter[status]": "verified", "filter[contract_types][]": ["VSA", "EMP"], "filter[payrolling]": "no"}
        return self._get(endpoint, params=params)

    # def get_employees(self) -> list[Optional[CPEmployee]]:
    #     """Get and validate CrewPlanner employees."""
    #     results = self._get(
    #         "employees",
    #         {"filter[status]": "verified", "filter[contract_types][]": ["VSA", "EMP"], "filter[payrolling]": "no"},
    #     )
    #     return [self.validate_employee(employee) for employee in results.json()]
    #
    # def validate_employee(self, employee: dict) -> Optional[CPEmployee]:
    #     """Validates a CrewPlanner employee by checking for missing required fields. Saves the invalid employee creation
    #     attempt to the DB with the reason for failure."""
    #     try:
    #         for field in ["payroll_employee_statement", "payroll_student_loan_plan", "payroll_postgrad_loan"]:
    #             field_value = employee["custom_fields"].get(field, [])
    #             if isinstance(field_value, list) and len(field_value) > 0:
    #                 employee["custom_fields"][field] = field_value[0]
    #             else:
    #                 employee["custom_fields"][field] = None
    #         cp_employee = CPEmployee(**employee)
    #         return cp_employee
    #     except ValidationError as e:
    #         name = f"{employee['first_name']} {employee['last_name']}"
    #         invalid_employee = InvalidEmployee(
    #             employee_id=employee["id"],
    #             name=name,
    #             error=json.dumps(e.errors()),
    #             employer=Employer.objects.get(user__crewplanner_user__stub=self.stub),
    #         )
    #         invalid_employee.save()
    #         return None
