import json
import os
from typing import List
from uuid import uuid4

import requests
from fastapi import APIRouter, Depends
from fastapi.logger import logger
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.common.consts import MAX_API_KEY, MAX_API_WHITELIST
from app.database.conn import db
from app.database.schema import Users, ApiKeys, ApiWhiteLists
from app import models as m
from app.errors import exceptions as ex
import string
import secrets

from app.models import MessageOk, KakaoMsgBody

router = APIRouter(prefix='/services')


@router.get('')
async def get_all_services(request: Request):
    return dict(your_email=request.state.user.email)




@router.post('kakao/send')
async def send_kakao(request: Request, body: KakaoMsgBody):
    token = os.environ.get("KAKAO_KEY", "dOAap7zvH9ri6kj53SzApCTBy41AS6E*****************g")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/x-www-form-urlencoded"}

    body = dict(object_type="text", text=body.msg, link=dict(web_url="https://dingrr.com", mobile_url="https://dingrr.com"), button_title="지금 확인")
    data = {"template_object": json.dumps(body, ensure_ascii=False)}

    res = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", headers=headers, data=data)
    try:
        res.raise_for_status()
        if res.json()["result_code"] != 0:
            raise Exception("KAKAO SEND FAILED")
    except Exception as e:
        print(res.json())
        logger.warning(e)
        raise ex.KakaoSendFailureEx

    return MessageOk()

