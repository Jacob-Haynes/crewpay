import json
from typing import Optional, Dict, List
from datetime import datetime as dt
import requests

from api.v1.staffology.dto_so_employee import StaffologyEmployee
from crewpay.models import StaffologyUser


class StaffologyEmployeeAPI:
    """Handles all staffology employee api calls"""

    def __init__(self, admin_user: str = "admin"):
        self.base_url = "https://api.staffology.co.uk/"
        self.admin_user = admin_user
        self.headers = {"content-type": "text/json"}
        access_key = StaffologyUser.objects.get(user__username=admin_user).staffology_key
        self.auth = ("username", access_key)

    def get(self, endpoint: str) -> requests.Response:
        response = requests.get(
            f"{self.base_url}{endpoint}",
            auth=self.auth,
            headers=self.headers,
        )
        if not response.ok:
            raise ValueError(response.text)
        return response

    def post(self, endpoint: str, data: str) -> requests.Response:
        response = requests.post(
            f"{self.base_url}{endpoint}",
            auth=self.auth,
            data=data,
            headers=self.headers,
        )
        if not response.ok:
            raise ValueError(response.text)
        return response

    def put(self, endpoint: str, data: str, params: Optional[Dict] = None) -> requests.Response:
        response = requests.put(
            f"{self.base_url}{endpoint}", auth=self.auth, data=data, headers=self.headers, params=params
        )
        if not response.ok:
            raise ValueError(response.text)
        return response

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

    def delete_employees(self, employer: str, employees: List[str]) -> None:
        self.post(f"/employers/{employer}/employees/delete", data=json.dumps(employees))

    def update_employees(self, employer: str, employee_id: str, employee: StaffologyEmployee) -> None:
        self.put(f"/employers/{employer}/employees/{employee_id}", data=employee.json()).json()
