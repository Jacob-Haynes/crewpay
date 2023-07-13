import json

import requests

from crewpay.models import CrewplannerUser


class CrewPlannerAPI:
    def __init__(self, user: CrewplannerUser) -> None:
        self.stub = user.stub
        self.access_key = user.access_key

    def _get(self, endpoint: str, params: dict = None) -> requests.Response:
        """Performs a GET request to the CrewPlanner API."""
        url = f"https://{self.stub}.crewplanner.com/api/v1/client{endpoint}"
        headers = {"Authorization": f"Bearer {self.access_key}"}
        combined_response = []

        while True:
            response = requests.get(url, params=params, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            combined_response.extend(data["data"])

            # Check for next page
            if "links" in data and "next" in data["links"] and data["links"]["next"]:
                url = data["links"]["next"]
            else:
                break

        response = requests.Response()
        response._content = json.dumps(combined_response).encode("utf-8")
        response.status_code = 200
        return response
