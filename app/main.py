"""Web application"""
import logging
import requests

from bson import ObjectId
from fastapi import FastAPI, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pymongo.collection import Collection
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import CONFIG
from app.db import Translation, get_translation_collection
from app.schemas import TranslateRequest

logging.basicConfig(level='DEBUG')
logger = logging.getLogger('app')

translations: Collection = get_translation_collection()

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

        translation = Translation(id=ObjectId(), text=req.text, source_lang=req.source_lang,
                                  target_lang=req.target_lang,
                                  translation=deepl_resp.json()['translations'][0]['text'])
        translations.insert_one(translation.db())
    else:
        translation = Translation.from_db(translation_db)

    return translation
