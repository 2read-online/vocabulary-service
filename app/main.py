"""Web application"""
import logging
import re
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
from app.nlp import NLPEngine
from app.schemas import TranslateRequest, SaveRequest, RemoveRequest

logging.basicConfig(level='DEBUG')
logger = logging.getLogger('main')

translations: Collection = get_translation_collection()
vocabulary: Collection = get_vocabulary_collection()

app = FastAPI()
nlp = NLPEngine()

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

    logger.info(req.dict())
    src_word_info = nlp.get_info(req.source_lang, req.text, req.context)
    logger.info('%s is [%s, %s]', req.text, src_word_info.lemma, src_word_info.pos)
    translations_db = translations.find({'text': src_word_info.lemma,
                                         'pos': src_word_info.pos,
                                         'source_lang': req.source_lang,
                                         'target_lang': req.target_lang})
    translation_db = None
    THRESHOLD = 0.8
    for t in translations_db:
        sim = nlp.similarity(req.source_lang, t['context'], req.context)
        logger.info('Similar to "%s" on %f', t['context'], sim)
        if sim > THRESHOLD:
            translation_db = t

    if translation_db is None:
        marked_context = req.context.replace(req.text, f'<w>{req.text}</w>', 1)
        logger.info('Translation not found for this context. Ask DeepL: "%s"', marked_context)

        deepl_resp = requests.post(url='https://api-free.deepl.com/v2/translate',
                                   data={
                                       'source_lang': req.source_lang_code,
                                       'target_lang': req.target_lang_code,
                                       'auth_key': CONFIG.deepl_key,
                                       'text': marked_context,
                                       'tag_handling': 'xml'
                                   })

        if deepl_resp.status_code != 200:
            raise HTTPException(status_code=deepl_resp.status_code, detail=deepl_resp.json())

        context_translation: str = deepl_resp.json()['translations'][0]['text']
        m = re.search('<w>(.*)</w>', context_translation)

        if m is None:
            raise HTTPException(status_code=500, detail="Failed get translation")

        translated_word = m.group(1)
        logger.info(context_translation)
        context_translation = context_translation.replace('<w>', '').replace('</w>', '')

        logger.info('%s in %s', translated_word, context_translation)
        dst_word_info = nlp.get_info(req.target_lang, translated_word, context_translation)
        logger.info('%s -> %s', translated_word, dst_word_info.lemma)

        translation = Translation(text=src_word_info.lemma, pos=src_word_info.pos,
                                  source_lang=req.source_lang,
                                  target_lang=req.target_lang,
                                  translation=dst_word_info.lemma,
                                  context=req.context)

        logger.info(translation)
        ret: InsertOneResult = translations.insert_one(translation.db())
        translation.id = ret.inserted_id
    else:
        translation = Translation.from_db(translation_db)

    return translation


@app.post('/vocab/save')
def save_to_vocabulary(req: SaveRequest, user_id: ObjectId = Depends(get_current_user)):
    """Save translation into user's vocabulary
    """
    logger.info('Save %s', req)
    entry = VocabularyEntry(translation_id=req.translation_id, owner_id=user_id)
    vocabulary.insert_one(entry.db(), entry.db())
    return {}


@app.post('/vocab/remove')
def remove_from_vocabulary(req: RemoveRequest, user_id: ObjectId = Depends(get_current_user)):
    """Remove translation from user's vocabulary
    """
    logger.info('Remove %s', req)
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
