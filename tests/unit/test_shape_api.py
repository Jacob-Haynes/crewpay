from unittest.mock import MagicMock, Mock, patch

import pytest

from api.v1.shape.api.base import ShapeAPI


@pytest.fixture
def fixture_shape_api() -> ShapeAPI:
    return ShapeAPI()


def test_get_token_success(fixture_shape_api: ShapeAPI) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'access_token': 'dummy_token',
        'expires_in': 3600
    }

    with patch('requests.post', return_value=mock_response):
        access_token = fixture_shape_api._get_token()

    assert access_token == 'dummy_token'


def test_get_token_failure(fixture_shape_api: ShapeAPI) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {'error': 'Invalid credentials'}

    with patch('requests.post', return_value=mock_response):
        with pytest.raises(Exception):
            fixture_shape_api._get_token()


@patch.object(ShapeAPI, "_get_token")
def test_get_headers(mock_get_token: Mock, fixture_shape_api: ShapeAPI) -> None:
    mock_get_token.return_value = 'dummy_token'
    headers = fixture_shape_api._get_headers()
    assert headers == {'Authorization': 'Bearer dummy_token'}


def test_get_success(fixture_shape_api: ShapeAPI) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response):
        response = fixture_shape_api._get('/endpoint')

    assert response.status_code == 200


def test_get_failure(fixture_shape_api: ShapeAPI) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = Exception('Not found')

    with patch('requests.get', return_value=mock_response):
        with pytest.raises(Exception):
            fixture_shape_api._get('/endpoint')


@patch.object(ShapeAPI, "_get_headers")
def test_post_success(mock_get_headers: Mock, fixture_shape_api: ShapeAPI) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    expected_headers = {}
    mock_get_headers.return_value = expected_headers

    with patch('requests.post', return_value=mock_response) as mock_post:
        response = fixture_shape_api._post('/endpoint', data={'key': 'value'})

    assert response.status_code == 200
    mock_post.assert_called_once_with(
        fixture_shape_api.base_url + '/endpoint',
        json={'key': 'value'},
        headers=expected_headers,
        timeout=60
    )


def test_post_failure(fixture_shape_api: ShapeAPI) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = Exception('Server error')

    with patch('requests.post', return_value=mock_response):
        with pytest.raises(Exception):
            fixture_shape_api._post('/endpoint', data={'key': 'value'})


@patch.object(ShapeAPI, "_get_headers")
def test_patch_success(mock_get_headers: Mock, fixture_shape_api: ShapeAPI) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    expected_headers = {}
    mock_get_headers.return_value = expected_headers

    with patch('requests.patch', return_value=mock_response) as mock_patch:
        response = fixture_shape_api._patch('/endpoint', data={'key': 'value'})

    assert response.status_code == 200
    mock_patch.assert_called_once_with(
        fixture_shape_api.base_url + '/endpoint',
        json={'key': 'value'},
        headers=expected_headers,
        timeout=60
    )


def test_patch_failure(fixture_shape_api: ShapeAPI) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = Exception('Not found')

    with patch('requests.patch', return_value=mock_response):
        with pytest.raises(Exception):
            fixture_shape_api._patch('/endpoint', data={'key': 'value'})


@patch.object(ShapeAPI, "_get_headers")
def test_delete_success(mock_get_headers: Mock, fixture_shape_api: ShapeAPI) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 204
    expected_headers = {}
    mock_get_headers.return_value = expected_headers

    with patch('requests.delete', return_value=mock_response) as mock_delete:
        response = fixture_shape_api._delete('/endpoint')

    assert response.status_code == 204
    mock_delete.assert_called_once_with(
        fixture_shape_api.base_url + '/endpoint',
        headers=expected_headers,
        timeout=60
    )


def test_delete_failure(fixture_shape_api: ShapeAPI) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = Exception('Forbidden')

    with patch('requests.delete', return_value=mock_response):
        with pytest.raises(Exception):
            fixture_shape_api._delete('/endpoint')
