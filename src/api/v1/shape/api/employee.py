from typing import Dict, Optional

import requests

from api.v1.shape.api.base import ShapeAPI


class EmployeeAPI(ShapeAPI):
    def list_employees(self, company_id: Optional[str] = None) -> requests.Response:
        """Returns a list of employees"""
        endpoint = "/employee"
        params = {"companyId": company_id} if company_id else None
        return self._get(endpoint, params=params)

    # Not needed as Patch method exists
    # def create_employee(self, employee_data: Dict) -> requests.Response:
    #     """Creates a new employee in a company"""
    #     endpoint = "/employee"
    #     return self._post(endpoint, data=employee_data)

    def patch_employee(self, employee_data: Dict) -> requests.Response:
        """Creates a new, or partial updates an existing employee.
        Existing employees are matched using rules in spec:
        A company must be included
        If an employee.employeeCode is included it will match on employeeCode
        If an employee.payId is set it will match on payId
        If employee.IncludeLeavers is not set, employees with a P45 will not be matched, if set to true they will be.
        If an existing employee is found any values set in employee will overwrite the existing values.

        If no employee is found, a new record is created using the values is employee. If starter is set, those values
        will be run through the starter process setting the tax code, starter declaration etc.

        When using employeeCode identification, the system will generate a unique payId for any new employees created"""
        endpoint = "/employee"
        return self._patch(endpoint, data=employee_data)

    def get_employee(self, employee_id: str) -> requests.Response:
        """Gets an employee"""
        endpoint = f"/employee/{employee_id}"
        return self._get(endpoint)

    # Not needed as Patch method exists
    # def update_employee(self, employee_id: str, employee_data: Dict) -> requests.Response:
    #     """Updates an employee, all fields are optional, only sent fields will be updated"""
    #     endpoint = f"/employee/{employee_id}"
    #     return self._post(endpoint, data=employee_data)

    def delete_employee(self, employee_id: str) -> requests.Response:
        """Deletes an employee"""
        endpoint = f"/employee/{employee_id}"
        return self._delete(endpoint)

    # Not needed as Patch method exists
    # def starter_employee(self, employee_id: str, starter_data: Dict) -> requests.Response:
    #     """Mark the employee as a starter and set appropriate tax code and starer declaration."""
    #     endpoint = f"/employee/{employee_id}/starter"
    #     return self._post(endpoint, data=starter_data)

    # Not needed as Patch method exists
    # def migrated_employee(self, employee_id: str, migration_data: Dict) -> requests.Response:
    #     """Mark the employee as a migrated from another system. No starter info will be sent to HMRC."""
    #     endpoint = f"/employee/{employee_id}/migrated"
    #     return self._post(endpoint, data=migration_data)
