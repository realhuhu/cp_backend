from random import sample

from rest_framework.exceptions import ValidationError

from competition.models import *
from user.models import *
from common.models import *
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


class ScoreSerializer(serializers.ModelSerializer):
    competition = serializers.CharField(source='competition_id.title')
    username = serializers.CharField(source="user_id.username")
    time_limit = serializers.CharField(source='competition_id.time_limit')

    class Meta:
        model = UserToCompetition
        fields = [
            "id",
            "username",
            "start_time",
            "time_used",
            "score",
            "is_active",
            "competition",
            "time_limit"
        ]


class CompetitionSerializer(serializers.ModelSerializer):
    question_list = serializers.ListField(write_only=True, required=False)
    question_num = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Competition
        fields = "__all__"

    def create(self, validated_data):
        questions = validated_data.pop("question_list", None)
        num = validated_data.pop("question_num", None)

        if not questions and not num:
            raise ValidationError("缺少数量")

        instance = super(CompetitionSerializer, self).create(validated_data)

        if not questions:
            queryset = QuestionBank.objects.filter(is_active=True).values_list("id")
            questions = sample(list(map(lambda x: x[0], queryset)), num)

        for question_id in questions:
            CompetitionToQuestionBank.objects.create(
                question_id=QuestionBank.objects.filter(id=question_id).first(),
                competition_id=instance
            )

        return instance


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


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articles
        fields = "__all__"


class SwipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Swipe
        fields = "__all__"


class TopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Top
        fields = "__all__"


__all__ = [
    "QuestionBankSerializer",
    "ScoreSerializer",
    "CompetitionSerializer",
    "UserSerializer",
    "ArticleSerializer",
    "SwipeSerializer",
    "TopSerializer",
]
