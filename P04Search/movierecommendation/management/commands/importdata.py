from datetime import datetime

import pandas as pd
from django.core.management import BaseCommand, call_command
from django.utils.timezone import make_aware

from movierecommendation.models import WeiboEntry


def parse_date(date_str):
    # 假设date_str是类似"2024年04月14日 00:02"的字符串
    # 使用strptime来进行转换
    dt = datetime.strptime(date_str, "%Y年%m月%d日 %H:%M")
    # 如果你的Django项目设置了时区支持，你还需要确保日期时间是"aware"的
    aware_dt = make_aware(dt)
    return aware_dt


class Command(BaseCommand):
    help = 'Import Weibo posts from an Xlsx file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The Excel file path.')

    def handle(self, *args, **kwargs):
        call_command('automigrate')
        file_path = kwargs['file_path']
        df = pd.read_excel(file_path)
        for index, row in df.iterrows():
            WeiboEntry.objects.create(
                blogger_nickname=row['博主昵称'],
                blogger_homepage=row['博主主页'],
                weibo_content=row['微博内容'],
                publish_time=parse_date(row['发布时间']),
                weibo_source=row['微博来源'],
                repost_count=row['转发'],
                comment_count=row['评论'],
                like_count=row['赞']
            )
        self.stdout.write(self.style.SUCCESS('Successfully imported Weibo posts'))
