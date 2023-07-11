import os
from typing import Optional

import requests


class ShapeAPI:
    def __init__(self) -> None:
        self.base_url = f"https://{os.getenv('SHAPE_API_ENV')}.{os.getenv('SHAPE_API_HOST')}"
        self.api_secret = os.getenv("SHAPE_API_SECRET")
        self.api_id = os.getenv("SHAPE_API_ID")

    def _get_token(self) -> str:
        rsp = requests.post(
            f"{self.base_url}/oauth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.api_id,
                "client_secret": self.api_secret,
            },
            timeout=60,
        )
        if rsp.status_code != 200:
            raise ValueError(f"Failed to login: {rsp.json()}")

        # Expires in
        # expires_in = rsp.json()["expires_in"]

        # This is the bearer token to use in the auth header of secure requests
        access_token: str = rsp.json()["access_token"]
        return access_token

    def _get_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._get_token()}"}

    def _get(self, endpoint: str, params: Optional[dict] = None) -> requests.Response:
        url = self.base_url + endpoint
        headers = self._get_headers()
        response = requests.get(url, params=params, headers=headers, timeout=60)
        response.raise_for_status()
        return response

    def _post(self, endpoint: str, data: Optional[dict] = None) -> requests.Response:
        url = self.base_url + endpoint
        headers = self._get_headers()
        response = requests.post(url, json=data, headers=headers, timeout=60)
        response.raise_for_status()
        return response

    def _patch(self, endpoint: str, data: Optional[dict] = None) -> requests.Response:
        url = self.base_url + endpoint
        headers = self._get_headers()
        response = requests.patch(url, json=data, headers=headers, timeout=60)
        response.raise_for_status()
        return response

    def _delete(self, endpoint: str) -> requests.Response:
        url = self.base_url + endpoint
        headers = self._get_headers()
        response = requests.delete(url, headers=headers, timeout=60)
        response.raise_for_status()
        return response
