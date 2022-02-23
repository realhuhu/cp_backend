from django.db import models


class QuestionBank(models.Model):
    content = models.TextField(verbose_name="题干")
    choice_a = models.TextField(null=True, verbose_name="选项A")
    choice_b = models.TextField(null=True, verbose_name="选项B")
    choice_c = models.TextField(null=True, verbose_name="选项C")
    choice_d = models.TextField(null=True, verbose_name="选项D")
    answer = models.CharField(max_length=5, verbose_name="正确答案")
    category = models.CharField(max_length=10, verbose_name="分类")
    difficulty = models.CharField(max_length=5, verbose_name="难度")
    answer_num = models.IntegerField(default=0, verbose_name="被回答次数")
    correct_answer_num = models.IntegerField(default=0, verbose_name="被正确回答次数")
    is_active = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        ordering = ["id"]


class Competition(models.Model):
    title = models.CharField(max_length=20, verbose_name="比赛名称")
    start_time = models.DateTimeField("比赛开始日期")
    end_time = models.DateTimeField("比赛截止日期")
    time_limit = models.IntegerField(null=True, default=None, verbose_name="答题限时(分钟)")
    answer_num = models.IntegerField(default=0, verbose_name="参与人次")
    questions = models.ManyToManyField(to=QuestionBank,
                                       through='CompetitionToQuestionBank',
                                       through_fields=('competition_id', 'question_id'),
                                       )
    is_active = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        ordering = ["id"]


class UserToCompetition(models.Model):
    user_id = models.ForeignKey(to="user.User", on_delete=models.DO_NOTHING)
    competition_id = models.ForeignKey(to="Competition", on_delete=models.DO_NOTHING)
    answer = models.TextField(null=True, default=None, verbose_name="答题信息")
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="开始答题时间")
    time_used = models.IntegerField(null=True, default=None, verbose_name="耗时(秒)")
    score = models.IntegerField(default=0, verbose_name="得分")
    is_active = models.BooleanField(default=True, verbose_name="是否有效")


class CompetitionToQuestionBank(models.Model):
    competition_id = models.ForeignKey(to="Competition", on_delete=models.DO_NOTHING)
    question_id = models.ForeignKey(to="QuestionBank", on_delete=models.DO_NOTHING)
    answer_num = models.IntegerField(default=0, verbose_name="被回答次数")
    correct_answer_num = models.IntegerField(default=0, verbose_name="被正确回答次数")

    class Meta:
        ordering = ["id"]


__all__ = [
    "QuestionBank",
    "Competition",
    "UserToCompetition",
    "CompetitionToQuestionBank"
]
