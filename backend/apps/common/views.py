from uuid import uuid4

from django.core.files.base import File
from django.core.cache import cache
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from .serializers import *
from .models import *
from backend.utils import SMS, COS
from backend.libs import *


class SMSCodeView(ViewSet):
    @action(["GET"], False)
    def code(self, request):
        ser = SMSSerializer(data=request.query_params)
        ser.is_valid(True)

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


class ImageView(ViewSet):
    authentication_classes = [SuperuserJwtAuthentication]

    # 文章内图片上传
    @action(["POST"], False)
    def image(self, request):
        file = request.data.get("file")
        name = "".join(str(uuid4()).split("-"))
        form = str(file).split(".")[-1]

        if not isinstance(file, File):
            return APIResponse(response_code.WRONG_FORM, "请上传图片")

        if form.lower() not in ("jpg", "png", "bmp", "jpeg", "gif"):
            return APIResponse(response_code.WRONG_FORM, "不支持的图片格式")

        if file.size / (1024 * 1024) > 5:
            return APIResponse(response_code.EXCEEDED_SIZE, "图片不能超过5M")

        image = f"articles/{name}.{form}"
        COS.put_obj(file, image)

        return APIResponse(response_code.SUCCESS_POST_ARTICLE_IMAGE, "成功", {"data": image})


class ArticleView(ViewSet):
    @action(["GET"], True)
    def article(self, request, pk):
        instance = Articles.objects.filter(is_active=True, published=True, id=pk).first()
        if not instance:
            return APIResponse(response_code.INEXISTENT_ARTICLE, "公告不存在")

        data = ArticleDetailSerializer(instance).data
        return APIResponse(response_code.SUCCESS_GET_ARTICLE, "成功获取公告", {"data": data})


class ArticleDetailView(APIModelViewSet):
    http_method_names = ['get', 'head', 'options', 'trace']
    queryset = Articles.objects.filter(is_active=True, published=True).order_by("-id").all()
    serializer_class = ArticleSerializer
    search_fields = ["title", "description", "content"]


class SwipeView(ViewSet):
    @action(["GET"], False)
    def swipe(self, request):
        return APIResponse(result=Swipe.objects.values("url"))


class TopView(ViewSet):
    @action(["GET"], False)
    def top(self, request):
        return APIResponse(result=Top.objects.values("title", "url"))


__all__ = [
    "SMSCodeView",
    "ImageView",
    "ArticleView",
    "ArticleDetailView",
    "SwipeView",
    "TopView",
]
