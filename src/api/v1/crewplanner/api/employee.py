import requests

from api.v1.crewplanner.api.base import CrewPlannerAPI


class CPEmployeeAPI(CrewPlannerAPI):
    def get_employees(self) -> requests.Response:
        """Get and validate CrewPlanner employees."""
        endpoint = "/employees"
        params = {"filter[status]": "verified", "filter[contract_types][]": ["VSA", "EMP"], "filter[payrolling]": "no"}
        return self._get(endpoint, params=params)
