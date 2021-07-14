"""Test remove translation request"""
# pylint: disable=redefined-outer-name
import pytest
from bson import ObjectId

from app.db.vocabulary import VocabularyEntry
from app.schemas import RemoveRequest
from tests.main.conftest import get_detail


@pytest.fixture
def valid_request() -> RemoveRequest:
    """Valid HTTP request"""
    return RemoveRequest(
        translationId=str(ObjectId())
    )


def test__remove_ok(client, headers, valid_request, mock_vocabulary, user_id):
    """Should remove a translation in vocabulary"""
    resp = client.post('/vocab/remove', valid_request.json(by_alias=True), headers=headers)

    assert resp.status_code == 200
    entry = VocabularyEntry(translationId=valid_request.translation_id, ownerId=user_id)
    mock_vocabulary.delete_one.assert_called_with(entry.db())


def test__remove_no_jwt(client, valid_request):
    """Should check access token"""
    resp = client.post('/vocab/remove', valid_request.json(by_alias=True))

    assert resp.status_code == 401
    assert get_detail(resp.content) == "Missing Authorization Header"
