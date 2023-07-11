import os
from typing import Dict, Optional

import requests


class ShapeAPI:
    def __init__(self):
        self.base_url = f"https://{os.getenv('SHAPE_API_ENV')}.{os.getenv('SHAPE_API_HOST')}"
        self.api_secret = os.getenv("SHAPE_API_SECRET")
        self.api_id = os.getenv("SHAPE_API_ID")

    def _get_token(self):
        rsp = requests.post(
            f"{self.base_url}/oauth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.api_id,
                "client_secret": self.api_secret,
            },
        )
        if rsp.status_code != 200:
            raise Exception(f"Failed to login: {rsp.json()}")

        # Expires in
        expires_in = rsp.json()["expires_in"]

        # This is the bearer token to use in the auth header of secure requests
        return rsp.json()["access_token"]

    def _get_headers(self):
        return {"Authorization": f"Bearer {self._get_token()}"}

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        url = self.base_url + endpoint
        headers = self._get_headers()
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response

    def _post(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        url = self.base_url + endpoint
        headers = self._get_headers()
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response

    def _patch(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        url = self.base_url + endpoint
        headers = self._get_headers()
        response = requests.patch(url, json=data, headers=headers)
        response.raise_for_status()
        return response

    def _delete(self, endpoint: str) -> requests.Response:
        url = self.base_url + endpoint
        headers = self._get_headers()
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response
