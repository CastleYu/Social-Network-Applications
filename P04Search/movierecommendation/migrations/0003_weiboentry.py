# Generated by Django 5.0.4 on 2024-04-15 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movierecommendation', '0002_doubanmovieindex'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeiboEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blogger_nickname', models.CharField(max_length=150, verbose_name='博主昵称')),
                ('blogger_homepage', models.URLField(verbose_name='博主主页')),
                ('weibo_content', models.TextField(verbose_name='微博内容')),
                ('publish_time', models.DateTimeField(verbose_name='发布时间')),
                ('weibo_source', models.CharField(max_length=150, verbose_name='微博来源')),
                ('repost_count', models.IntegerField(default=0, verbose_name='转发数')),
                ('comment_count', models.IntegerField(default=0, verbose_name='评论数')),
                ('like_count', models.IntegerField(default=0, verbose_name='赞数')),
            ],
            options={
                'verbose_name': '微博条目',
                'verbose_name_plural': '微博条目',
            },
        ),
    ]
