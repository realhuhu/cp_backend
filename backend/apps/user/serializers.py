import re
import time
from django.core.cache import cache
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from .models import *
from backend.libs import *


class RegisterSerializer(EmptySerializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    confirm_password = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    code = serializers.CharField(required=False)

    def validate_username(self, username):
        if not re.search(re_patterns.USERNAME, username):
            raise ValidationError("非法的用户名")

        if User.objects.filter(username=username).exists():
            self.set_context(response_code.USERNAME_REGISTERED, "用户名已注册")
            raise ValidationError("用户名已注册")

        return username

    def validate_password(self, password):
        if not re.search(re_patterns.PASSWORD, password):
            self.set_context(response_code.INVALID_PASSWORD, "非法的密码")
            raise ValidationError("非法的密码")

        return password

    def validate_confirm_password(self, confirm_password):
        if not re.search(re_patterns.PASSWORD, confirm_password):
            self.set_context(response_code.INVALID_PASSWORD, "非法的确认密码")
            raise ValidationError("非法的确认密码")

        return confirm_password

    def validate_phone(self, phone):
        if not re.search(re_patterns.PHONE, phone):
            self.set_context(response_code.INVALID_PHONE, "无效的手机号码")
            raise ValidationError("无效的手机号码")

        return phone

    def validate_code(self, code):
        if not re.search(re_patterns.CODE, code):
            self.set_context(response_code.INCORRECT_CODE_FORM, "验证码为4位数字")
            raise ValidationError("验证码为4位数字")

        return code

    def validate(self, attrs):
        if code := attrs.get("code"):
            phone = attrs.get("phone")
            if code != cache.get("register" + phone):
                raise ValidationError("验证码错误")

            attrs.pop("code")
            attrs["password"] = phone
            attrs["username"] = str(int(time.time()))
            return attrs

        password = attrs.get("password")
        confirm_password = attrs.pop("confirm_password")
        if password != confirm_password:
            self.set_context(response_code.INCONSISTENT_PASSWORD, "两次密码不一致")
            raise ValidationError("密码与确认密码不一致")

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        token = getToken(user)
        self.context["token"] = token

        return user


class LoginSerializer(EmptySerializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate_username(self, username):
        if not re.search("|".join([re_patterns.USERNAME, re_patterns.PHONE]), username):
            self.set_context(response_code.INVALID_USERNAME, "非法的用户名")
            raise ValidationError("非法的用户名")

        return username

    def validate_password(self, password):
        if not re.search("|".join([re_patterns.PASSWORD, re_patterns.CODE]), password):
            self.set_context(response_code.INVALID_PASSWORD, "非法的密码")
            raise ValidationError("非法的密码")

        return password

    def validate(self, attrs):
        user = self._get_user(attrs)
        token = getToken(user)
        self.context["token"] = token
        self.context["user"] = user
        return attrs

    def _get_user(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        user = User.objects.filter(Q(username=username) | Q(phone=username), is_active=True).first()
        if not user:
            self.set_context(response_code.USERNAME_NOT_REGISTERED, "用户不存在")
            raise ValidationError("用户不存在")

        if not (user.check_password(password) or password == cache.get("login" + username)):
            self.set_context(response_code.INCORRECT_PASSWORD, "密码错误")
            raise ValidationError("密码错误")

        return user


class ResetPasswordSerializer(EmptySerializer):
    phone = serializers.CharField()
    code = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate_phone(self, phone):
        if not re.search(re_patterns.PHONE, phone):
            self.set_context(response_code.INVALID_PHONE, "无效的电话号码")
            raise ValidationError("无效的电话号码")

        is_register = User.objects.filter(phone=phone).exists()
        if not is_register:
            self.set_context(response_code.NOT_REGISTERED, "手机号未绑定账号")
            raise ValidationError("手机号未绑定账号")

        return phone

    def validate_code(self, code):
        if not re.search(re_patterns.CODE, code):
            self.set_context(response_code.INCORRECT_CODE_FORM, "验证码格式错误")
            raise ValidationError("验证码格式错误")

        return code

    def validate_password(self, password):
        if not re.search(re_patterns.PASSWORD, password):
            self.set_context(response_code.INVALID_PASSWORD, "非法的密码")
            raise ValidationError("非法的密码")

        return password

    def validate_confirm_password(self, confirm_password):
        if not re.search(re_patterns.PASSWORD, confirm_password):
            self.set_context(response_code.INVALID_PASSWORD, "非法的确认密码")
            raise ValidationError("非法的确认密码")

        return confirm_password

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        if password != confirm_password:
            self.set_context(response_code.INCONSISTENT_PASSWORD, "两次密码不一致")
            raise ValidationError("密码与确认密码不一致")

        phone = attrs.get("phone")
        code = attrs.get("code")
        if code != cache.get("reset_password" + phone):
            self.set_context(response_code.INCORRECT_CODE, "验证码错误")
            raise ValidationError("验证码错误")

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
            self.set_context(response_code.INVALID_PASSWORD, "非法的密码")
            raise ValidationError("非法的密码")

        return old_password

    def validate_new_password(self, old_new_password):
        if not re.search(re_patterns.PASSWORD, old_new_password):
            self.set_context(response_code.INVALID_PASSWORD, "非法的密码")
            raise ValidationError("非法的密码")

        return old_new_password

    def validate_confirm_password(self, confirm_password):
        if not re.search(re_patterns.PASSWORD, confirm_password):
            self.set_context(response_code.INVALID_PASSWORD, "非法的密码")
            raise ValidationError("非法的密码")

        return confirm_password

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")
        if new_password != confirm_password:
            self.set_context(response_code.INCONSISTENT_PASSWORD, "两次密码不一致")
            raise ValidationError("密码与确认密码不一致")

        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data.get("new_password"))
        instance.save()
        return instance


class BindPhoneView(EmptySerializer):
    phone = serializers.CharField()
    code = serializers.CharField()

    def validate_phone(self, phone):
        if not re.search(re_patterns.PHONE, phone):
            self.set_context(response_code.INVALID_PHONE, "无效的电话号码")
            raise ValidationError("无效的电话号码")

        is_register = User.objects.filter(phone=phone).exists()
        if is_register:
            self.set_context(response_code.REGISTERED, "手机号已绑定账号")
            raise ValidationError("手机号已绑定账号")

        return phone

    def validate_code(self, code):
        if not re.search(re_patterns.CODE, code):
            self.set_context(response_code.INCORRECT_CODE_FORM, "验证码格式错误")
            raise ValidationError("验证码格式错误")

        return code

    def validate(self, attrs):
        phone = attrs.get("phone")
        code = attrs.get("code")
        if code != cache.get("bind_phone" + phone):
            self.set_context(response_code.INCORRECT_CODE, "验证码错误")
            raise ValidationError("验证码错误")

        return attrs

    def update(self, instance, validated_data):
        phone = validated_data.get("phone")

        instance.phone = phone
        instance.save()

        return instance


class UnbindPhoneView(EmptySerializer):
    phone = serializers.CharField()
    code = serializers.CharField()

    def validate_phone(self, phone):
        if not re.search(re_patterns.PHONE, phone):
            self.set_context(response_code.INVALID_PHONE, "无效的电话号码")
            raise ValidationError("无效的电话号码")

        is_register = User.objects.filter(phone=phone).exists()
        if not is_register:
            self.set_context(response_code.REGISTERED, "手机号未绑定账号")
            raise ValidationError("手机号未绑定账号")

        return phone

    def validate_code(self, code):
        if not re.search(re_patterns.CODE, code):
            self.set_context(response_code.INCORRECT_CODE_FORM, "验证码格式错误")
            raise ValidationError("验证码格式错误")

        return code

    def validate(self, attrs):
        phone = attrs.get("phone")
        code = attrs.get("code")
        if code != cache.get("unbind_phone" + phone):
            self.set_context(response_code.INCORRECT_CODE, "验证码错误")
            raise ValidationError("验证码错误")

        return attrs

    def update(self, instance, validated_data):
        instance.phone = None
        instance.save()

        return instance


class UserInfoSerializer(EmptySerializer):
    username = serializers.CharField(required=False)

    def validate_username(self, username):
        is_register = User.objects.filter(username=username).exists()
        if is_register:
            self.set_context(response_code.USERNAME_REGISTERED, "用户名已注册")
            raise ValidationError("用户名已注册")

        if not re.search(re_patterns.USERNAME, username):
            self.set_context(response_code.INVALID_USERNAME, "非法的用户名")
            raise ValidationError("非法的用户名")
        return username

    def update(self, instance, validated_data):
        username = validated_data.get("username")
        if username:
            instance.username = username
        instance.save()

        return instance


__all__ = [
    "RegisterSerializer",
    "LoginSerializer",
    "ResetPasswordSerializer",
    "ChangePasswordSerializer",
    "BindPhoneView",
    "UnbindPhoneView",
    "UserInfoSerializer"
]
