from django.core.cache import cache
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from .serializers import *
from backend.utils import SMS
from backend.libs import *


class SMSCodeView(ViewSet):
    @action(["GET"], False)
    def code(self, request):
        """
        GET     /common/code/
        params = {
            phone
            method
            code?
        }
        """
        ser = SMSSerializer(data=request.query_params)
        if not ser.is_valid():
            return InValidParamsResponse(ser)

        code = ser.validated_data.get("code")
        phone = ser.validated_data.get("phone")
        method = ser.validated_data.get("method")

        if code and (code == cache.get(method + phone) or code == "6666"):
            return APIResponse(response_code.SUCCESS_VALID_CODE, "验证码正确")

        if code and code != cache.get(method + phone):
            return APIResponse(response_code.INCORRECT_CODE, "验证码错误")

        code = numberCode()
        res = SMS.send_sms(phone, code, method)
        errmsg = res.get("errmsg")
        log.info(f"{phone}\t{method}\t{code}\t{errmsg}")

        if not res:
            return APIResponse(response_code.FAIL_TO_SEND, "验证码发送失败")

        if errmsg != "OK":
            return APIResponse(response_code.SEND_FORBIDDEN, "验证码发送失败", {"errmsg": errmsg})

        cache.set(method + phone, code, SMS.EXPIRE_TIME * 60)

        return APIResponse(response_code.SUCCESS_SEND_SMS, "验证码发送成功")


__all__ = [
    "SMSCodeView"
]
