from datetime import datetime
from typing import Type

from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import QuerySet

from movierecommendation.models import *


def get_model_data(cls: Type[models.Model]):
    return cls.objects.all().order_by('id')


def paginate_queryset(request: WSGIRequest, queryset: QuerySet, page_size=10):
    """
    分页函数
    :param request: (HttpRequest) 用于获取页码
    :param queryset: (Django QuerySet) 数据集
    :param page_size: 页大小
    :returns: 分页对象, 当前页面的数据
    """
    page = request.GET.get('page')
    paginator = Paginator(queryset, page_size)

    try:
        current_page = paginator.page(page)
    except PageNotAnInteger:
        current_page = paginator.page(1)
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)

    return paginator, current_page


from django.core.serializers.json import DjangoJSONEncoder


# 自定义一个JSON Encoder，继承自DjangoJSONEncoder以处理datetime和其他Django特有的数据类型
class JsonEncodeWithDatetime(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            # 格式化datetime对象为字符串
            return obj.strftime('%Y-%m-%d %H:%M:%S %Z')
        return super().default(obj)
