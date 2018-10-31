from django.db import models
from persons.models import Person, Profile
from django.urls import reverse
from django_mysql.models import JSONField, SetTextField, ListCharField, SetCharField

# Create your models here.
class List(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=400)
    summary = models.TextField(max_length=1000,null=True)
    #tags = JSONField(default=dict,blank=True, null=True)
    movies = models.ManyToManyField("Movie")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-id"]


def item_image_upload_path(instance, filename):
    return "posters/{0}/{1}".format(instance.movie.id,filename)


class Movie(models.Model):
    id = models.IntegerField(primary_key=True)
    imdb_id = models.CharField(max_length=9, null=True)
    tmdb_id = models.IntegerField(null=True)

    name = models.CharField(max_length=100)
    year = models.IntegerField(null=True)
    summary = models.TextField(max_length=5000,null=True)

    imdb_rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    poster = models.ImageField(blank=True, upload_to="posters/")
    director = models.ForeignKey(Person, on_delete=models.CASCADE, null=True,blank=True, related_name="movies")
    actors = models.ForeignKey(Person, on_delete=models.CASCADE, null=True,blank=True, related_name="acted")
    
    tags = SetTextField(default=set(), base_field=models.CharField(max_length=15), null=True, blank=True)
    data = JSONField(default=dict)
    ratings_user = SetCharField(default=set(),max_length=15, base_field=models.IntegerField(),null=True, blank=True)
    ratings_dummy = SetCharField(default=set(),max_length=15, base_field=models.CharField(max_length=15),null=True, blank=True)
    
    @property
    def shortName(self):
        if len(self.name)>10:
            return "{}...".format(self.name[:10])
        else:
            return self.name

    def __str__(self):
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


class MovieImage(models.Model):
    movie = models.ForeignKey(Movie, related_name='images', on_delete=models.CASCADE)
    info = models.CharField(max_length=40, blank=True, null=True)
    image = models.ImageField(blank=True, upload_to=item_image_upload_path)

    def __str__(self):
        return self.image.url
    @property
    def image_info(self):
        return {"info":self.info, "url":self.image.url}

class Video(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=150)
    summary = models.CharField(max_length=2000, null=True, blank=True)

    link = models.URLField()
    duration = models.IntegerField(null=True,blank=True, help_text="seconds")

    related_persons = models.ManyToManyField(Person, blank=True, related_name="videos")
    related_movies = models.ManyToManyField(Movie, blank=True, related_name="videos")

    def __str__(self):
        return self.title