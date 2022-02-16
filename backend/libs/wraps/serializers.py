from rest_framework import serializers


class EmptySerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def set_context(self, code=None, msg=None):
        self.context["code"] = code
        self.context["msg"] = msg


__all__ = [
    "EmptySerializer",
    "serializers",
]
