"""DB Translation Model"""
import logging
from typing import Optional, List, Set

from pydantic import Field
from pymongo import MongoClient, IndexModel, ASCENDING
from pymongo.errors import OperationFailure

from app.db.mongo_model import MongoModel
from app.config import CONFIG

logger = logging.getLogger('translation')


def get_translation_collection():
    """Get or setup translation collection from MongoDB"""
    client = MongoClient(CONFIG.mongodb_url)
    db = client.prod
    translations = db.translations

    try:
        translations.create_index(keys=[('text', ASCENDING), ('pos', ASCENDING)], name='text_pos')
    except OperationFailure as err:
        logger.warning('Index "text" already created: %s', err)
    return translations


class Translation(MongoModel):
    """Translation Model"""
    text: str
    pos: Optional[str]
    forms: List[str]
    source_lang: str = Field(alias='sourceLang')
    target_lang: str = Field(alias='targetLang')
    translation: str
    context: Optional[str]
