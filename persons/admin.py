from django.contrib import admin
from .models import Profile, Person, Director,Actor, PersonImage, Crew
from items.models import Video, Movie
# Register your models here.

class VideoPersonInline(admin.TabularInline):
    model = Video.related_persons.through

class ImagePersonInline(admin.TabularInline):
    model = PersonImage

class MoviePersonInline(admin.TabularInline):
    model = Movie

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",'username',)

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("id","tmdb_id",'name',"job")
    list_filter = ('active',"job")
    inlines = [ImagePersonInline,]
    list_display_links = ("name",)
    search_fields = ('name', 'id', )

@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ("id",'name',)
    inlines = [ImagePersonInline,]
    search_fields = ('name', 'id', )

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ("id",'name',)
    inlines = [ImagePersonInline,]
    search_fields = ('name', 'id', )

@admin.register(PersonImage)
class PersonImageAdmin(admin.ModelAdmin):
    list_display = ("id","person","info","image" )

@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("person",'movie',"job")
