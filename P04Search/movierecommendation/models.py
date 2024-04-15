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


# 创建索引表
class DoubanMovieIndex(models.Model):
    movie_keyword = models.CharField(max_length=256)
    movie_doclist = models.TextField()

    def __str__(self):
        return self.movie_keyword
