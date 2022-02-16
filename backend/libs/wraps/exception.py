from rest_framework.views import exception_handler
from .response import APIResponse

from .logger import log
from rest_framework.exceptions import Throttled


def common_exception_handler(exc, context):
    log.error("%s : %s" % (context["view"].__class__.__name__, str(exc)))
    ret = exception_handler(exc, context)
    if not ret:
        return APIResponse(code=-1, msg="未知错误", result='')
    else:
        if isinstance(exc, Throttled):
            return APIResponse(code=2001, msg="访问频率过快", result=ret.data)
        return APIResponse(code=0, msg="错误", result=ret.data)


__all__ = [
    "common_exception_handler",
]
