from qcloudsms_py import SmsSingleSender

from .settings import *
from backend.libs import log


def send_sms(phone, code, usage, *args):
    sender = SmsSingleSender(APP_ID, APP_KEY)
    params = [str(code), EXPIRE_TIME, *args]

    try:
        result = sender.send_with_param(86, phone, TEMPLATE_ID[usage], params, SMS_SIGN)
        return result
    except Exception as e:
        log.error(f"{phone}短信发送失败:{str(e)}")
        ...


__all__ = [
    "send_sms",
]
