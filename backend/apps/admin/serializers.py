from competition.models import *
from user.models import *
from backend.libs import *


class QuestionBankSerializer(serializers.ModelSerializer):
    qid = serializers.CharField(required=False)

    class Meta:
        model = QuestionBank
        fields = ["id",
                  "qid",
                  "content",
                  "choice_a",
                  "choice_b",
                  "choice_c",
                  "choice_d",
                  "answer",
                  "category",
                  "difficulty",
                  "answer_num",
                  "correct_answer_num",
                  "is_active"
                  ]


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["id", "username", "icon", "phone", "date_joined", "is_superuser", "is_active", "password"]

    def update(self, instance, validated_data):
        if password := validated_data.pop("password", None):
            instance.set_password(password)
            instance.save()
        return super().update(instance, validated_data)


__all__ = [
    "QuestionBankSerializer",
    "CompetitionSerializer",
    "UserSerializer",
]
