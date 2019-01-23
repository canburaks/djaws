from django.db import models
from persons.models import Person
from persons.profile import Profile
from django.urls import reverse
from django_mysql.models import (JSONField, SetTextField, ListTextField, SetCharField)
from django.utils.functional import cached_property
from django.conf import settings

def item_image_upload_path(instance, filename):
    return "posters/{0}/{1}".format(instance.movie.id,filename)

def movie_poster_upload_path(instance, filename):
    return "posters/{0}/{1}".format(instance.id,filename)

def topic_image_upload_path(instance, filename):
    return "topics/{0}/{1}".format(instance.name, filename)


class Movie(models.Model):
    id = models.IntegerField(primary_key=True)
    imdb_id = models.CharField(max_length=9, null=True)
    tmdb_id = models.IntegerField(null=True)

    name = models.CharField(max_length=100)
    year = models.IntegerField(null=True, db_index=True)
    summary = models.TextField(max_length=5000,null=True)

    imdb_rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    poster = models.ImageField(blank=True, upload_to=movie_poster_upload_path)
    director = models.ForeignKey(Person, on_delete=models.CASCADE, null=True,blank=True, related_name="movies")

    people =  models.ManyToManyField(Person,
        through='persons.Crew', through_fields=('movie', 'person'),null=True, blank=True)

    tags = ListTextField(default = list(),base_field=models.CharField(max_length=20),
                    max_length=20, null=True, blank=True)
    
    data = JSONField(default=dict)
    ratings_user = SetTextField(default=set(), base_field=models.CharField(max_length=15),null=True, blank=True)
    ratings_dummy = SetTextField(default=set(), base_field=models.CharField(max_length=15),null=True, blank=True)
    class Meta:
        ordering = ["-year"]

    def __str__(self):
        return self.name
    
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)

    @property
    def mini_data(self):
        data_keys = ["Country", "Genre", "Runtime", "Language"]

    @property
    def shortName(self):
        if len(self.name)>10:
            return "{}...".format(self.name[:10])
        else:
            return self.name

    def get_absolute_url(self):
        "Returns the url to access a particular movie instance."
        return reverse('movie-detail', args=[str(self.id)])
        
    @property
    def image(self):
        return self.poster.url

    def setOmdbInfo(self):
        from .outerApi import omdb_details
        if self.summary:
            return 0
        if self.imdb_id:
            imdbId=self.imdb_id
        try:
            resp = omdb_details(imdbId)
            if resp.get("imdbRating")!="N/A":
                self.imdb_rating = float(resp.get("imdbRating"))
            if resp.get("Director")!="N/A":
                d = resp.get("Director")
                self.data.update({"Director":d})
            if resp.get("Actors")!="N/A":
                a = resp.get("Actors")
                self.data.update({"Actors":a})

            if resp.get("Plot")!="N/A":
                p = resp.get("Plot")
                if len(p)>5000:
                    print("long summary",self.id, self.name, sep=",")
                else:
                    self.summary = p
                    self.data.update({"Plot":p})

            if resp.get("Website")!="N/A":
                w = resp.get("Website")
                self.data.update({"Website":w})


            if resp.get("Genre")!="N/A":
                g = resp.get("Genre")
                self.data.update({"Genre":g})

            if resp.get("Metascore")!="N/A":
                m = resp.get("Metascore")
                self.data.update({"Metascore":int(m)})

            if resp.get("Runtime")!="N/A":
                run = resp.get("Runtime")
                self.data.update({"Runtime":run})

            if resp.get("Country")!="N/A":
                coun = resp.get("Country")
                self.data.update({"Country":coun})

            if resp.get("Language")!="N/A":
                lang = resp.get("Language")
                self.data.update({"Language":lang})

            if resp.get("imdbVotes")!="N/A":
                vote = resp.get("imdbVotes")
                vote = vote.replace(",","")
                self.data.update({"imdbVotes":int(vote)})
            self.save()
            print("Info was set:" + self.name)
        except:
            print("could not get:",self.id, self.name, sep=",")

    def setTmdbInfo(self, force=False):
            from .outerApi import getPosterUrlAndSummary

            from django.core import files
            from io import BytesIO
            import requests
            if self.tmdb_id:
                try:
                    tmdb = self.tmdb_id
                    pUrl, overview, year = getPosterUrlAndSummary(tmdb)
                    if self.poster=="" or self.poster==None or force==True:
                        try:
                            resp = requests.get(pUrl)
                            fp = BytesIO()
                            fp.write(resp.content)
                            file_name = "{0}/{0}-tmdb.jpg".format(str(self.id))

                            self.poster.save(file_name, files.File(fp))
                            print("Movie Poster:{} saved.".format(self.id))
                        except:
                            print("request error")
                    if self.summary==None or self.summary=="":
                        self.summary = overview
                        self.save()
                        print("Movie:{} saved.".format(self.id))
                except:
                    print("error Id:{}".format(self.id))

    def getCastCrew(self):
        from gql import tmdb_class as t
        if self.tmdb_id:
            tmovie = t.Movie(self.tmdb_id)
            cast, crew = tmovie.credits()
            if cast:
                self.data.update({"cast":cast[:8]})
            if crew:
                self.data.update({"crew":crew})
            self.save()


