import os
import re

import jieba
from Levenshtein import distance as levenshtein_distance
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm

from movierecommendation.utils import *
from universe.quick_http import *


# 定义推荐页面
def weibo_recommendation(request):
    queryset = get_model_data(WeiboEntry)
    paginator, page_object = paginate_queryset(request, queryset, page_size=10)

    return render(request, 'weiboRecommendation.html', {
        'page_object': page_object,
        'data_list': page_object.object_list
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
        if name == 'create_new_index':
            # 初始化停用词列表 load Stopwords
            stopwords = []
            static_filepath = os.path.join(settings.STATIC_ROOT, 'resources')

            for word in open(os.path.join(static_filepath, 'baidu_stopwords.txt'), encoding='utf-8'):
                stopwords.append(word.strip())
            weibo_list = WeiboEntry.objects.values('id', 'weibo_content')
            all_keywords = []
            weibo_set = dict()
            for weibo in tqdm(weibo_list):
                weibo_id = weibo['id']
                # 正则表达式去除非文字和数字的字符
                weibo_text = re.sub(r'[^\w]+', '', weibo['weibo_content'].strip())
                cut_text = jieba.cut(weibo_text, cut_all=False)
                keywordlist = []
                for word in cut_text:
                    if word not in stopwords:
                        keywordlist.append(word)
                all_keywords.extend(keywordlist)
                weibo_set[weibo_id] = keywordlist
            # 利用set删除重复keywords
            set_all_keywords = set(all_keywords)
            set_all_keywords = list(set_all_keywords)
            # 建立倒排索引
            for term in tqdm(set_all_keywords):
                temp = []
                for w_id in weibo_set.keys():
                    cut_text = weibo_set[w_id]
                    if term in cut_text:
                        temp.append(w_id)
                # 存储索引到数据库
                try:
                    exist_list = WeiboEntryIndex.objects.get(keyword=term)
                    exist_list.doclist = json.dumps(temp)
                    exist_list.save()
                except ObjectDoesNotExist:
                    new_list = WeiboEntryIndex(keyword=term, doclist=json.dumps(temp))
                    new_list.save()
                    a
            res = {
                'status': 200,
                'text': 'Index successfully!'
            }
    return RespBuilder(res).build()


# 定义检索请求链接.
# def searchindex(request):
#     res = {
#         'status': 404,
#         'text': 'Unknown request!'
#     }
#     if request.method == 'GET':
#         try:
#             keyword = request.GET['keyword']
#             invertedindex_rec = WeiboEntryIndex.objects.get(keyword=keyword)
#             result = json.loads(invertedindex_rec.doclist)
#             result_queryset = WeiboEntry.objects.filter(id__in=result).values('blogger_nickname', 'weibo_content',
#                                                                               'publish_time', 'weibo_source',
#                                                                               'repost_count', 'comment_count',
#                                                                               'like_count')
#             if result_queryset:
#                 res = {
#                     'status': 200,
#                     'text': list(result_queryset)
#                 }
#             else:
#                 res = {
#                     'status': 201,
#                     'text': 'No result!'
#                 }
#         except ObjectDoesNotExist:
#             res = {
#                 'status': 201,
#                 'text': 'No result!'
#             }
#     return HttpResponse(json.dumps(res, cls=JsonEncodeWithDatetime), content_type='application/json')


def searchindex(request):
    res = {
        'status': 404,
        'text': 'Unknown request!'
    }
    if request.method == 'GET':
        keyword = request.GET.get('keyword', '')
        min_similarity_threshold = 20  # 相似度阈值设置为20%
        matches = []

        for index in WeiboEntryIndex.objects.all():
            max_len = max(len(index.keyword), len(keyword))
            if max_len == 0:  # 防止除零错误
                similarity = 0
            else:
                similarity = (1 - levenshtein_distance(index.keyword, keyword) / max_len) * 100

            if similarity >= min_similarity_threshold:
                result = json.loads(index.doclist)
                queryset = WeiboEntry.objects.filter(id__in=result).values('blogger_nickname', 'weibo_content',
                                                                           'publish_time', 'weibo_source',
                                                                           'repost_count', 'comment_count',
                                                                           'like_count')
                for item in queryset:
                    matches.append(item)

        if matches:
            res = {
                'status': 200,
                'text': matches
            }
        else:
            res = {
                'status': 201,
                'text': 'No results with sufficient similarity.'
            }

    return HttpResponse(json.dumps(res, cls=JsonEncodeWithDatetime), content_type='application/json')


# 定义推荐请求链接.
@csrf_exempt
def getrecmendation(request):
    res = {
        'status': 404,
        'text': 'Unknown request!'
    }
    if request.method == 'GET':
        # 获取当前需要推荐的微博ID
        weibo_id_cur = request.GET.get('id')
        if weibo_id_cur:
            try:
                print('start get_recommendation')
                weibo_top = None  # 记录top-1的结果，也可以修改代码返回top-k
                # 获取当前微博数据
                result = WeiboEntry.objects.get(id=weibo_id_cur)
                weibo_text = result.weibo_content
                # 排除当前微博的数据
                data_list = WeiboEntry.objects.exclude(weibo_content=weibo_text)[:500]

                if data_list:

                    # 使用Bert模型
                    model_bert = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

                    # 计算嵌入
                    embedding = model_bert.encode(weibo_text, convert_to_tensor=True)
                    cosine_score_top = -1

                    for data_rec in tqdm(data_list):
                        rec_embedding = model_bert.encode(data_rec.weibo_content, convert_to_tensor=True)
                        cosine_scores = util.pytorch_cos_sim(embedding, rec_embedding).item()
                        if cosine_scores > cosine_score_top:
                            cosine_score_top = cosine_scores
                            weibo_top = data_rec

                if weibo_top:
                    res = {
                        'status': 200,
                        'data': {
                            'id': weibo_top.id,
                            'blogger_nickname': weibo_top.blogger_nickname,
                            'blogger_homepage': weibo_top.blogger_homepage,
                            'weibo_content': weibo_top.weibo_content,
                            'publish_time': weibo_top.publish_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'weibo_source': weibo_top.weibo_source,
                            'repost_count': weibo_top.repost_count,
                            'comment_count': weibo_top.comment_count,
                            'like_count': weibo_top.like_count
                        }
                    }
                else:
                    res = {
                        'status': 201,
                        'data': 'No result!'
                    }
            except ObjectDoesNotExist:
                res = {
                    'status': 201,
                    'data': 'No result!'
                }
    return HttpResponse(json.dumps(res), content_type='application/json')