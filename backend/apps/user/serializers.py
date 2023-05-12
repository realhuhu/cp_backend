import re
from django.core.cache import cache
from django.db.models import Q

from .models import *
from backend.libs import *


class LoginSerializer(EmptySerializer):
    card = serializers.CharField()
    password = serializers.CharField()

    def validate_card(self, card):
        if not re.search("|".join([re_patterns.CARD, re_patterns.PHONE]), card):
            raise SerializerError("无效的一卡通号", response_code.INVALID_USERNAME)

        return card

    def validate_password(self, password):
        if not re.search("|".join([re_patterns.PASSWORD, re_patterns.CODE]), password):
            raise SerializerError("非法的密码", response_code.INVALID_PASSWORD)

        return password

    def validate(self, attrs):
        user = self._get_user(attrs)
        token = getToken(user)
        self.context["token"] = token
        self.context["user"] = user
        return attrs

    def _get_user(self, attrs):
        card = attrs.get("card")
        password = attrs.get("password")
        user = User.objects.filter(Q(card=card) | Q(phone=card), is_active=True).first()
        if not user:
            raise SerializerError("用户不存在", response_code.USERNAME_NOT_REGISTERED)

        if not (user.check_password(password) or password == cache.get("login" + card)):
            raise SerializerError("密码错误", response_code.INCORRECT_PASSWORD)

        return user


# class LoginSerializer(EmptySerializer):
#     card = serializers.CharField()
#
#     def validate_card(self, card):
#         if not re.search(re_patterns.CARD, card):
#             raise SerializerError("无效的一卡通号", response_code.INVALID_USERNAME)
#
#         return card
#
#     def validate(self, attrs):
#         user = self._get_user(attrs)
#         token = getToken(user)
#         self.context["token"] = token
#         self.context["user"] = user
#         return attrs
#
#     def _get_user(self, attrs):
#         card = attrs.get("card")
#         user = User.objects.filter(card=card, is_active=True).first()
#         if not user:
#             raise SerializerError("用户不存在", response_code.USERNAME_NOT_REGISTERED)
#
#         return user


class ResetPasswordSerializer(EmptySerializer):
    phone = serializers.CharField()
    code = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate_phone(self, phone):
        if not re.search(re_patterns.PHONE, phone):
            raise SerializerError("无效的电话号码", response_code.INVALID_PHONE)

        is_register = User.objects.filter(phone=phone).exists()
        if not is_register:
            raise SerializerError("手机号未绑定账号", response_code.NOT_REGISTERED)

        return phone

    def validate_code(self, code):
        if not re.search(re_patterns.CODE, code):
            raise SerializerError("验证码格式错误", response_code.INCORRECT_CODE_FORM)

        return code

    def validate_password(self, password):
        if not re.search(re_patterns.PASSWORD, password):
            raise SerializerError("非法的密码", response_code.INVALID_PASSWORD)

        return password

    def validate_confirm_password(self, confirm_password):
        if not re.search(re_patterns.PASSWORD, confirm_password):
            raise SerializerError("非法的确认密码", response_code.INVALID_PASSWORD)

        return confirm_password

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        if password != confirm_password:
            raise SerializerError("密码与确认密码不一致", response_code.INCONSISTENT_PASSWORD)

        phone = attrs.get("phone")
        code = attrs.get("code")
        if code != cache.get("reset_password" + phone):
            raise SerializerError("验证码错误", response_code.INCORRECT_CODE)

        return attrs

    def update(self, instance, validated_data):
        phone = validated_data.get("phone")
        password = validated_data.get("password")
        user = instance.filter(phone=phone).first()
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(EmptySerializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate_old_password(self, old_password):
        if not re.search(re_patterns.PASSWORD, old_password):
            raise SerializerError("非法的密码", response_code.INVALID_PASSWORD)

        return old_password

    def validate_new_password(self, old_new_password):
        if not re.search(re_patterns.PASSWORD, old_new_password):
            raise SerializerError("非法的密码", response_code.INVALID_PASSWORD)

        return old_new_password

    def validate_confirm_password(self, confirm_password):
        if not re.search(re_patterns.PASSWORD, confirm_password):
            raise SerializerError("非法的密码", response_code.INVALID_PASSWORD)

        return confirm_password

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")
        if new_password != confirm_password:
            raise SerializerError("密码与确认密码不一致", response_code.INCONSISTENT_PASSWORD)

        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data.get("new_password"))
        instance.save()
        return instance


class BindPhoneSerializer(EmptySerializer):
    phone = serializers.CharField()
    code = serializers.CharField()

    def validate_phone(self, phone):
        if not re.search(re_patterns.PHONE, phone):
            raise SerializerError("无效的电话号码", response_code.INVALID_PHONE)

        is_register = User.objects.filter(phone=phone).exists()
        if is_register:
            raise SerializerError("手机号已绑定账号", response_code.REGISTERED)

        return phone

    def validate_code(self, code):
        if not re.search(re_patterns.CODE, code):
            raise SerializerError("验证码格式错误", response_code.INCORRECT_CODE_FORM)

        return code

    def validate(self, attrs):
        phone = attrs.get("phone")
        code = attrs.get("code")
        if code != cache.get("bind_phone" + phone):
            raise SerializerError("验证码错误", response_code.INCORRECT_CODE)

        return attrs

    def update(self, instance, validated_data):
        phone = validated_data.get("phone")

        instance.phone = phone
        instance.save()

        return instance


class UnbindPhoneSerializer(EmptySerializer):
    phone = serializers.CharField()
    code = serializers.CharField()

    def validate_phone(self, phone):
        if not re.search(re_patterns.PHONE, phone):
            raise SerializerError("无效的电话号码", response_code.INVALID_PHONE)

        is_register = User.objects.filter(phone=phone).exists()
        if not is_register:
            raise SerializerError("手机号未绑定账号", response_code.REGISTERED)

        return phone

    def validate_code(self, code):
        if not re.search(re_patterns.CODE, code):
            raise SerializerError("验证码格式错误", response_code.INCORRECT_CODE_FORM)

        return code

    def validate(self, attrs):
        phone = attrs.get("phone")
        code = attrs.get("code")
        if code != cache.get("unbind_phone" + phone):
            raise SerializerError("验证码错误", response_code.INCORRECT_CODE)

        return attrs

    def update(self, instance, validated_data):
        instance.phone = None
        instance.save()

        return instance


__all__ = [
    "LoginSerializer",
    "ResetPasswordSerializer",
    "ChangePasswordSerializer",
    "BindPhoneSerializer",
    "UnbindPhoneSerializer",
]
