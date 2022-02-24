import json
import datetime

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
        start = competition.start_time
        end = competition.end_time
        now = datetime.datetime.now()
        record = UserToCompetition.objects.filter(user_id=request.user, competition_id=competition).first()

        if now < start:
            return APIResponse(response_code.NOT_START, "还未开始")

        if now > end:
            return APIResponse(response_code.ENDED, "比赛已结束", {"answered": bool(record)})

        info = CompetitionSerializer(competition).data
        if record:
            answer_start = record.start_time

            if info["time_limit"] and not record.time_used and (now - answer_start).seconds > info["time_limit"] * 60:
                record.time_used = info["time_limit"] * 60
                record.save()
                competition.answer_num += 1
                competition.save()
                return APIResponse(response_code.TIMEOUT, "超时")

            if record.time_used:
                return APIResponse(response_code.ANSWERED, "你已经答过了")

            info["start"] = answer_start
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
        start = competition.start_time
        end = competition.end_time
        now = datetime.datetime.now()

        if now < start:
            return APIResponse(response_code.NOT_START, "还未开始")

        if now > end:
            return APIResponse(response_code.ENDED, "比赛已结束")

        record = UserToCompetition.objects.filter(user_id=uid, competition_id=competition).first()

        if record.time_used:
            return APIResponse(response_code.ANSWERED, "你已经答过了")

        record.answer = json.dumps(request.data["answer"])

        if request.data.get("finish"):
            competition.answer_num += 1
            competition.save()
            record.time_used = (now - record.start_time).seconds

        record.save()

        return APIResponse(response_code.SUCCESS_ANSWER_COMPETITION, "答题完成")

    @action(["GET"], True)
    def score(self, request, pk):
        uid = request.user
        record = UserToCompetition.objects.filter(user_id=uid, competition_id_id=pk, is_active=True).first()
        competition = Competition.objects.filter(id=pk, is_active=True).first()
        start = record.start_time
        now = datetime.datetime.now()
        raw = json.loads(record.answer)

        if not record:
            return APIResponse(response_code.NOT_ANSWERED, "未参加比赛")

        if not record.time_used and (now - start).seconds < competition.time_limit * 60:
            return APIResponse(response_code.NOT_ANSWERED, "未提交")

        if record.score is not None:
            return APIResponse(code=response_code.SUCCESS_GET_SCORE, result={
                "time_used": record.time_used,
                "score": record.score,
                "total": len(raw)
            })

        score = 0
        answered = filter(lambda x: x.get("answer"), raw)

        for i in answered:
            question = QuestionBank.objects.filter(id=i["id"]).first()
            c_question = CompetitionToQuestionBank.objects.filter(competition_id_id=pk, question_id_id=i["id"]).first()
            question.answer_num += 1
            c_question.answer_num += 1
            if i["answer"] == question.answer:
                score += 1
                question.correct_answer_num += 1
                c_question.correct_answer_num += 1
            question.save()
            c_question.save()

        record.score = score

        if not record.time_used:
            record.time_used = competition.time_limit * 60
            competition.answer_num += 1
            competition.save()

        record.save()

        return APIResponse(code=response_code.SUCCESS_GET_SCORE, result={
            "time_used": record.time_used,
            "score": record.score,
            "total": len(raw)
        })


class EntryView(APIModelViewSet):
    http_method_names = ['get', 'head', 'options', 'trace']
    authentication_classes = [CommonJwtAuthentication]
    serializer_class = EntrySerializer

    def get_queryset(self):
        return UserToCompetition.objects.filter(is_active=True, user_id=self.request.user).all().order_by("-id")


__all__ = [
    "CompetitionView",
    "CompetitionDetailView",
    "EntryView",
]
