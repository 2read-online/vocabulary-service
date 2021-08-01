"""Request schemas"""
from pydantic import BaseModel, Field, validator, ValidationError

LANG_CODE_MAP = {
    # 'bul': 'BG', # no
    # 'ces': 'CS', # no
    # 'dan': 'DA', # da_core_news_md
    'deu': 'DE', # de_core_news_md
    # 'ell': 'EL', # el_core_news_md
    'eng': 'EN', # en_core_web_md
    'spa': 'ES', # es_core_news_md
    # 'est': 'ET', # no
    # 'fin': 'FI', # no
    'fra': 'FR', # fr_core_news_md
    # 'hun': 'HU', # no
    # 'ita': 'IT', # it_core_news_md
    # 'jpn': 'JA', # ja_core_news_md
    # 'lit': 'LT', # lt_core_news_md
    # 'lav': 'LV', # no
    # 'nld': 'NL', # nl_core_news_md
    # 'pol': 'PL', # pl_core_news_md
    # 'por': 'PT', # pt_core_news_md
    # 'ron': 'RO', # ro_core_news_md
    'rus': 'RU', # ru_core_news_md
    # 'slk': 'SK', # no
    # 'slv': 'SL', # no
    # 'swe': 'SV', # no
    # 'zho': 'ZH', # zh_core_web_md
}


def _check_language(lang: str):
    if lang not in LANG_CODE_MAP:
        raise ValidationError(f'Language {lang} is not supported')
    return lang


class TranslateRequest(BaseModel):
    """Translate Request
    """
    text: str
    context: str
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
