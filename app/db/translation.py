"""DB Translation Model"""
import logging

from pydantic import Field
from pymongo import MongoClient
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
        translations.create_index('text', unique=True)
    except OperationFailure as err:
        logger.warning('Index "text" already created: %s', err)
    return translations


class Translation(MongoModel):
    """Translation Model"""
    text: str
    source_lang: str = Field(alias='sourceLang')
    target_lang: str = Field(alias='targetLang')
    translation: str
