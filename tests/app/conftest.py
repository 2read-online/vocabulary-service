# pylint: skip-file
import json
import pytest
from bson import ObjectId
from fastapi_jwt_auth import AuthJWT
from pymongo.collection import Collection
from starlette.testclient import TestClient
from typing import Dict
from unittest.mock import Mock

texts = Mock(spec=Collection)


@pytest.fixture
def mock_translations(mocker):
    mock = mocker.patch('app.db.get_translation_collection')
    mock.return_value = texts
    return mock.return_value


@pytest.fixture
def client(mock_translations, mock_post):
    from app.main import app
    return TestClient(app)


@pytest.fixture
def user_id() -> ObjectId:
    return ObjectId('60c0b2d700569d97f8a93dcd')


@pytest.fixture
def token(user_id: ObjectId) -> str:
    auth = AuthJWT()
    return auth.create_access_token(subject=str(user_id))


@pytest.fixture
def headers(token: str) -> Dict[str, str]:
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def mock_post(mocker):
    mock = mocker.patch('requests.post')
    return mock


def get_detail(content: str) -> str:
    return json.loads(content)['detail']
