from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django_mysql.models import JSONField
from django.core.cache import cache
JOB = (
    ('d', 'Director'),
    ('a', 'Actor/Actress'),
    ('w', 'Writer'),
    ('e', 'Editor'),
    ('f','Director of Photography'),
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
    follow_persons = models.ManyToManyField("persons.Person", related_name="followers", blank=True)
    follow_lists = models.ManyToManyField("items.List", related_name="followers", blank=True)
    follow_topics = models.ManyToManyField("items.Topic", related_name="followers", blank=True)

    def __str__(self):
        return self.username



    def follow_person(self, target_person):
        if target_person not in self.follow_persons.all():
            self.follow_persons.add(target_person)
            self.save()
        elif target_person in self.follow_persons.all():
            self.follow_persons.remove(target_person)
            self.save()

    def follow_topic(self, target_topic):
        if target_topic not in self.follow_topics.all():
            self.follow_topics.add(target_topic)
            self.save()
        elif target_topic in self.follow_topics.all():
            self.follow_topics.remove(target_topic)
            self.save()

    def follow_list(self, target_list):
        if target_list not in self.follow_lists.all():
            self.follow_lists.add(target_list)
            self.save()
        elif target_list in self.follow_lists.all():
            self.follow_lists.remove(target_list)
            self.save()

    @property
    def token(self):
        from graphql_jwt import shortcuts
        return shortcuts.get_token(self.user)

    @property
    def points(self):
        return self.rates.all().count()

    def rate(self,target, rate,**kwargs):
            from items.models import Rating
            from django.core.cache import cache
            notes = kwargs.get("notes")
            date = kwargs.get("date")
            movid = target.id
            self.ratings.update({str(movid):float(rate)})
            target.ratings_user.add(str(self.id))
            self.save()

            if len(self.ratings.keys())>39:
                self.cache_set(movid)

            r , created = Rating.objects.update_or_create(profile=self, movie=target)
            r.rating = rate
            if notes:
                r.notes = notes
            r.date = date
            r.save()

            self.save()
            target.save()
            print("Rate Added {} {}".format(r.movie, r.rating))

    def cache_set(self, movid):
        #Add user cache
        user_cache_id = str(self.user.id)
        user_cache = cache.get(user_cache_id)
        cache.set(user_cache_id, self.ratings, None)

        #Add movie cache
        movie_cache_id = "m{}".format(movid)
        movie_cache_list = cache.get(movie_cache_id)
        movie_cache_list.append(user_cache_id)
        cache.set(movie_cache_id, list(set(movie_cache_list)), None)


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


    def predict(self, target,zscore=True):
        print(target.name)
        if str(target.id) in self.ratings.keys():
            return 0
        from algorithm.models import  Rs
        from items.models import Prediction
        rs_user = Rs(str(self.user.id))

        result =  rs_user.prediction(target, zscore=zscore)
        result = round(result,1)
        points = self.points

        pred = Prediction.objects.create(profile=self, profile_points=points,
                movie=target, prediction=result )
        return result


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
    

    def __str__(self):
        return self.name
        
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)

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
