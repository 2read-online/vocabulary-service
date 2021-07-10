"""Test save translation request"""
# pylint: disable=redefined-outer-name
import pytest
from bson import ObjectId

from app.db.vocabulary import VocabularyEntry
from app.schemas import SaveRequest
from tests.main.conftest import get_detail


@pytest.fixture
def valid_request() -> SaveRequest:
    """Valid HTTP request"""
    return SaveRequest(
        translationId=str(ObjectId())
    )


def test__save_ok(client, headers, valid_request, mock_vocabulary, user_id):
    """Should save a translation in vocabulary"""
    resp = client.post('/vocab/save', valid_request.json(by_alias=True), headers=headers)

    assert resp.status_code == 200
    entry = VocabularyEntry(translationId=valid_request.translation_id, ownerId=user_id)
    mock_vocabulary.insert_one.assert_called_with(entry.db(), entry.db())


def test__save_no_jwt(client, valid_request):
    """Should check access token"""
    resp = client.post('/vocab/save', valid_request.json(by_alias=True))

    assert resp.status_code == 401
    assert get_detail(resp.content) == "Missing Authorization Header"
