from http import HTTPStatus

from fastapi.testclient import TestClient

from slotlock.app import app


def test_health_returns_ok():
    with TestClient(app) as client:
        response = client.get('/health')

    assert response.status_code == HTTPStatus.OK
    assert response.headers['content-type'] == 'application/json'
    assert response.json() == {'status': 'ok'}
