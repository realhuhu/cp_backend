from django.db.models import F, Q
from rest_framework.mixins import DestroyModelMixin

from competition.models import *
from user.models import *
from common.models import *
from .serializers import *
from backend.libs import *


class QuestionBankView(APIModelViewSet):
    throttle_classes = []
    authentication_classes = [SuperuserJwtAuthentication]
    queryset = QuestionBank.objects.all()
    serializer_class = QuestionBankSerializer
    filter_fields = ["category", "difficulty", "is_active"]
    search_fields = ["id", "content", "choice_a", "choice_b", "choice_b", "category", "difficulty"]

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


class ScoreView(APIModelViewSet):
    throttle_classes = []
    authentication_classes = [SuperuserJwtAuthentication]
    queryset = UserToCompetition.objects.all().order_by("-score")
    serializer_class = ScoreSerializer
    filter_fields = ["is_active"]

    def get_queryset(self):
        queryset = self.queryset
        search = self.request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                Q(user_id__username__contains=search) | Q(competition_id__title__contains=search)
            )

        return queryset


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

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        if isinstance(self.request.data, list):
            kwargs.pop("many", None)
            return serializer_class(many=True, *args, **kwargs)
        else:
            return serializer_class(*args, **kwargs)


class ArticleView(APIModelViewSet):
    throttle_classes = []
    authentication_classes = [SuperuserJwtAuthentication]
    queryset = Articles.objects.all().order_by("create_time")
    serializer_class = ArticleSerializer
    filter_fields = ["is_active", "published"]
    search_fields = ["title", "description", "content"]


class SwipeView(APIModelViewSet):
    throttle_classes = []
    http_method_names = ['get', 'post', 'put', 'patch', "delete", 'head', 'options', 'trace']

    authentication_classes = [SuperuserJwtAuthentication]
    queryset = Swipe.objects.all().order_by("id")
    serializer_class = SwipeSerializer
    search_fields = ["url"]


class TopView(APIModelViewSet, DestroyModelMixin):
    http_method_names = ['get', 'post', 'put', 'patch', "delete", 'head', 'options', 'trace']

    throttle_classes = []
    authentication_classes = [SuperuserJwtAuthentication]
    queryset = Top.objects.order_by("id")
    serializer_class = TopSerializer
    search_fields = ["url", "title"]


__all__ = [
    "QuestionBankView",
    "ScoreView",
    "CompetitionView",
    "UserView",
    "ArticleView",
    "SwipeView",
    "TopView",
]
