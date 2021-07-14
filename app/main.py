"""Web application"""
import logging
from typing import List

import requests

from bson import ObjectId
from fastapi import FastAPI, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pymongo.collection import Collection
from pymongo.results import InsertOneResult
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import CONFIG
from app.db.translation import Translation, get_translation_collection
from app.db.vocabulary import VocabularyEntry, get_vocabulary_collection
from app.schemas import TranslateRequest, SaveRequest, RemoveRequest

logging.basicConfig(level='DEBUG')
logger = logging.getLogger('main')

translations: Collection = get_translation_collection()
vocabulary: Collection = get_vocabulary_collection()

app = FastAPI()


@AuthJWT.load_config
def get_config():
    """Load settings
    """
    return CONFIG


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(_request: Request, exc: AuthJWTException):
    """
    JWT exception
    :param _request:
    :param exc:
    :return:
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


def get_current_user(req: Request) -> ObjectId:
    """Get ID of authorized user
        """
    authorize = AuthJWT(req)
    authorize.jwt_required()
    return ObjectId(authorize.get_jwt_subject())


@app.post('/vocab/translate')
def get_translation(req: TranslateRequest, _user_id: ObjectId = Depends(get_current_user)):
    """Get text from DB by its ID
    """
    translation_db = translations.find_one({'text': req.text,
                                            'source_lang': req.source_lang,
                                            'target_lang': req.target_lang})
    if translation_db is None:
        logger.info('Translation not found. Ask DeepL')

        deepl_resp = requests.post(url='https://api-free.deepl.com/v2/translate',
                          data={
                              'source_lang': req.source_lang_code,
                              'target_lang': req.target_lang_code,
                              'auth_key': CONFIG.deepl_key,
                              'text': req.text
                          })

        if deepl_resp.status_code != 200:
            raise HTTPException(status_code=deepl_resp.status_code, detail=deepl_resp.json())

        translation = Translation(text=req.text, source_lang=req.source_lang,
                                  target_lang=req.target_lang,
                                  translation=deepl_resp.json()['translations'][0]['text'])
        ret: InsertOneResult = translations.insert_one(translation.db())
        translation.id = ret.inserted_id
    else:
        translation = Translation.from_db(translation_db)

    return translation


@app.post('/vocab/save')
def save_to_vocabulary(req: SaveRequest, user_id: ObjectId = Depends(get_current_user)):
    """Save translation into user's vocabulary
    """
    entry = VocabularyEntry(translation_id=req.translation_id, owner_id=user_id)
    vocabulary.insert_one(entry.db(), entry.db())
    return {}


@app.post('/vocab/remove')
def remove_from_vocabulary(req: RemoveRequest, user_id: ObjectId = Depends(get_current_user)):
    """Remove translation from user's vocabulary
    """
    entry = VocabularyEntry(translation_id=req.translation_id, owner_id=user_id)
    vocabulary.delete_one(entry.db())
    return {}


@app.get('/vocab/list')
def list_vocabulary(user_id: ObjectId = Depends(get_current_user)):
    """List translations in the vocabulary"""
    user_vocabulary = vocabulary.find({'owner_id': user_id})
    response: List[Translation] = []
    for entry in user_vocabulary:
        translation_db = translations.find_one(entry['translation_id'])
        if translation_db is not None:
            response.append(Translation.from_db(translation_db))

    return response
