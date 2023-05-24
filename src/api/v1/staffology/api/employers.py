import json
from typing import Dict, List

from api.v1.staffology.api.base import StaffologyAPI


class StaffologyEmployerAPI(StaffologyAPI):
    """Handles all staffology employer api calls"""

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
