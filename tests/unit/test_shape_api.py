from unittest.mock import MagicMock, patch

import pytest

from api.v1.shape.api.base import ShapeAPI


@pytest.fixture
def shape_api():
    return ShapeAPI()


def test_get_token_success(shape_api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'access_token': 'dummy_token',
        'expires_in': 3600
    }

    with patch('requests.post', return_value=mock_response):
        shape_api._get_token()

    assert shape_api.access_token == 'dummy_token'


def test_get_token_failure(shape_api):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {'error': 'Invalid credentials'}

    with patch('requests.post', return_value=mock_response):
        with pytest.raises(Exception):
            shape_api._get_token()


def test_get_headers(shape_api):
    shape_api.access_token = 'dummy_token'
    headers = shape_api._get_headers()
    assert headers == {'Authorization': 'Bearer dummy_token'}


def test_get_success(shape_api):
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response):
        response = shape_api._get('/endpoint')

    assert response.status_code == 200


def test_get_failure(shape_api):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = Exception('Not found')

    with patch('requests.get', return_value=mock_response):
        with pytest.raises(Exception):
            shape_api._get('/endpoint')


def test_post_success(shape_api):
    mock_response = MagicMock()
    mock_response.status_code = 201

    with patch('requests.post', return_value=mock_response) as mock_post:
        response = shape_api._post('/endpoint', data={'key': 'value'})

    assert response.status_code == 201
    mock_post.assert_called_once_with(
        shape_api.base_url + '/endpoint',
        json={'key': 'value'},
        headers=shape_api._get_headers()
    )


def test_post_failure(shape_api):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = Exception('Server error')

    with patch('requests.post', return_value=mock_response):
        with pytest.raises(Exception):
            shape_api._post('/endpoint', data={'key': 'value'})


def test_patch_success(shape_api):
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch('requests.patch', return_value=mock_response) as mock_patch:
        response = shape_api._patch('/endpoint', data={'key': 'value'})

    assert response.status_code == 200
    mock_patch.assert_called_once_with(
        shape_api.base_url + '/endpoint',
        json={'key': 'value'},
        headers=shape_api._get_headers()
    )


def test_patch_failure(shape_api):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = Exception('Not found')

    with patch('requests.patch', return_value=mock_response):
        with pytest.raises(Exception):
            shape_api._patch('/endpoint', data={'key': 'value'})


def test_delete_success(shape_api):
    mock_response = MagicMock()
    mock_response.status_code = 204

    with patch('requests.delete', return_value=mock_response) as mock_delete:
        response = shape_api._delete('/endpoint')

    assert response.status_code == 204
    mock_delete.assert_called_once_with(
        shape_api.base_url + '/endpoint',
        headers=shape_api._get_headers()
    )


def test_delete_failure(shape_api):
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = Exception('Forbidden')

    with patch('requests.delete', return_value=mock_response):
        with pytest.raises(Exception):
            shape_api._delete('/endpoint')
