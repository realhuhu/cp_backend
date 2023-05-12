from random import sample

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
                  "question_type",
                  "correct_answer_num",
                  "is_active"
                  ]
        extra_kwargs = {
            "choice_c": {"required": False, "allow_blank": True},
            "choice_d": {"required": False, "allow_blank": True},
            "category": {"required": False, "allow_blank": True},
            "difficulty": {"required": False, "allow_blank": True},
        }

    def create(self, validated_data):
        validated_data["answer"] = validated_data.get("answer").replace(" ", '').strip().upper()
        if len(validated_data.get("answer")) > 1:
            validated_data["answer"] = "".join(sorted([i for i in validated_data.get("answer") if i in "ABCD"]))
            validated_data["question_type"] = 2
        else:
            num = 0
            if validated_data.get("choice_a"):
                num += 1
            if validated_data.get("choice_b"):
                num += 1
            if validated_data.get("choice_c"):
                num += 1
            if validated_data.get("choice_d"):
                num += 1

            if num <= 2:
                validated_data["question_type"] = 1
            else:
                validated_data["question_type"] = 0

        return super(QuestionBankSerializer, self).create(validated_data)


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
    choice_num = serializers.IntegerField(write_only=True, required=False)
    TF_num = serializers.IntegerField(write_only=True, required=False)
    multi_num = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Competition
        fields = "__all__"

    def create(self, validated_data):
        question_list = validated_data.pop("question_list", [])
        question_num = validated_data.pop("question_num", None)
        choice_num = validated_data.get("choice_num")
        TF_num = validated_data.get("TF_num")
        multi_num = validated_data.get("multi_num")

        if not question_list and not question_num and not (
                TF_num is not None and choice_num is not None and multi_num is not None):
            raise SerializerError("缺少数量", response_code.INVALID_PARAMS)

        if question_num or question_list:
            validated_data["is_random"] = False

        instance = super().create({
            **validated_data,
            "total_num": len(question_list) or question_num or TF_num + choice_num + multi_num
        })

        if question_list:
            for question_id in question_list:
                CompetitionToQuestionBank.objects.create(
                    question_id=QuestionBank.objects.filter(id=question_id).first(),
                    competition_id=instance
                )

        if question_num:
            queryset = QuestionBank.objects.filter(is_active=True).values_list("id")
            questions = sample(list(map(lambda x: x[0], queryset)), question_num)
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
        fields = [
            "id",
            "card",
            "username",
            "icon",
            "phone",
            "date_joined",
            "is_superuser",
            "is_active",
            "password",
        ]

    def update(self, instance, validated_data):
        if password := validated_data.pop("password", None):
            instance.set_password(password)
            instance.save()
        return super().update(instance, validated_data)

    def create(self, validated_data):
        return self.Meta.model.objects.create_user(**validated_data)


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
