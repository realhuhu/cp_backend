from django.core.files.base import File
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

from .models import *
from .serializers import *
from backend.libs import *
from backend.utils.COS import *


class RegisterView(ViewSet):
    @action(["POST"], False)
    def register(self, request):
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
        if request.method == "GET":
            return UserInfoResponse(request.user, response_code.SUCCESS_GET_USER_INFO)
        else:
            ser = UserInfoSerializer(request.user, request.data)
            if not ser.is_valid():
                return InValidParamsResponse(ser)

            user = ser.save()
            code = response_code.SUCCESS_POST_USER_INFO
            return UserInfoResponse(user, code)

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

    @action(["POST"], False)
    def bind_phone(self, request):
        ser = BindPhoneView(request.user, request.data)
        if not ser.is_valid():
            return InValidParamsResponse(ser)

        ser.save()
        return APIResponse(response_code.SUCCESS_BIND_PHONE, "绑定手机成功")

    @action(["POST"], False)
    def unbind_phone(self, request):
        ser = UnbindPhoneView(request.user, request.data)
        if not ser.is_valid():
            return InValidParamsResponse(ser)

        ser.save()
        return APIResponse(response_code.SUCCESS_UNBIND_PHONE, "解除绑定成功")

    @action(["POST"], False)
    def icon(self, request):
        file = request.data.get("icon")
        user = request.user
        if not isinstance(file, File):
            return APIResponse(response_code.WRONG_FORM, "请上传图片")

        form = str(file).split(".")[-1]
        if form.lower() not in ("jpg", "png", "bmp", "jpeg"):
            return APIResponse(response_code.WRONG_FORM, "不支持的图片格式")

        if file.size / (1024 * 1024) > 5:
            return APIResponse(response_code.EXCEEDED_SIZE, "图片不能超过5M")

        if user.icon != "icon/default.jpg":
            delete_obj(user.icon)

        path = f"icon/{user.id}.{form}"
        if user.icon != path:
            user.icon = path
            user.save()
        put_obj(file, path)
        return APIResponse(response_code.SUCCESS_CHANGE_ICON, "修改头像成功")


__all__ = [
    "RegisterView",
    "LoginView",
    "UserInfoView"
]
