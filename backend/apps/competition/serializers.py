from .models import *
from backend.libs import *


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = [
            "id",
            "title",
            "start_time",
            "end_time",
            "time_limit",
            "answer_num",
            "total_num",
            "answer_times"
        ]


class CompetitionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = [
            "id",
            "content",
            "choice_a",
            "choice_b",
            "choice_c",
            "choice_d",
        ]


class CompetitionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToCompetition
        fields = [
            "id",
            "score",
            "start_time",
            "time_used",
            "answer_times"
        ]


class EntrySerializer(serializers.ModelSerializer):
    record = serializers.SerializerMethodField()

    def get_record(self, instance: Competition):
        return CompetitionRecordSerializer(
            instance.usertocompetition_set.filter(is_active=True,
                                                  user_id=self.context["view"].request.user).all().order_by(
                "answer_times"), many=True).data

    class Meta:
        model = Competition
        fields = [
            "id",
            "title",
            "start_time",
            "end_time",
            "total_num",
            "answer_times",
            "record"
        ]


__all__ = [
    "CompetitionSerializer",
    "CompetitionDetailSerializer",
    "EntrySerializer",
]
