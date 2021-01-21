import base64
import hmac
from datetime import datetime, timedelta

import requests


def parse_params_to_str(params):
    url = "?"
    for key, value in params.items():
        url = url + str(key) + '=' + str(value) + '&'
    return url[1:-1]


def hash_string(qs, secret_key):
    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(qs, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    validating_secret = str(base64.b64encode(d).decode('utf-8'))
    return validating_secret


def sample_request():
    access_key = "c0883231-4aa9-4a1f-a77b-3ef250af-e449-42e9-856a-b3ada17c426b"
    secret_key = "QhOaeXTAAkW6yWt31jWDeERkBsZ3X4UmPds656YD"
    cur_time = datetime.utcnow()+timedelta(hours=9)
    cur_timestamp = int(cur_time.timestamp())
    qs = dict(key=access_key, timestamp=cur_timestamp)
    header_secret = hash_string(parse_params_to_str(qs), secret_key)

    url = f"http://127.0.0.1:8080/api/services?{parse_params_to_str(qs)}"
    res = requests.get(url, headers=dict(secret=header_secret))
    return res


print(sample_request().json())





"""
채널톡 사업자!
친구에게 전송
나에게 전송
"""








