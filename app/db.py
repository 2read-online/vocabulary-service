import logging
from datetime import datetime
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel, BaseConfig, Field
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import OperationFailure

from app.config import CONFIG

logger = logging.getLogger('db')


def get_translation_collection():
    """Get or setup user collection from MongoDB"""
    client = MongoClient(CONFIG.mongodb_url)
    db: Database = client.prod
    translations: Collection = db.translations

    try:
        translations.create_index('text')
    except OperationFailure:
        logger.warning('User ID index already created')
    return translations


class OID(str):
    """Wrapper around ObjectId"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """Validate ID
        """
        try:
            return ObjectId(str(v))
        except InvalidId as err:
            raise ValueError("Not a valid ObjectId") from err


class MongoModel(BaseModel):
    """Base mongo document with ID"""
    id: Optional[OID]

    class Config(BaseConfig):
        """Config
        """
        allow_population_by_field_name = True  # << Added
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),  # pylint: disable=unnecessary-lambda
            ObjectId: lambda oid: str(oid),  # pylint: disable=unnecessary-lambda
        }

    @classmethod
    def from_db(cls, obj: dict):
        """Load model from DB document
        """
        if obj is None:
            return None

        return cls(id=obj['_id'], **obj)

    def db(self) -> dict:
        """Export to mongo document"""
        data: dict = self.dict(exclude_none=True)
        if 'id' in data:
            data['_id'] = data.pop('id')

        return data


class Translation(MongoModel):
    id: OID
    text: str
    source_lang: str = Field(alias='sourceLang')
    target_lang: str = Field(alias='targetLang')
    translation: str

    # TODO: Add validation for supported languages
