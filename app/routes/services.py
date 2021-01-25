import json
import os
from time import time, sleep

import yagmail

import requests
from fastapi import APIRouter
from fastapi.logger import logger
from starlette.background import BackgroundTasks
from starlette.requests import Request

from app.errors import exceptions as ex

from app.models import MessageOk, KakaoMsgBody, SendEmail

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
        logger.warning(e)
        raise ex.KakaoSendFailureEx

    return MessageOk()


email_content = """
<div style='margin-top:0cm;margin-right:0cm;margin-bottom:10.0pt;margin-left:0cm;line-height:115%;font-size:15px;font-family:"Calibri",sans-serif;border:none;border-bottom:solid #EEEEEE 1.0pt;padding:0cm 0cm 6.0pt 0cm;background:white;'>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:11.25pt;margin-left:0cm;line-height:115%;font-size:15px;font-family:"Calibri",sans-serif;background:white;border:none;padding:0cm;'><span style='font-size:25px;font-family:"Helvetica Neue";color:#11171D;'>{}님! Aristoxeni ingenium consumptum videmus in musicis?</span></p>
</div>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:11.25pt;margin-left:0cm;line-height:17.25pt;font-size:15px;font-family:"Calibri",sans-serif;background:white;vertical-align:baseline;'><span style='font-size:14px;font-family:"Helvetica Neue";color:#11171D;'>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quid nunc honeste dicit? Tum Torquatus: Prorsus, inquit, assentior; Duo Reges: constructio interrete. Iam in altera philosophiae parte. Sed haec omittamus; Haec para/doca illi, nos admirabilia dicamus. Nihil sane.</span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:10.0pt;margin-left:0cm;line-height:normal;font-size:15px;font-family:"Calibri",sans-serif;background:white;'><strong><span style='font-size:24px;font-family:"Helvetica Neue";color:#11171D;'>Expressa vero in iis aetatibus, quae iam confirmatae sunt.</span></strong></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:11.25pt;margin-left:0cm;line-height:17.25pt;font-size:15px;font-family:"Calibri",sans-serif;background:white;vertical-align:baseline;'><span style='font-size:14px;font-family:"Helvetica Neue";color:#11171D;'>Sit sane ista voluptas. Non quam nostram quidem, inquit Pomponius iocans; An tu me de L. Sed haec omittamus; Cave putes quicquam esse verius.&nbsp;</span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:11.25pt;margin-left:0cm;line-height:17.25pt;font-size:15px;font-family:"Calibri",sans-serif;text-align:center;background:white;vertical-align:baseline;'><span style='font-size:14px;font-family:"Helvetica Neue";color:#11171D;'><img width="378" src="https://dl1gtqdymozzn.cloudfront.net/forAuthors/K6Sfkx4f2uH780YGTbEHvHcTX3itiTBtzDWeyswQevxp8jqVttfBgPu86ZtGC6owG.webp" alt="sample1.jpg" class="fr-fic fr-dii"></span></p>

<p>
<br>
</p>

"""


@router.post("email/send_by_gmail")
async def email_by_gmail(request: Request, mailing_list: SendEmail):
    t = time()
    send_email(mailing_list=mailing_list.email_to)
    print("+*+*" * 30)
    print(str(round((time() - t) * 1000, 5)) + "ms")
    print("+*+*" * 30)
    return MessageOk()


@router.post("email/send_by_gmail2")
async def email_by_gmail2(request: Request, mailing_list: SendEmail, background_tasks: BackgroundTasks):
    t = time()
    background_tasks.add_task(
        send_email, mailing_list=mailing_list.email_to
    )
    print("+*+*" * 30)
    print(str(round((time() - t) * 1000, 5)) + "ms")
    print("+*+*" * 30)
    return MessageOk()


def send_email(**kwargs):
    mailing_list = kwargs.get("mailing_list", None)
    email_pw = os.environ.get("EMAIL_PW", None)
    email_addr = os.environ.get("EMAIL_ADDR", None)
    last_email = ""
    if mailing_list:
        try:
            yag = yagmail.SMTP({email_addr: "라이언X코알라"}, email_pw)
            # https://myaccount.google.com/u/1/lesssecureapps
            for m_l in mailing_list:
                contents = [
                    email_content.format(m_l.name)
                ]
                sleep(1)
                yag.send(m_l.email, '이렇게 한번 보내봅시다.', contents)
                last_email = m_l.email
            return True
        except Exception as e:
            print(e)
            print(last_email)
    print("발송 실패시 실패라고 알려야 합니다.")
