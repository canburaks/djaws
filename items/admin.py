from django.contrib import admin
from .models import Video, List, Movie, MovieImage

class VideoMovieInline(admin.TabularInline):
    model = Video.related_movies.through
class ImageMovieInline(admin.TabularInline):
    model = MovieImage

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id",'name',"year","imdb_id","tmdb_id", "imdb_rating","poster" )
    inlines = [VideoMovieInline,ImageMovieInline,]
    search_fields = ('name', 'imdb_id',"tmdb_id", 'id',"videos__id" )
# Register your models here.
@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ("id",'name',"summary")

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("id",'title',"link")
    search_fields = ('id',"related_persons", 'title',"summary","videos__id" )


@admin.register(MovieImage)
class MovieImageAdmin(admin.ModelAdmin):
    list_display = ("id","movie","info","image" )

