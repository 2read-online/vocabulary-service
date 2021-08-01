import logging
from dataclasses import dataclass
from subprocess import run
from typing import Optional

import spacy
from spacy import Language
from app.config import CONFIG

logger = logging.getLogger(__name__)

MODEL_MAP = {
    # 'dan': 'da_core_news_md',
    'deu': 'de_core_news_md',
    # 'ell': 'el_core_news_md',
    'eng': 'en_core_web_md',
    'spa': 'es_core_news_md',
    'fra': 'fr_core_news_md',
    # 'ita': 'it_core_news_md',
    # 'jpn': 'ja_core_news_md',
    # 'lit': 'lt_core_news_md',
    # 'nld': 'nl_core_news_md',
    # 'pol': 'pl_core_news_md',
    # 'por': 'pt_core_news_md',
    # 'ron': 'ro_core_news_md',
    'rus': 'ru_core_news_md',
    # 'zho': 'zh_core_web_md',
}


@dataclass
class WordInfo:
    word: str
    lang: str
    lemma: str
    pos: str


class NLPEngine:
    def __init__(self):
        self.model_cache = dict()

    def get_info(self, lang: str, word: str, context: str) -> Optional[WordInfo]:
        root = list(filter(lambda t: t.dep_ == 'ROOT', self._get_model(lang)(word)))[0]

        doc = self._get_model(lang)(context)
        for token in doc:
            if token.text == root.text:
                print(token)
                return WordInfo(word=token.text, lang=lang, lemma=token.lemma_, pos=token.pos_)

        return None

    def similarity(self, lang: str, context1: str, context2: str) -> float:
        model = self._get_model(lang)
        return model(context1).similarity(model(context2))

    def _get_model(self, lang) -> Optional[Language]:
        if lang not in MODEL_MAP:
            return None

        model_name = MODEL_MAP[lang]

        if model_name in self.model_cache:
            return self.model_cache[model_name]

        model = spacy.load(model_name)
        self.model_cache[model_name] = model
        return model
