from unittest.mock import MagicMock, Mock, patch

import pytest

from api.v1.crewplanner.api.base import CrewPlannerAPI


@pytest.fixture
def mock_user() -> Mock:
    user = MagicMock()
    user.stub = "example-stub"
    user.access_key = "example-access-key"
    return user


@pytest.fixture
def fixture_crewplanner_api(mock_user: Mock) -> CrewPlannerAPI:
    return CrewPlannerAPI(mock_user)


def test_get_success(fixture_crewplanner_api: CrewPlannerAPI) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response):
        response = fixture_crewplanner_api._get('/endpoint')

    assert response.status_code == 200


def test_get_failure(fixture_crewplanner_api: CrewPlannerAPI) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = Exception('Not found')

    with patch('requests.get', return_value=mock_response):
        with pytest.raises(Exception):
            fixture_crewplanner_api._get('/endpoint')

