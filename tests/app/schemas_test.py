import pytest
from pydantic import ValidationError

from app.schemas import TranslateRequest


def test__translate_request_ok():
    TranslateRequest(text='some_text', targetLang='eng', sourceLang='rus')


def test__translate_request_check_target_lang():
    with pytest.raises(ValidationError):
        TranslateRequest(text='some_text', targetLang='xxx', sourceLang='rus')


def test__translate_request_check_source_lang():
    with pytest.raises(ValidationError):
        TranslateRequest(text='some_text', targetLang='rus', sourceLang='xxx')
