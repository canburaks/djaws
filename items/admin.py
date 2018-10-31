from django.contrib import admin
from .models import Video, List,Movie

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id",'name',"year","imdb_id","tmdb_id", "imdb_rating","poster" )
# Register your models here.
@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ("id",'name',"summary")

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("id",'title',"link", "duration")