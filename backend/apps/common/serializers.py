import re
from rest_framework.exceptions import ValidationError

from user.models import User
from backend.libs import EmptySerializer, serializers, re_patterns, response_code
from backend.utils import SMS


class SMSSerializer(EmptySerializer):
    method = serializers.CharField()
    phone = serializers.CharField()
    code = serializers.CharField(required=False)

    def validate_method(self, method):
        if method not in SMS.TEMPLATE_ID.keys():
            self.set_context(response_code.INVALID_PARAMS, "无效的方式")
            raise ValidationError("无效的方式")

        return method

    def validate_phone(self, phone):
        if not re.search(re_patterns.PHONE, phone):
            self.set_context(response_code.INVALID_PHONE, "无效的电话号码")
            raise ValidationError("无效的电话号码")

        return phone

    def validate_code(self, code):
        if not code:
            return code

        if not re.search(re_patterns.CODE, code):
            self.set_context(response_code.INCORRECT_CODE_FORM, "验证码应当是四位数字")
            raise ValidationError("验证码应当是四位数字")

        return code

    def validate(self, attrs):
        code = attrs.get("code")
        phone = attrs.get("phone")
        method = attrs.get("method")

        if code:
            return attrs

        is_register = User.objects.filter(phone=phone).exists()

        if is_register and method in ("register", "bind_phone"):
            self.set_context(response_code.REGISTERED, "手机号已注册")
            raise ValidationError("手机号已注册")

        if not is_register and method in ("login", "reset_password", "unbind_phone"):
            self.set_context(response_code.NOT_REGISTERED, "手机号未注册")
            raise ValidationError("手机号未注册")

        return attrs


__all__ = [
    "SMSSerializer"
]