class MovieImage(models.Model):
    movie = models.ForeignKey(Movie, related_name='images', on_delete=models.CASCADE)
    info = models.CharField(max_length=40, blank=True, null=True)
    image = models.ImageField(blank=True, upload_to=item_image_upload_path)

    def __str__(self):
        return self.image.url
    @property
    def image_info(self):
        return {"info":self.info, "url":self.image.url}

class List(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    summary = models.TextField(max_length=1000,null=True, blank=True)
    #tags = JSONField(default=dict,blank=True, null=True)
    movies = models.ManyToManyField(Movie,null=True, blank=True, related_name="lists")

    owner = models.ForeignKey(Profile, related_name='lists', on_delete=models.DO_NOTHING)
    public = models.BooleanField(default=True)

    related_persons = models.ManyToManyField(Person, null=True, blank=True,  related_name="related_lists")
    reference_notes = models.CharField(max_length=400, null=True, blank=True, help_text="Notes about reference.")
    reference_link = models.URLField(null=True, blank=True, help_text="Reference of relation with person. Enter link of url")


    def __str__(self):
        return self.name
    
    @classmethod
    def autokey(cls):
        return cls.objects.all().order_by("-id")[0].id + 1

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)

    @cached_property
    def get_movies(self):
        return self.movies.all()
    
    @property
    def image(self):
        aws = settings.MEDIA_URL
        posters = self.movies.order_by("?").values("poster")
        poster_urls = ["{}{}".format(aws,i["poster"]) for i in posters][:10]
        dictionary = {"id":self.id, "name":self.name, "summary":self.summary, "thumbs":poster_urls}
        return dictionary


"""
    @property
    def items(self):
        aws = settings.MEDIA_URL
        movies = self.movies.defer("imdb_id",
                "tmdb_id","actors","data","ratings_dummy","director","summary","tags","ratings_user")
        movie_dictionary = [{"name":i["name"], "id":i["id"], "poster":"{}{}".format(aws,i["poster"])} for i in movies]
        return movies
"""

class Topic(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=400)
    summary = models.TextField(max_length=1000,null=True, blank=True)
    content = models.TextField(max_length=5000,null=True, blank=True)
    #tags = JSONField(default=dict,blank=True, null=True)
    poster = models.ImageField(blank=True, upload_to=topic_image_upload_path)
    
    movies = models.ManyToManyField(Movie, null=True, blank=True,  related_name="topics")
    lists = models.ManyToManyField(List, null=True, blank=True,  related_name="topics")
    persons = models.ManyToManyField(Person, null=True, blank=True,  related_name="topics")

    def __str__(self):
        return self.name
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)

class Video(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=150)
    summary = models.CharField(max_length=2000, null=True, blank=True)
    link = models.URLField()
    tags = ListTextField(default = list(),base_field=models.CharField(max_length=40),
                    null=True, help_text="Enter the type of video category.\n E.g:'video-essay or interview or conversations'")
    duration = models.IntegerField(null=True,blank=True, help_text="seconds")
    thumbnail = models.URLField(null=True, blank=True, help_text="Thumbnail url if exists.")
    youtube_id = models.CharField(max_length=50, null=True, blank=True, help_text="Youtube video id, if video is on TouTube.")
    channel_url = models.URLField(null=True, blank=True, help_text="Youtube channel's main page link")
    channel_name = models.CharField(max_length=150, null=True, blank=True, help_text="Name of the Youtube channel")

    related_persons = models.ManyToManyField(Person, blank=True, related_name="videos")
    related_movies = models.ManyToManyField(Movie, blank=True, related_name="videos")
    related_topics = models.ManyToManyField(Topic, blank=True, related_name="videos")
    def __str__(self):
        return self.title
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "title__icontains",)

class Article(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=250)
    abstract = models.CharField(max_length=2000, null=True, blank=True)
    content = models.TextField(max_length=20000, null=True, blank=True)
    link = models.URLField(null=True, blank=True)

    related_persons = models.ManyToManyField(Person, blank=True, related_name="articles")
    related_movies = models.ManyToManyField(Movie, blank=True, related_name="articles")
    related_topics = models.ManyToManyField(Topic, blank=True, related_name="articles")
    
    def __str__(self):
        return self.title
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)
        
class Rating(models.Model):
    profile = models.ForeignKey(Profile, related_name='rates', on_delete=models.DO_NOTHING)
    movie = models.ForeignKey(Movie, related_name='rates', on_delete=models.DO_NOTHING)
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)

    notes = models.CharField(max_length=2500, blank=True, null=True)
    date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("profile","movie",)

    def __str__(self):
        return "Profile: {}, Movie: {}, Ratings:{}".format(self.profile, self.movie,self.rating)

class Prediction(models.Model):
    profile = models.ForeignKey(Profile, related_name='predictions', on_delete=models.DO_NOTHING)
    profile_points = models.IntegerField()

    movie = models.ForeignKey(Movie, related_name='predictions', on_delete=models.DO_NOTHING)
    prediction = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return "Profile: {}, Movie: {}, Prediction:{}".format(self.profile, self.movie,self.prediction)