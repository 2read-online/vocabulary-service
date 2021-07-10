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
from app.schemas import TranslateRequest, LANG_CODE_MAP

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


# def find_text_and_check_permission(text_id: ObjectId, user_id: ObjectId) -> Text:
#     """
#     Find text in DB and check its owner
#     :param text_id: text ID
#     :param user_id: owner ID
#     :return: found text document
#     """
#     text_db = texts.find_one({'_id': text_id})
#     if text_db is None:
#         raise HTTPException(status_code=404, detail="Text not found")
#     if text_db['owner'] != user_id:
#         raise HTTPException(status_code=403, detail="You have no permission to remove this text")
#     return Text.from_db(text_db)

@app.post('/vocab/translate')
def get_translation(req: TranslateRequest, user_id: ObjectId = Depends(get_current_user)):
    """Get text from DB by its ID
    """

    translation_db = translations.find_one({'text': req.text,
                                            'source_lang': req.source_lang,
                                            'target_lang': req.target_lang})
    if translation_db is None:
        logger.info('Translation not found. Ask DeepL')

        r = requests.post(url='https://api-free.deepl.com/v2/translate',
                          data={
                              'source_lang': LANG_CODE_MAP[req.source_lang],
                              'target_lang': LANG_CODE_MAP[req.target_lang],
                              'auth_key': CONFIG.deepl_key,
                              'text': req.text
                          })

        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.json())

        translation = Translation(id=ObjectId(), text=req.text, source_lang=req.source_lang,
                                  target_lang=req.target_lang,
                                  translation=r.json()['translations'][0]['text'])
        translations.insert_one(translation.db())
    else:
        translation = Translation.from_db(translation_db)

    return translation
