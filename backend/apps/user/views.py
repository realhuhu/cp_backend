from django.core.files.base import File
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

from .models import *
from .serializers import *
from backend.libs import (
    InValidParamsResponse,
    APIResponse, getUserInfo,
    response_code,
    CommonJwtAuthentication,
    UserInfoResponse
)


class RegisterView(ViewSet):
    @action(["POST"], False)
    def register(self, request):
        """
        POST     /user/register/
        params = {
            username
            password
            confirm_password
        }
        """
        ser = RegisterSerializer(data=request.data)
        if not ser.is_valid():
            return InValidParamsResponse(ser)

        user = ser.save()

        return UserInfoResponse(user, response_code.SUCCESS_REGISTER)


class LoginView(ViewSet):
    @action(["POST"], False)
    def login(self, request):
        ser = LoginSerializer(data=request.data)
        if not ser.is_valid():
            return InValidParamsResponse(ser)

        user = ser.context["user"]
        user_info = getUserInfo(user)
        token = ser.context["token"]

        return APIResponse(response_code.SUCCESS_LOGIN, "登录成功", {"user": user_info, "token": token})


class UserInfoView(ViewSet):
    def get_authenticators(self):
        if self.request.META.get("PATH_INFO") == "/user/reset_password/":
            return None
        return [CommonJwtAuthentication()]

    @action(["GET", "POST"], False)
    def user_info(self, request):
        return UserInfoResponse(request.user, response_code.SUCCESS_GET_USER_INFO)

    @action(["POST"], False)
    def reset_password(self, request):
        ser = ResetPasswordSerializer(User.objects, request.data)
        if not ser.is_valid():
            return InValidParamsResponse(ser)

        ser.save()
        return APIResponse(response_code.SUCCESS_RESET_PASSWORD, "重置密码成功")

    @action(["POST"], False)
    def change_password(self, request):
        ser = ChangePasswordSerializer(request.user, request.data)
        if not ser.is_valid():
            return InValidParamsResponse(ser)

        if not request.user.check_password(ser.validated_data.get("old_password")):
            return APIResponse(response_code.INCORRECT_PASSWORD, "原密码错误")

        ser.save()
        return APIResponse(response_code.SUCCESS_RESET_PASSWORD, "重置密码成功")


__all__ = [
    "RegisterView",
    "LoginView",
    "UserInfoView"
]
