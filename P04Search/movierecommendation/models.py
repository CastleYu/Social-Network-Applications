from django.db import models


# Create your models here.
class DoubanMovie(models.Model):
    movie_url = models.CharField(max_length=256)
    movie_title = models.CharField(max_length=64)
    movie_keywords = models.TextField()
    movie_description = models.TextField()
    movie_directors = models.TextField()
    movie_actors = models.TextField()

    def __str__(self):
        return self.movie_title


class WeiboEntry(models.Model):
    blogger_nickname = models.CharField(max_length=150, verbose_name="博主昵称")
    blogger_homepage = models.URLField(verbose_name="博主主页")
    weibo_content = models.TextField(verbose_name="微博内容")
    publish_time = models.DateTimeField(verbose_name="发布时间")
    weibo_source = models.CharField(max_length=150, verbose_name="微博来源")
    repost_count = models.IntegerField(default=0, verbose_name="转发数")
    comment_count = models.IntegerField(default=0, verbose_name="评论数")
    like_count = models.IntegerField(default=0, verbose_name="赞数")

    class Meta:
        verbose_name = "微博条目"
        verbose_name_plural = "微博条目"

    def __str__(self):
        return self.blogger_nickname


# 创建索引表
class DoubanMovieIndex(models.Model):
    movie_keyword = models.CharField(max_length=256)
    movie_doclist = models.TextField()

    def __str__(self):
        return self.movie_keyword
