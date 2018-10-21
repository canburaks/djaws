from django.contrib import admin
from .models import Profile, Person, Director
# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",'username',)

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("id",'name',)

@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ("id",'name',)
