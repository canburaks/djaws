from django.contrib import admin
from .models import Profile, Person, Director,PersonImage
from items.models import Video
# Register your models here.

class VideoPersonInline(admin.TabularInline):
    model = Video.related_persons.through

class ImagePersonInline(admin.TabularInline):
    model = PersonImage

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",'username',)

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("id",'name',)
    inlines = [VideoPersonInline,ImagePersonInline,]
    search_fields = ('name', 'id', )
@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ("id",'name',)
    inlines = [VideoPersonInline,ImagePersonInline,]
    search_fields = ('name', 'id', )
@admin.register(PersonImage)
class PersonImageAdmin(admin.ModelAdmin):
    list_display = ("id","person","info","image" )