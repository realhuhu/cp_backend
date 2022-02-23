from .models import *
from backend.libs import *


class CompetitionSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    def get_questions(self, instance):
        return len(instance.questions.filter(is_active=True).values("id").all())

    class Meta:
        model = Competition
        fields = [
            "id",
            "title",
            "start_time",
            "end_time",
            "time_limit",
            "questions",
            "answer_num"
        ]


class CompetitionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = ["id",
                  "content",
                  "choice_a",
                  "choice_b",
                  "choice_c",
                  "choice_d",
                  ]


__all__ = [
    "CompetitionSerializer",
    "CompetitionDetailSerializer"
]
