from django.urls import re_path as url
from movierecommendation import views

urlpatterns = [
    url(r'^movieRecommendation', views.weibo_recommendation, name='movieRecommendation'),
    url(r'^buildindex', views.buildindex, name='weiboIndex'),
    url(r'^searchindex', views.searchindex, name='searchIndex')
]
