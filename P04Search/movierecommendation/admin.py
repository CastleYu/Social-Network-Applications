import json

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from movierecommendation.models import DoubanMovie, DoubanMovieIndex
from .models import WeiboEntry, WeiboEntryIndex


class WeiboEntryAdmin(admin.ModelAdmin):
    list_display = ('blogger_nickname', 'publish_time', 'weibo_source', 'repost_count', 'comment_count', 'like_count')
    search_fields = ('blogger_nickname', 'weibo_content')
    list_filter = ('publish_time', 'weibo_source')


class WeiboEntryIndexAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'doclist')
    search_fields = ('keyword',)

    def doclist_display(self, obj):
        # 展示文档列表的一部分或进行格式化以便于阅读
        return ', '.join(json.loads(obj.doclist)[:10])  # 显示前10个文档ID

    doclist_display.short_description = 'Document List (preview)'


admin.site.register(WeiboEntry, WeiboEntryAdmin)
admin.site.register(WeiboEntryIndex, WeiboEntryIndexAdmin)


# Register your models here.
class MovieResource(resources.ModelResource):
    class Meta:
        model = DoubanMovie
        export_order = (
            'movie_url', 'movie_title', 'movie_keywords', 'movie_description', 'movie_directors', 'movie_actors')


@admin.register(DoubanMovie)
class MovieAdmin(ImportExportModelAdmin):
    list_display = (
        'movie_url', 'movie_title', 'movie_keywords', 'movie_description', 'movie_directors', 'movie_actors')
    search_fields = ('movie_title', 'movie_keywords', 'movie_description', 'movie_directors', 'movie_actors')
    resource_class = MovieResource


class MovieIndexResource(resources.ModelResource):
    class Meta:
        model = DoubanMovieIndex
        export_order = ('movie_keyword', 'movie_doclist')


@admin.register(DoubanMovieIndex)
class MovieIndexAdmin(ImportExportModelAdmin):
    list_display = ('movie_keyword', 'movie_doclist')
    search_field = 'movie_keyword'
    resource_class = MovieIndexResource
