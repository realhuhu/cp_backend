import json

from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

from .models import *
from .serializers import *
from backend.libs import *


class CompetitionView(APIModelViewSet):
    http_method_names = ['get', 'head', 'options', 'trace']
    queryset = Competition.objects.filter(is_active=True).order_by("-start_time")
    serializer_class = CompetitionSerializer
    search_fields = ["id", "title", "start_time", "end_time"]


class CompetitionDetailView(ViewSet):
    authentication_classes = [CommonJwtAuthentication]

    @action(["GET"], True)
    def questions(self, request, pk):
        competition = Competition.objects.filter(id=pk, is_active=True).first()
        info = CompetitionSerializer(competition).data
        record = UserToCompetition.objects.filter(user_id=request.user, competition_id=competition).first()
        if record:
            info["start"] = record.start_time
            data = json.loads(record.answer)
        else:
            instance = competition.questions.filter(is_active=True).all()
            data = CompetitionDetailSerializer(instance, many=True).data
            UserToCompetition.objects.create(
                user_id=request.user,
                competition_id=competition,
                answer=json.dumps(data)
            )
        return APIResponse(response_code.SUCCESS_GET_QUESTIONS, "成功获取题目", {"info": info, "questions": data})

    @action(["POST"], True)
    def upload(self, request, pk):
        uid = request.user
        competition = Competition.objects.filter(id=pk, is_active=True).first()
        record = UserToCompetition.objects.filter(user_id=uid, competition_id=competition).first()
        record.answer = json.dumps(request.data["answer"])
        record.save()
        return APIResponse(response_code.SUCCESS_ANSWER_COMPETITION, "答题完成")


__all__ = [
    "CompetitionView",
    "CompetitionDetailView"
]
