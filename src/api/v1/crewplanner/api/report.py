import requests

from api.v1.crewplanner.api.base import CrewPlannerAPI


class CPReportAPI(CrewPlannerAPI):
    def get_report(self, start_date: str, end_date: str) -> requests.Response:
        """Gets reports from the CrewPlanner API"""
        endpoint = "/report"
        params = {
            "filter[after]": start_date,
            "filter[before]": end_date,
            "filter[include_external_workers]": "false",
            "filter[contract_types]": ["VSA", "EMP"],
        }
        return self._get(endpoint, params=params)
