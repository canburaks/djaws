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
    def dummyId(self):
        did = 1000000 +self.id
        return did

    def rate(self,target, rate,**kwargs):
            from items.models import Rating
            notes = kwargs.get("notes")
            date = kwargs.get("date")
            movid = target.id
            self.ratings.update({str(movid):float(rate)})
            target.ratings_user.add(str(self.id))

            r , created = Rating.objects.update_or_create(profile=self, movie=target)
            r.rating = rate
            r.notes = notes
            r.date = date
            r.save()

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


    def predict(self, target, **kwargs):
        from algorithm.models import  Dummy
        return Dummy.prediction(self, target)


    @property
    def points(self):
        return len(self.ratings["movie"])


def person_image_upload_path(instance, filename):
    return "person/{0}/pictures/{1}".format(instance.person.id,filename)

class Person(models.Model):

    id = models.CharField(primary_key=True, max_length=9,
        help_text="Use Imdb Id, if exists. " + 
        "Otherwise use prefix 'pp' with 7 digit number. \n" + 
        "E.g: \n If Imdb Id=nm0000759  than enter 'nm0000759' as Id.\n" + 
         "Otherwise: enter like 'pp0000001' or 'pp1700001'.(2letter(pp) + 7digit)")

    name = models.CharField(max_length=40)

    bio = models.CharField(max_length=1000, null=True)
    job = models.CharField(max_length=len(JOB), choices=JOB, null=True, blank=True)

    born = models.DateField(null=True, blank=True)
    died = models.DateField(null=True, blank=True)
    data = JSONField(blank=True,null=True)# {"job": ["director","writer", etc.]}
    
    relations = models.ManyToManyField("self", blank=True)


    def __str__(self):
        return self.name
    
class PersonImage(models.Model):
    person = models.ForeignKey(Person, related_name='images', on_delete=models.CASCADE)
    info = models.CharField(max_length=40, null=True,blank=True)
    image = models.ImageField(upload_to=person_image_upload_path)

    def __str__(self):
        return self.image.url
    @property
    def image_info(self):
        return {"info":self.info, "url":self.image.url}
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
