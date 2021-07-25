# pylint: disable=redefined-outer-name, too-many-arguments
"""Test handling Translate Request"""
from unittest.mock import Mock

import pytest
from bson import ObjectId
from pymongo.results import InsertOneResult
from requests import Response

from app.db.translation import Translation
from app.schemas import TranslateRequest
from tests.main.conftest import get_detail


@pytest.fixture
def valid_request() -> TranslateRequest:
    """Valid HTTP request"""
    return TranslateRequest(
        text='hey',
        targetLang='rus',
        sourceLang='eng',
        context='hey there'
    )


@pytest.fixture
def deepl_response():
    """Response from DeepL"""
    deepl_resp = Mock(spec=Response)
    deepl_resp.status_code = 200
    deepl_resp.json.return_value = dict(translations=[dict(text='<w>привет</w> там')])
    return deepl_resp


@pytest.fixture
def translation() -> Translation:
    """Translation example"""
    return Translation(id=ObjectId(), source_lang='eng',
                       target_lang='rus', text='hey', translation='привет', pos='INTJ', context='hey there')


def test__translate_from_deepl(client, headers, valid_request: TranslateRequest, deepl_response,
                               mock_translations, mock_post):
    """Should request translation from DeepL if there is no translation in DB
    """
    mock_translations.find.return_value = []
    translation_id = ObjectId()
    mock_translations.insert_one.return_value = InsertOneResult(
        inserted_id=translation_id, acknowledged=True)
    mock_post.return_value = deepl_response
    resp = client.post('/vocab/translate', valid_request.json(by_alias=True), headers=headers)

    assert resp.status_code == 200
    mock_post.assert_called_with(url='https://api-free.deepl.com/v2/translate',
                                 data=dict(source_lang='EN', target_lang='RU',
                                           auth_key='xxxxxxx', text='<w>hey</w> there', tag_handling='xml')
                                 )

    mock_translations.insert_one.assert_called_with(
        {'text': 'hey', 'source_lang': 'eng', 'pos': 'INTJ', 'target_lang': 'rus', 'translation': 'привет',
         'context': 'hey there'})

    translation = Translation.parse_raw(resp.content)
    assert translation.source_lang == valid_request.source_lang
    assert translation.target_lang == valid_request.target_lang
    assert translation.text == valid_request.text
    assert translation.translation == 'привет'
    assert translation.id == translation_id


def test__translate_from_db(client, headers, valid_request: TranslateRequest,
                            translation: Translation, mock_translations, mock_post):
    """Should request translation from DB
    """
    mock_translations.find.return_value = [translation.db()]

    resp = client.post('/vocab/translate', valid_request.json(by_alias=True), headers=headers)

    assert resp.status_code == 200

    mock_post.assert_not_called()
    assert translation == Translation.parse_raw(resp.content)


def test__translate_no_jwt(client, valid_request):
    """Should check access token"""
    resp = client.post('/vocab/translate', valid_request.json(by_alias=True))

    assert resp.status_code == 401
    assert get_detail(resp.content) == "Missing Authorization Header"
