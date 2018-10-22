from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django_mysql.models import JSONField
JOB = (
    ('d', 'Director'),
    ('a', 'Actor/Actress'),
    ('w', 'Writer'),
)

class Profile(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
        verbose_name=("user"),on_delete=models.CASCADE)
    username = models.CharField(max_length=40, null=True)
    name = models.CharField(max_length=40, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True)
    joined = models.DateField(null=True, blank=True)
    born = models.DateField(null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    ratings = JSONField(default=dict)
    bookmarks = models.ManyToManyField("items.Movie", related_name="bookmarked")
    #bookmarks = models.ManyToManyField("items.Movie")

    def __str__(self):
        return self.username
    
    @property
    def token(self):
        from graphql_jwt import shortcuts
        return shortcuts.get_token(self.user)
    @property
    def dummyId(self):
        did = 1000000 +self.id
        return did

    def rate(self,target, rate, item="Movie"):
            movid = target.id
            self.ratings.update({int(movid):float(rate)})
            target.ratings_user.add(self.id)
            self.save()
            target.save()
            print("Rate Added")


    def isBookmarked(self,target):
        return target in self.bookmarks.all()

    def bookmarking(self, target, item="Movie"):
        if item=="Movie":
            if target not in self.bookmarks.all():
                self.bookmarks.add(target)
                self.save()
            elif target in self.bookmarks.all():
                self.bookmarks.remove(target)
                self.save()
            return self.isBookmarked(target)


    def predict(self, target, **kwargs):
        from algorithm.models import  Dummy
        try:
            result = Dummy.prediction(self, target,**kwargs)
        except:
            result = 0
        return result

    def convInt(self):
        oldrates = self.ratings["movie"]
        newrates = {int(key):val for key,val in oldrates.items()}
        self.ratings["movie"] = newrates
        self.save()


    @property
    def points(self):
        return len(self.ratings["movie"])




class Person(models.Model):

    id = models.CharField(primary_key=True, max_length=9,
        help_text="Use Imdb Id, if exists. " + 
        "Otherwise use prefix 'pp' with 7 digit number. \n" + 
        "E.g: \n If Imdb Id=nm0000759  than enter 'nm0000759' as Id.\n" + 
         "Otherwise: enter like 'pp0000001' or 'pp1700001'.(2letter(pp) + 7digit)")

    name = models.CharField(max_length=40)

    bio = models.CharField(max_length=1000, null=True)
    job = models.CharField(max_length=len(JOB), choices=JOB, null=True)
    pictures = models.ImageField(blank=True, upload_to="person/pictures/")

    born = models.DateField(null=True, blank=True)
    died = models.DateField(null=True, blank=True)
    data = JSONField(blank=True,null=True)# {"job": ["director","writer", etc.]}
    
    relations = models.ManyToManyField("self", blank=True)


    def __str__(self):
        return self.name


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


def post_save_user_model_receiver(sender, instance, created, *args, **kwargs):
    if created:
        try:
            if (instance.first_name and instance.last_name):
                name = "{} {}".format(instance.first_name, instance.last_name)
            else:
                name=None
            p = Profile(user=instance, email=instance.email, username=instance.username,joined= instance.date_joined, name=name)
            p.save()
        except:
            print("Error:")
post_save.connect(post_save_user_model_receiver, sender=settings.AUTH_USER_MODEL)
