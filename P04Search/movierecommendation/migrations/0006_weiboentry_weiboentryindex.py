# Generated by Django 5.0.4 on 2024-04-16 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movierecommendation', '0005_delete_weiboentry_delete_weiboentryindex'),
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
        migrations.CreateModel(
            name='WeiboEntryIndex',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=256, verbose_name='关键词')),
                ('doclist', models.TextField(verbose_name='文档列表')),
            ],
            options={
                'verbose_name': '微博索引',
                'verbose_name_plural': '微博索引',
            },
        ),
    ]