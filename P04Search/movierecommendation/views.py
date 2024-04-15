import json
import os
import re

import jieba
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from movierecommendation.models import DoubanMovie, DoubanMovieIndex


# 定义推荐页面.
def douban_recommendation(request):
    movie_list = DoubanMovie.objects.all().order_by('id')  # 取出DoubanMoview表所有数据并排序
    paginator = Paginator(movie_list, 3)  # 3是每页显示的数量，把数据库取出的数据生成paginator对象，并指定每页显示的数量
    page = request.GET.get('page')  # 从查询字符串获取page的当前页数
    data_list = []
    if page:  # 判断：获取当前页码的数据集，这样在模版就可以针对当前的数据集进行展示
        data_list = paginator.page(page).object_list
    else:
        data_list = paginator.page(1).object_list
    try:  # 实现分页对象，分别判断当页码存在/不存在的情况，返回当前页码对象
        page_object = paginator.page(page)
    except PageNotAnInteger:
        page_object = paginator.page(1)
    except EmptyPage:
        page_object = paginator.page(paginator.num_pages)
    return render(request, 'doubanRecommendation.html', {
        'page_object': page_object,
        'data_list': data_list
    })


# 定义索引请求链接.
@csrf_exempt
def buildindex(request):
    res = {
        'status': 404,
        'text': 'Unknown request!'
    }
    if request.method == 'POST':
        name = request.POST['id']
        if name == 'submit2index':
            # 初始化停用词列表
            # 注意：从网上下载一个较为全面完整的stopwords.txt用于本次任务。此处只是一个简单的示例文件
            stopwords = []
            static_filepath = os.path.join(settings.STATIC_ROOT, 'refs')
            file_path = os.path.join(static_filepath, 'stopwords.txt')
            for word in open(file_path, encoding='utf-8'):
                stopwords.append(word.strip())
            # 获取所有电影的文本属性用于索引
            movie_list = DoubanMovie.objects.values('id', 'movie_title', 'movie_keywords', 'movie_description')
            all_keywords = []
            movie_set = dict()
            for movie in movie_list:
                movie_id = movie['id']
                text = movie['movie_title'] + movie['movie_keywords'] + movie['movie_description']
                # 正则表达式去除非文字和数字的字符
                movie_text = re.sub(r'[^\w]+', '', text.strip())
                cut_text = jieba.cut(movie_text, cut_all=False)
                keywordlist = []
                for word in cut_text:
                    # 此处去停用词
                    if word not in stopwords:
                        keywordlist.append(word)
                all_keywords.extend(keywordlist)
                movie_set[movie_id] = keywordlist
            # 利用set删除重复keywords
            set_all_keywords = set(all_keywords)
            # 建立倒排索引
            for term in set_all_keywords:
                temp = []
                for m_id in movie_set.keys():
                    cut_text = movie_set[m_id]
                    if term in cut_text:
                        temp.append(m_id)
                # 存储索引到数据库
                try:
                    exist_list = DoubanMovieIndex.objects.get(movie_keyword=term)
                    exist_list.movie_doclist = json.dumps(temp)
                    exist_list.save()
                except ObjectDoesNotExist:
                    new_list = DoubanMovieIndex(movie_keyword=term, movie_doclist=json.dumps(temp))
                    new_list.save()
            res = {
                'status': 200,
                'text': 'Index successfully!'
            }
    return HttpResponse(json.dumps(res), content_type='application/json')


# 定义检索请求链接.
def searchindex(request):
    res = {
        'status': 404,
        'text': 'Unknown request!'
    }
    if request.method == 'GET':
        name = request.GET['id']
        if name == 'submit2search':
            try:
                # 获取前端的关键词
                keyword = request.GET['keyword']
                # 精确匹配索引关键词
                # 如何实现模糊匹配？
                invertedindex_rec = DoubanMovieIndex.objects.get(movie_keyword=keyword)
                # 将文档列表字符串转化成数组
                jsonDec = json.decoder.JSONDecoder()
                result = jsonDec.decode(invertedindex_rec.movie_doclist)
                # 查询电影ID在数组内的数据
                result_queryset = DoubanMovie.objects.filter(id__in=result).values()
                if result_queryset:
                    res = {
                        'status': 200,
                        'text': list(result_queryset)
                    }
                else:
                    res = {
                        'status': 201,
                        'text': 'No result!'
                    }
            except ObjectDoesNotExist:
                res = {
                    'status': 201,
                    'text': 'No result!'
                }
    return HttpResponse(json.dumps(res), content_type='application/json')
