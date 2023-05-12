from rest_framework.response import Response
from backend.libs import response_code, getUserInfo, getToken


class APIResponse(Response):
    def __init__(self, code=None, msg=None, result=None, status=None, headers=None, content_type=None, **kwargs):
        """
        :param code: 自定义响应代码
        :param msg: 响应摘要
        :param result: 响应数据
        :param status: HTTPS响应代码
        :param headers: 额外响应头
        :param content_type:响应编码
        :param kwargs: 额外响应内容
        """
        dic = {"code": code or 100, "msg": msg or "成功", "result": result or ""}
        dic.update(kwargs)
        super().__init__(data=dic, status=status, headers=headers, content_type=content_type)


def UserInfoResponse(user, code):
    user_info = getUserInfo(user)
    token = getToken(user)
    return APIResponse(code, result={"user": user_info, "token": token})


__all__ = [
    "APIResponse",
    "UserInfoResponse"
]
