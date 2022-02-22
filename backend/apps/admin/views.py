from competition.models import *
from user.models import *
from .serializers import *
from backend.libs import *
from django.db.models import F


class QuestionBankView(APIModelViewSet):
    throttle_classes = []
    authentication_classes = [SuperuserJwtAuthentication]
    queryset = QuestionBank.objects.all()
    serializer_class = QuestionBankSerializer
    filter_fields = ["category", "difficulty", "is_active"]
    search_fields = ["id", "content", "choice_a", "choice_b", "choice_b"]

    def get_queryset(self):
        if cid := self.request.query_params.copy().get("cid"):
            self.filter_fields = []
            self.search_fields = ["content", "choice_a", "choice_b", "choice_b", "category", "difficulty"]
            a = CompetitionToQuestionBank.objects.filter(competition_id_id=cid).all().annotate(
                qid=F("question_id"),
                content=F("question_id__content"),
                choice_a=F("question_id__choice_a"),
                choice_b=F("question_id__choice_b"),
                choice_c=F("question_id__choice_c"),
                choice_d=F("question_id__choice_d"),
                answer=F("question_id__answer"),
                category=F("question_id__category"),
                difficulty=F("question_id__difficulty"),
                is_active=F("question_id__is_active")
            ).values(
                "id",
                "qid",
                "answer_num",
                "correct_answer_num",
                "content",
                "choice_a",
                "choice_b",
                "choice_c",
                "choice_d",
                "answer",
                "category",
                "difficulty",
                "is_active",
            ).order_by("question_id_id")
            print(a)
            return a
        return self.queryset

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        if isinstance(self.request.data, list):
            kwargs.pop("many", None)
            return serializer_class(many=True, *args, **kwargs)
        else:
            return serializer_class(*args, **kwargs)


class CompetitionView(APIModelViewSet):
    throttle_classes = []
    authentication_classes = [SuperuserJwtAuthentication]
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    filter_fields = ["is_active"]
    search_fields = ["id", "title", "start_time", "end_time"]


class UserView(APIModelViewSet):
    throttle_classes = []
    authentication_classes = [SuperuserJwtAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_fields = ["is_active"]
    search_fields = ["username", "phone"]


__all__ = [
    "QuestionBankView",
    "CompetitionView",
    "UserView"
]
