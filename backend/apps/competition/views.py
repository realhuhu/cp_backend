import json
import datetime

from django.db.models import Q
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
        competition = Competition.objects.filter(id=pk, is_active=True)

        if not competition:
            return APIResponse(response_code.INVALID_PK, "比赛不存在")

        competition = competition.first()
        start = competition.start_time
        now = datetime.datetime.now()
        end = competition.end_time

        if now < start:
            return APIResponse(response_code.NOT_START, "还未开始")

        if now > end:
            return APIResponse(response_code.ENDED, "比赛已结束")

        record = UserToCompetition.objects.filter(
            user_id=request.user,
            competition_id_id=pk
        ).order_by(
            "answer_times"
        )

        if len(record.filter(~Q(score=None))) == competition.answer_times:
            return APIResponse(response_code.RUN_OUT, "次数已用完")

        if not record:
            return self._create_questions(request.user, 1, competition)

        record = record.last()

        if record.is_active and record.score is None:
            return self._load_questions(record, competition)

        return self._create_questions(request.user, record.answer_times + 1, competition)

    @action(["POST"], True)
    def upload(self, request, pk):
        competition = Competition.objects.filter(id=pk, is_active=True)

        if not competition:
            return APIResponse(response_code.INVALID_PK, "比赛不存在")

        competition = competition.first()
        start = competition.start_time
        end = competition.end_time
        now = datetime.datetime.now()

        if now < start:
            return APIResponse(response_code.NOT_START, "还未开始")

        if now > end:
            return APIResponse(response_code.ENDED, "比赛已结束")

        record = UserToCompetition.objects.filter(
            user_id=request.user,
            competition_id=competition,
            is_active=True
        ).order_by("answer_times")

        if not record:
            return APIResponse(response_code.NOT_FOUND, "无记录")

        record = record.last()

        if competition.time_limit and (now - record.start_time).seconds > competition.time_limit * 60:
            record.time_used = competition.time_limit * 60
            self._calc_score(record, competition)
            record.save()
            return APIResponse(response_code.ENDED, "超时")

        if record.score:
            return APIResponse(response_code.ANSWERED, "你已经答过了")

        record.answer = json.dumps(request.data["answer"])
        record.save()

        return APIResponse(response_code.SUCCESS_ANSWER_COMPETITION, "答题完成")

    @action(["GET"], True)
    def score(self, request, pk):
        competition = Competition.objects.filter(id=pk, is_active=True)

        if not competition:
            return APIResponse(response_code.INVALID_PK, "比赛不存在")

        competition = competition.first()

        record = UserToCompetition.objects.filter(
            user_id=request.user,
            competition_id_id=pk,
            score=None,
            is_active=True
        ).order_by("answer_times")

        if not record:
            return APIResponse(response_code.NOT_ANSWERED, "无记录")

        record = record.last()

        record.time_used = (datetime.datetime.now() - record.start_time).seconds
        self._calc_score(record, competition)
        record.save()

        return APIResponse(code=response_code.SUCCESS_GET_SCORE, result={
            "id": record.id,
            "time_used": record.time_used,
            "score": record.score,
            "total": competition.total_num
        })

    @action(["GET"], True)
    def record(self, request, pk):
        record = UserToCompetition.objects.filter(
            Q(pk=pk, is_active=True, user_id=request.user, competition_id__is_active=True) & ~Q(score=None))
        if not record:
            return APIResponse(response_code.INVALID_PK, "记录不存在")
        record = record.last()
        data = json.loads(record.answer)
        info = CompetitionSerializer(record.competition_id).data
        return APIResponse(response_code.SUCCESS_GET_QUESTIONS, "成功获取题目", {"info": info, "questions": data})

    def _load_questions(self, record: UserToCompetition, competition: Competition):
        answer_start = record.start_time
        now = datetime.datetime.now()
        if competition.time_limit and (now - answer_start).seconds > competition.time_limit * 60:
            record.time_used = competition.time_limit * 60
            competition.save()
            self._calc_score(record, competition)
            record.save()
            return APIResponse(response_code.TIMEOUT, "超时", {"id": record.id})

        data = json.loads(record.answer)
        info = CompetitionSerializer(competition).data
        info["times"] = record.answer_times
        info["start"] = record.start_time
        return APIResponse(response_code.SUCCESS_GET_QUESTIONS, "成功获取题目", {"info": info, "questions": data})

    def _create_questions(self, user, answer_times, competition: Competition):
        print(answer_times)
        if answer_times == 1:
            competition.answer_num += 1
            competition.save()

        if competition.is_random:
            instance1 = QuestionBank.objects.filter(is_active=True, question_type=0).order_by("?")[
                        :competition.choice_num]
            instance2 = QuestionBank.objects.filter(is_active=True, question_type=1).order_by("?")[
                        :competition.TF_num]
            instance = instance1.union(instance2)
        else:
            instance = competition.questions.filter(is_active=True).all()

        data = CompetitionDetailSerializer(instance, many=True).data

        UserToCompetition.objects.create(
            user_id=user,
            competition_id=competition,
            answer=json.dumps(data),
            answer_times=answer_times
        )
        info = CompetitionSerializer(competition).data
        info["times"] = answer_times
        return APIResponse(response_code.SUCCESS_GET_QUESTIONS, "成功获取题目", {"info": info, "questions": data})

    def _calc_score(self, record: UserToCompetition, competition: Competition):
        raw = json.loads(record.answer)
        score = 0
        for i in raw:
            question = QuestionBank.objects.filter(id=i["id"]).first()
            if not competition.is_random:
                c_question = CompetitionToQuestionBank.objects.filter(
                    competition_id=competition,
                    question_id_id=i["id"]
                ).first()
                question.answer_num += 1
                c_question.answer_num += 1
                if i.get("answer") == question.answer or {"A": "√", "B": "X"}.get(i.get("answer")) == question.answer:
                    score += 1
                    question.correct_answer_num += 1
                    c_question.correct_answer_num += 1
                i["right_answer"] = question.answer
                question.save()
                c_question.save()
            else:
                question.answer_num += 1
                if i.get("answer") == question.answer or {"A": "√", "B": "X"}.get(i.get("answer")) == question.answer:
                    score += 1
                    question.correct_answer_num += 1
                i["right_answer"] = question.answer
                question.save()

        record.score = score
        record.answer = json.dumps(raw)


