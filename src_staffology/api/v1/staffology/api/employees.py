import json
from datetime import datetime as dt
from typing import Dict, List

from api.v1.staffology.api.base import StaffologyAPI
from api.v1.staffology.dto.dto_so_employee import StaffologyEmployee
from api.v1.staffology.dto.dto_so_employee_full import StaffologyEmployeeFull


class StaffologyEmployeeAPI(StaffologyAPI):
    """Handles all staffology employee api calls"""

    def employee_create(self, employer: str, employee: StaffologyEmployee) -> Dict:
        return self.post(f"employers/{employer}/employees", data=employee.json()).json()

    def mark_leavers(self, employer: str, employees: List[str]) -> None:
        now = dt.today()
        params = {"date": now.strftime("%Y-%m-%d"), "emailP45": json.dumps(False)}
        self.put(f"employers/{employer}/employees/leavers", data=json.dumps(employees), params=params)

    def mark_rehires(self, employer: str, employee: str) -> Dict:
        return self.get(f"/employers/{employer}/employees/{employee}/rehire").json()

    def staffology_employees_get(self, employer: str) -> List[Dict]:
        return self.get(f"employers/{employer}/employees").json()

    def staffology_employee_get(self, employer: str, employee: str) -> Dict:
        return self.get(f"employers/{employer}/employees/{employee}").json()

    def delete_employees(self, employer: str, employees: List[str]) -> None:
        self.post(f"/employers/{employer}/employees/delete", data=json.dumps(employees))

    def update_employees(self, employer: str, employee_id: str, employee: StaffologyEmployeeFull) -> None:
        self.put(f"/employers/{employer}/employees/{employee_id}", data=employee.json(exclude_unset=True)).json()
