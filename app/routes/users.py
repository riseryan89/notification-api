from typing import List
from uuid import uuid4

import bcrypt
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request
from fastapi.logger import logger

from app.common.consts import MAX_API_KEY
from app.database.conn import db
from app.database.schema import Users, ApiKeys
from app import models as m
from app.errors import exceptions as ex
import string
import secrets

from app.models import MessageOk

router = APIRouter(prefix='/user')


@router.get('/me')
async def get_me(request: Request):
    user = request.state.user
    user_info = Users.get(id=user.id)
    return user_info


@router.put('/me')
async def put_me(request: Request):
    ...


@router.delete('/me')
async def delete_me(request: Request):
    ...


@router.get('/apikeys', response_model=List[m.GetApiKeyList])
async def get_api_keys(request: Request):
    user = request.state.user
    api_keys = ApiKeys.filter(user_id=user.id).filter(id__gt=1).all()
    return api_keys


@router.post('/apikeys', response_model=m.GetApiKeys)
async def create_api_keys(request: Request, key_info: m.AddApiKey, session: Session = Depends(db.session)):
    user = request.state.user

    api_keys = ApiKeys.filter(session, user_id=user.id, status='active').count()
    if api_keys == MAX_API_KEY:
        raise ex.MaxKeyCountEx()

    alphabet = string.ascii_letters + string.digits
    s_key = ''.join(secrets.choice(alphabet) for i in range(40))
    uid = f"{str(uuid4())[:-12]}{str(uuid4())}"

    key_info = key_info.dict()

    try:
        new_key = ApiKeys.create(session, auto_commit=True, secret_key=s_key, user_id=user.id, access_key=uid, **key_info)
    except Exception as e:
        raise ex.SqlFailureEx(e)
    return new_key


@router.delete('/apikeys/{key_id}')
async def delete_api_keys(request: Request, key_id: int, access_key: str):
    user = request.state.user
    key_data = ApiKeys.get(access_key=access_key)
    if key_data and key_data.id == key_id and key_data.user_id == user.id:
        ApiKeys.filter(id=key_id).delete(auto_commit=True)
        return MessageOk()
    else:
        raise ex.NoKeyMatchEx()
