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

def avatar_upload_path(instance, filename):
    return "avatars/{0}/{1}".format(instance.id,filename)

class Profile(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
        verbose_name=("user"),on_delete=models.CASCADE)
    username = models.CharField(max_length=40, null=True, unique=True)
    bio = models.CharField(default="...", max_length=140, null=True, blank=True)
    avatar = models.ImageField(blank=True, upload_to=avatar_upload_path)

    name = models.CharField(max_length=40, null=True, blank=True)
    email = models.EmailField(max_length=50, null=True)
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

    def rating_movieset(self):
        return self.rates.values_list("movie_id", flat=True)

    @property
    def token(self):
        from graphql_jwt import shortcuts
        return shortcuts.get_token(self.user)

    @property
    def points(self):
        return len(self.ratings.keys())

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

    @property
    def archive(self):
        from archive.models import  UserArchive
        qs = UserArchive.objects.filter(user_id=self.user.id, user_type="u").only("user_id", "user_type")
        if qs.exists():
            ua = qs[0]
            ua.ratings = self.ratings
            int_movieset = {int(x) for x in self.ratings.keys()}
            ua.movieset = int_movieset
            ua.save()
            return ua
        else:
            int_movieset = {int(x) for x in self.ratings.keys()}
            ua = UserArchive(user_id= self.user.id, user_type="u", ratings= self.ratings, movieset=int_movieset)
            ua.save()
            return ua

    def rate(self,target, rate,**kwargs):
            from items.models import Rating
            from archive.models import UserArchive, MovieArchive
            notes = kwargs.get("notes")
            date = kwargs.get("date")

            movid = target.id            
            self.ratings.update({str(movid):float(rate)})

            if len(self.ratings.keys())>20:
                #Archive objects
                ma = MovieArchive.objects.get(movie_id=movid)
                ua = self.archive
                ma.userset.add(self.user.id)
                ua.movieset.add(int(movid))
                ma.save()
                ua.save()

            r , created = Rating.objects.update_or_create(profile=self, movie=target)
            r.rating = rate
            if notes:
                r.notes = notes
            r.date = date
            r.save()
            self.save()
            print("Rate Added {} {}".format(r.movie, r.rating))

    def predict(self, target,zscore=True):
        from items.models import Prediction
        movie_id = target.id
        if movie_id in self.ratings.keys():
            return 0
        ua = self.archive
        result = ua.post_prediction(movie_id)
        points = self.points

        pred = Prediction.objects.create(profile=self, profile_points=points,
                movie=target, prediction=result )
        return round(result,1)


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

"""
class Message(models.Model):
    
    sender = models.ForeignKey(Profile, on_delete=models.DO_NOTHING, related_name="sents")
    receiver = models.ForeignKey(Profile, on_delete=models.DO_NOTHING, related_name="messages")

    movie = models.ForeignKey("items.Movie", on_delete=models.DO_NOTHING,related_name="suggested")
    message = models.TextField(max_length=250,null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    watched_before = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    class Meta:
        unique_together = ("sender","movie", "receiver")

    def __str__(self):
        return "{} - {}".format(self.sender.username, self.receiver.username)

    def save(self, *args, **kwargs):
        if not self.pk:
            from items.models import Rating
            qs = Rating.objects.filter(movie=self.movie, profile=self.receiver)
            if qs.count()==1:
                self.watched_before = True
                self.rating = qs[0].rating
            elif qs.count()==0:
                self.watched_before = False
        super(Message, self).save(*args, **kwargs)

"""
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