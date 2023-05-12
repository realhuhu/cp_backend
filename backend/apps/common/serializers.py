import re

from user.models import User
from .models import *
from backend.libs import *
from backend.utils import SMS


class SMSSerializer(EmptySerializer):
    method = serializers.CharField()
    phone = serializers.CharField()
    code = serializers.CharField(required=False)

    def validate_method(self, method):
        if method not in SMS.TEMPLATE_ID.keys():
            raise SerializerError("无效的方式", response_code.INVALID_PARAMS)

        return method

    def validate_phone(self, phone):
        if not re.search(re_patterns.PHONE, phone):
            raise SerializerError("无效的电话号码", response_code.INVALID_PHONE)

        return phone

    def validate_code(self, code):
        if not code:
            return code

        if not re.search(re_patterns.CODE, code):
            raise SerializerError("验证码应当是四位数字", response_code.INCORRECT_CODE_FORM)

        return code

    def validate(self, attrs):
        code = attrs.get("code")
        phone = attrs.get("phone")
        method = attrs.get("method")

        if code:
            return attrs

        is_register = User.objects.filter(phone=phone).exists()

        if is_register and method in ("register", "bind_phone"):
            raise SerializerError("手机号已注册", response_code.REGISTERED)

        if not is_register and method in ("login", "reset_password", "unbind_phone"):
            raise SerializerError("手机号未注册", response_code.NOT_REGISTERED)

        return attrs


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articles
        fields = [
            "id",
            "title",
            "description",
            "create_time",
            "update_time",
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articles
        fields = [
            "id",
            "title",
            "description",
            "create_time",
            "update_time",
            "content"
        ]


__all__ = [
    "SMSSerializer",
    "ArticleSerializer",
    "ArticleDetailSerializer",
]
