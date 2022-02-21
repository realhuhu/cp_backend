from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination, OrderedDict
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from .response import APIResponse


class Pag(PageNumberPagination):
    page_size_query_param = "limit"
    page_query_param = "page"
    page_size = 10

    def get_paginated_response(self, data):
        return APIResponse(msg="成功获取此页数据", result=OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class APIModelViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options', 'trace']
    pagination_class = Pag
    filter_backends = (SearchFilter, DjangoFilterBackend)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return APIResponse(msg="成功添加数据", result=serializer.data, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse(msg="成功获取单条数据", result=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return APIResponse(msg="已更新", result=serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(msg="成功获取此页数据", result=serializer.data)


__all__ = [
    "APIModelViewSet"
]
