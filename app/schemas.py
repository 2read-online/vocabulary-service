"""Request schemas"""
from pydantic import BaseModel, Field, validator, ValidationError

LANG_CODE_MAP = {
    'bul': 'BG',
    'ces': 'CS',
    'dan': 'DA',
    'deu': 'DE',
    'ell': 'EL',
    'eng': 'EN',
    'spa': 'ES',
    'est': 'ET',
    'fin': 'FI',
    'fra': 'FR',
    'hun': 'HU',
    'ita': 'IT',
    'jpn': 'JA',
    'lit': 'LT',
    'lav': 'LV',
    'nld': 'NL',
    'pol': 'PL',
    'por': 'PT',
    'ron': 'RO',
    'rus': 'RU',
    'slk': 'SK',
    'slv': 'SL',
    'swe': 'SV',
    'zho': 'ZH',
}


def _check_language(lang: str):
    if lang not in LANG_CODE_MAP:
        raise ValidationError(f'Language {lang} is not supported')
    return lang


class TranslateRequest(BaseModel):
    """Translate Request
    """
    text: str
    source_lang: str = Field(alias='sourceLang', )
    target_lang: str = Field(alias='targetLang')

    @property
    def source_lang_code(self):
        """DeepL code of source language
        """
        return LANG_CODE_MAP[self.source_lang]

    @property
    def target_lang_code(self):
        """DeepL code of target language
        """
        return LANG_CODE_MAP[self.target_lang]

    @validator('source_lang')
    def _source_lang_must_be_supported(cls, lang: str):  # pylint: disable=no-self-argument,no-self-use
        return _check_language(lang)

    @validator('target_lang')
    def _target_lang_must_be_supported(cls, lang: str):  # pylint: disable=no-self-argument, no-self-use
        return _check_language(lang)


class SaveRequest(BaseModel):
    """Save translation into vocabulary request"""
    translation_id: str = Field(alias='translationId')


class RemoveRequest(BaseModel):
    """Remove translation from vocabulary request"""
    translation_id: str = Field(alias='translationId')
