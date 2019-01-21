from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django_mysql.models import JSONField
from django.core.cache import cache
from .profile import Profile
JOB = (
    ('d', 'Director'),
    ('a', 'Actor/Actress'),
    ('w', 'Writer'),
    ('e', 'Editor'),
    ('f','Director of Photography'),
)


def person_image_upload_path(instance, filename):
    return "person/{0}/pictures/{1}".format(instance.person.id,filename)

def person_poster_upload_path(instance, filename):
    return "person/{0}/pictures/{1}".format(instance.id,filename)
    
class Person(models.Model):

    id = models.CharField(primary_key=True, max_length=9,
        help_text="Use Imdb Id, if exists. " + 
        "Otherwise use prefix 'pp' with 7 digit number. \n" + 
        "E.g: \n If Imdb Id=nm0000759  than enter 'nm0000759' as Id.\n" + 
         "Otherwise: enter like 'pp0000001' or 'pp1700001'.(2letter(pp) + 7digit)")
    tmdb_id = models.IntegerField(null=True, blank=True, db_index=True, unique=True)
    name = models.CharField(max_length=40)

    bio = models.CharField(max_length=6000, null=True)
    job = models.CharField(max_length=len(JOB), choices=JOB, null=True, blank=True,)

    born = models.DateField(null=True, blank=True)
    died = models.DateField(null=True, blank=True)
    data = JSONField(blank=True,null=True)# {"job": ["director","writer", etc.]}
    active = models.BooleanField(default=False, help_text="if ready for show on web page make it true")
    poster = models.ImageField(blank=True, upload_to=person_poster_upload_path)
    
    #relations = models.ManyToManyField("self", blank=True)


    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact","tmdb_id__iexact", "name__icontains",)


class Crew(models.Model):
    movie = models.ForeignKey("items.Movie", on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    job = models.CharField(max_length=len(JOB), choices=JOB, null=True, blank=True)
    data = JSONField(blank=True,null=True)#
    character = models.TextField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.person.name

##########################################################################################
class PersonImage(models.Model):
    person = models.ForeignKey(Person, related_name='images', on_delete=models.CASCADE)
    info = models.CharField(max_length=40, null=True,blank=True)
    image = models.ImageField(upload_to=person_image_upload_path)

    def __str__(self):
        return self.image.url
    @property
    def image_info(self):
        return {"info":self.info, "url":self.image.url}
#######################################################################################
# DIRECTOR PROXY MODEL
class DirectorManager(models.Manager):
    def get_queryset(self):
        return super(DirectorManager, self).get_queryset().filter(job='d')

    def create(self, **kwargs):
        kwargs.update({'job': 'd'})
        return super(DirectorManager, self).create(**kwargs)

class Director(Person):
    objects = DirectorManager()
    class Meta:
        proxy = True
#####################################################################################

# ACTOR PROXY MODEL
class ActorManager(models.Manager):
    def get_queryset(self):
        return super(ActorManager, self).get_queryset().filter(job='a')

    def create(self, **kwargs):
        kwargs.update({'job': 'a'})
        return super(ActorManager, self).create(**kwargs)

class Actor(Person):
    objects = ActorManager()
    class Meta:
        proxy = True
######################################################################################




