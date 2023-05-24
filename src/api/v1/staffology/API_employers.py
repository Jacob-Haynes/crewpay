import json
from typing import Optional, Dict, List

import requests

from crewpay.models import StaffologyUser


class StaffologyEmployerAPI:
    """Handles all staffology employer api calls"""

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

    def post(self, endpoint: str, data: Optional[str] = None) -> requests.Response:
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

    def delete(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        response = requests.delete(f"{self.base_url}{endpoint}", auth=self.auth, headers=self.headers, params=params)
        if not response.ok:
            raise ValueError(response.text)
        return response

    def update_pay_schedule(self, employer: str, tax_year: str, pay_period: str, payload) -> None:
        self.put(f"/employers/{employer}/schedules/{tax_year}/{pay_period}/1", data=json.dumps(payload))

    def create_employer(self, payload: Dict) -> Dict:
        return self.post("/employers", data=json.dumps(payload)).json()

    def get_pay_schedules(self, employer: str, tax_year: str) -> List[Dict]:
        return self.get(f"/employers/{employer}/schedules/{tax_year}").json()

    def get_pay_schedule(self, employer: str, tax_year: str, pay_period: str) -> Dict:
        return self.get(f"/employers/{employer}/schedules/{tax_year}/{pay_period}/1").json()

    def get_pay_run(self, employer: str, tax_year: str, pay_period: str, period: int) -> Dict:
        return self.get(f"/employers/{employer}/payrun/{tax_year}/{pay_period}/{period}").json()

    def start_next_payrun(self, employer: str, tax_year: str, pay_period: str) -> None:
        self.post(f"/employers/{employer}/payrun/{tax_year}/{pay_period}")

    def delete_pay_run(self, employer: str, tax_year: str, pay_period: str, period: int) -> None:
        self.delete(f"/employers/{employer}/payrun/{tax_year}/{pay_period}/{period}")

    def update_pay_run(self, employer: str, tax_year: str, pay_period: str, period: int) -> Dict:
        return self.put(f"/employers/{employer}/payrun/{tax_year}/{pay_period}/{period}").json()

    def import_pay(self, employer: str, pay_period: str, payload: List[Dict]) -> None:
        self.post(f"/employers/{employer}/payrun/{pay_period}/importpay?linesOnly=true", data=json.dumps(payload))

    def get_employer(self, employer: str) -> Dict:
        return self.get(f"/employers/{employer}").json()
