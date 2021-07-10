"""Vocabulary Model"""
import logging

from pydantic import Field
from pymongo import MongoClient
from pymongo.errors import OperationFailure

from app.config import CONFIG
from app.db.mongo_model import MongoModel, OID

logger = logging.getLogger('vocabulary')


def get_vocabulary_collection():
    """Get or setup vocabulary collection from MongoDB"""
    client = MongoClient(CONFIG.mongodb_url)
    db = client.prod
    vocabulary = db.vocabulary

    try:
        vocabulary.create_index('owner')
    except OperationFailure:
        logger.warning('index "owner" has already created')
    return vocabulary


class VocabularyEntry(MongoModel):
    """Vocabulary Entry Model"""
    owner_id: OID = Field(alias='ownerId')
    translation_id: OID = Field(alias='translationId')
