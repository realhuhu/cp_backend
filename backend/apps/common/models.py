from django.db import models


# Create your models here.
class Articles(models.Model):
    title = models.CharField(max_length=32, verbose_name="文章标题")
    description = models.TextField(verbose_name="文章摘要")
    content = models.TextField(verbose_name="文章内容")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="发帖时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")
    is_active = models.BooleanField(default=True, verbose_name="是否有效")
    published = models.BooleanField(default=False, verbose_name="是否发布")
    json_raw = models.TextField(verbose_name="内容原始数据")


class Swipe(models.Model):
    url = models.URLField(verbose_name="图片url")


class Top(models.Model):
    title = models.CharField(max_length=32, verbose_name="标题")
    url = models.URLField(verbose_name="标题")
