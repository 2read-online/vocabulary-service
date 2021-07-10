"""Test vocabulary list request"""
# pylint: disable=redefined-outer-name
import json

from bson import ObjectId

from app.db.translation import Translation
from tests.main.conftest import get_detail


def test__list_ok(client, headers, mock_vocabulary, mock_translations, user_id):
    """should find user vocabulary"""
    mock_vocabulary.find.return_value = [
        dict(_id=ObjectId(), translation_id='ID1', owner_id=user_id),
        dict(_id=ObjectId(), translation_id='ID2', owner_id=user_id),
    ]

    translation = Translation(id=ObjectId(), source_lang='eng',
                              target_lang='rus', text='and', translation='и')
    mock_translations.find_one.return_value = translation.db()

    resp = client.get('/vocab/list', headers=headers)
    assert resp.status_code == 200
    data = json.loads(resp.content)

    assert Translation(**data[0]) == translation
    assert Translation(**data[1]) == translation

    mock_vocabulary.find.assert_called_with({'owner_id': user_id})
    assert mock_translations.find_one.mock_calls[0].args[0] == 'ID1'
    assert mock_translations.find_one.mock_calls[1].args[0] == 'ID2'


def test__list_no_jwt(client):
    """Should check access token"""
    resp = client.get('/vocab/list')

    assert resp.status_code == 401
    assert get_detail(resp.content) == "Missing Authorization Header"
