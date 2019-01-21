from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django_mysql.models import JSONField

FOLLOW_TYPE = (
    ('u', 'Profile'),
    ('p', 'Person'),
    ('l', 'Liste'),
    ('t', 'Topic'),
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
    videos = models.ManyToManyField("items.Video", related_name="fav")
    liked_movies = models.ManyToManyField("items.Movie", related_name="liked")

    def __str__(self):
        return self.username

    def follow_profile(self, target_profile):
        Follow.follow_profile(profile=self, target_profile=target_profile)

    def follow_person(self, target_person):
        Follow.follow_person(profile=self, person=target_person)

    def follow_topic(self, target_topic):
        Follow.follow_topic(profile=self, topic=target_topic)

    def follow_list(self, target_list):
        Follow.follow_liste(profile=self, liste=target_list)



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

            if len(self.ratings.keys())>39 and len(self.ratings.keys())%10==0:
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
        from items.models import Rating
        from django.core.cache import cache
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

    def fav(self, target, type):

        if type.lower().startswith("v"):
            if target not in self.videos.all():
                self.videos.add(target)
                self.save()
            elif target in self.videos.all():
                self.videos.remove(target)
                self.save()

        elif type.lower().startswith("m"):
            if target not in self.liked_movies.all():
                self.liked_movies.add(target)
                self.save()
            elif target in self.liked_movies.all():
                self.liked_movies.remove(target)
                self.save()


    def predict(self, target,zscore=True):
        
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


class Follow(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="following")
    
    target_profile = models.ForeignKey(Profile, on_delete=models.CASCADE,  null=True,
            blank=True, related_name="followers")
    person = models.ForeignKey("persons.Person", on_delete=models.CASCADE,  null=True,
            blank=True, related_name="followers")
    liste = models.ForeignKey("items.List", on_delete=models.CASCADE,  null=True,
            blank=True, related_name="followers")
    topic = models.ForeignKey("items.Topic", on_delete=models.CASCADE,  null=True,
            blank=True, related_name="followers")

    typeof = models.CharField(max_length=1, choices=FOLLOW_TYPE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("profile","target_profile"), ("profile", "person"),
                ("profile", "liste"), ("profile","topic"),)

    def __str__(self):
        if self.target_profile:
            target =  self.target_profile.username
        elif self.person:
            target = self.person.name
        elif self.liste:
            target = self.liste.name
        elif self.topic:
            target = self.topic.name
        
        return "{}---{}".format(self.profile.username, target)

    @classmethod
    def follow_profile(cls, profile, target_profile):
        qs = cls.objects.filter(profile=profile, target_profile=target_profile)
        if qs.count()==0:
            cls(profile=profile, target_profile=target_profile, typeof="u").save()
        else:
            unfollow = qs[0]
            unfollow.delete()

    @classmethod
    def follow_person(cls, profile, person):
        qs = cls.objects.filter(profile=profile, person=person)
        if qs.count()==0:
            cls(profile=profile, person=person, typeof="p").save()
        else:
            unfollow = qs[0]
            unfollow.delete()

    @classmethod
    def follow_liste(cls, profile, liste):
        qs = cls.objects.filter(profile=profile, liste=liste)
        if qs.count()==0:
            cls(profile=profile, liste=liste, typeof="l").save()
        else:
            unfollow = qs[0]
            unfollow.delete()

    @classmethod
    def follow_topic(cls, profile, topic):
        qs = cls.objects.filter(profile=profile, topic=topic)
        if qs.count()==0:
            cls(profile=profile, topic=topic, typeof="t").save()
        else:
            unfollow = qs[0]
            unfollow.delete()



#######################################################################################
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