class EntryView(APIModelViewSet):
    http_method_names = ['get', 'head', 'options', 'trace']
    authentication_classes = [CommonJwtAuthentication]
    serializer_class = EntrySerializer

    def get_queryset(self):
        a = Competition.objects.filter(
            is_active=True,
            usertocompetition__user_id=self.request.user
        ).all().distinct().order_by("-id")
        return a


class ExerciseView(ViewSet):
    authentication_classes = [CommonJwtAuthentication]

    @action(["GET", "POST"], False)
    def random(self, request):
        if request.method == "GET":
            question = QuestionBank.objects.filter(is_active=True).order_by("?").first()
            return APIResponse(result={
                "id": question.id,
                "content": question.content,
                "choice_a": question.choice_a,
                "choice_b": question.choice_b,
                "choice_c": question.choice_c,
                "choice_d": question.choice_d,
                "difficulty": question.difficulty,
                "answer_num": question.answer_num,
                "correct_answer_num": question.correct_answer_num
            })
        else:
            qid = request.data.get("id")
            answer = request.data.get("answer")
            question = QuestionBank.objects.filter(is_active=True, id=qid).first()

            right = False

            question.answer_num += 1
            if question.answer == answer or question.answer == {"A": "√", "B": "X"}.get(answer):
                question.correct_answer_num += 1
                right = True

            question.save()
            return APIResponse(result={
                "right": right,
                "answer": question.answer
            })


__all__ = [
    "CompetitionView",
    "CompetitionDetailView",
    "EntryView",
    "ExerciseView",
]
