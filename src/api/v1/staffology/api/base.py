from typing import Dict, Optional

import requests

from crewpay.models import StaffologyUser


class StaffologyAPI:
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
