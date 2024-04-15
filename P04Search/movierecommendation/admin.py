from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from movierecommendation.models import DoubanMovie, DoubanMovieIndex


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
