from items.models import Rating,Movie, List, MovieImage, Video, Topic, Prediction
from persons.models import Person, PersonImage, Director, Crew
from persons.profile import Profile, Follow
from django.contrib.auth import get_user_model
import graphene
from django_mysql.models import JSONField
from graphene_django.types import DjangoObjectType
from graphene_django.converter import convert_django_field
from django.db.models import Q
from django_countries import countries

@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return graphene.String()


def is_owner(self, info):
    user = info.context.user
    if user.username == self.username:
        return True
    return False

movie_defer = ("imdb_id","tmdb_id","data",
        "director","summary","tags", "tags")



class CountryType(graphene.ObjectType):
    country = graphene.List(graphene.String)
    

    def __init__(self,code=None, num=None):
        self.code = code
        self.num = num

    def resolve_country(self, info):
        if self.code:
            return dict(countries).get(self.code)
        elif self.num:
            if list(countries)[self.num]:
                c =  list(countries)[self.num]
                return [c.name, c.code]

class VideoType(DjangoObjectType):
    tags = graphene.List(graphene.String)
    isFaved = graphene.Boolean()
    thumb = graphene.String()
    yt_id = graphene.String()

    related_movies = graphene.List("gql.types.CustomMovieType")
    related_persons = graphene.List("gql.types.DirectorPersonMixType")


    class Meta:
        model=Video

    def resolve_yt_id(self, info, *_):
        if self.youtube_id:
            return self.youtube_id
        else:
            url = self.link
            if "youtube" in url:
                try:
                    defer_web = url.split("v=")[1]
                    yt_id = defer_web.split("&")[0]
                    return yt_id
                except:
                    return None            

    def resolve_related_movies(self, info, *_):
        from gql.types import CustomMovieType
        movs = self.related_movies.only("id", "name").all()
        if movs:
            custom_movie_list = [CustomMovieType(x.id) for x in movs]
        else:
            return []

    def resolve_related_persons(self, info, *_):
        from gql.types import DirectorPersonMixType
        return self.related_persons.only("id", "name","poster").all()

    def resolve_thumb(self, info, *_):
        if self.thumbnail:
            return self.thumbnail
        else:
            url = self.link
            if "youtube" in url:
                try:
                    defer_web = url.split("v=")[1]
                    yt_id = defer_web.split("&")[0]
                    v.youtube_id = yt_id
                    v.thumbnail = "https://img.youtube.com/vi/{}/mqdefault.jpg".format(yt_id)
                except:
                    raise("Can not split youtube id from link of video")
                    return None


    def resolve_tags(self, info, *_):
        return self.tags

    def resolve_isFaved(self,info, *_):
        if info.context.user.is_authenticated:
            user= info.context.user
            if self in user.profile.videos.all():
                return True
        return False

class MovieImageType(DjangoObjectType):
    info = graphene.types.json.JSONString()
    class Meta:
        model= MovieImage
    def resolve_info(self, info, *_):
        return self.image_info

class PersonImageType(DjangoObjectType):
    info =  graphene.String()
    url = graphene.String()
    videos = graphene.List(VideoType)
    class Meta:
        model= PersonImage
    def resolve_url(self, info, *_):
        return self.image.url
    def resolve_info(self, info, *_):
        return self.info
    def resolve_videos(self, info, *_):
        return self.videos.all()

class MovieType(DjangoObjectType):
    poster = graphene.String()
    images = graphene.List(MovieImageType) #for property types
    pic = graphene.String()
    isBookmarked = graphene.Boolean()
    viewer_rating = graphene.Float()
    data = graphene.types.json.JSONString()
    tags = graphene.types.json.JSONString()
    viewer_points = graphene.Int()
    viewer_notes = graphene.String()
    viewer_rating_date = graphene.types.datetime.Date()
    isFaved = graphene.Boolean()


    class Meta:
        model = Movie
    def resolve_viewer_rating_date(self, info, *_):
        if info.context.user.is_authenticated:
            profile= info.context.user.profile
            try:
                return profile.rates.get(movie=self).date
            except:
                return ""

    def resolve_viewer_notes(self, info, *_):
        if info.context.user.is_authenticated:
            profile= info.context.user.profile
            try:
                return profile.rates.get(movie=self).notes
            except:
                return ""

            
    def resolve_viewer_points(self, info, *_):
        if info.context.user.is_authenticated:
            profile= info.context.user.profile
            return len(profile.ratings.items())
        return 0
    

    def resolve_poster(self, info, *_):
        if self.poster:
            return self.poster.url
        return ""

    def resolve_poster(self, info, *_):
        if self.poster and hasattr(self.poster, "url"):
            return self.poster.url
        return "https://s3.eu-west-2.amazonaws.com/cbs-static/static/images/default.jpg"


    def resolve_images(self,info, *_):
        return self.images.all()

    def resolve_isBookmarked(self,info, *_):
        if info.context.user.is_authenticated:
            user = info.context.user
            if user.profile in self.bookmarked.all():
                return True
        return False

    def resolve_viewer_rating(self, info, *_):
        if info.context.user.is_authenticated:
            user= info.context.user
            return user.profile.ratings.get(str(self.id))

    def resolve_data(self,info,*_):
        data = self.data
        new_data = {}
        new_data["Plot"] = data.get("Plot")
        new_data["Director"] = data.get("Director")
        new_data["Country"] = data.get("Country")
        new_data["Runtime"] = data.get("Runtime")
        return new_data

    def resolve_tags(self, info, *_):
        return self.tags

    def resolve_isFaved(self,info, *_):
        if info.context.user.is_authenticated:
            user= info.context.user
            if user.profile in self.liked.all():
                return True
        return False

class RatingType(DjangoObjectType):
    movie = graphene.Field(MovieType)
    date = graphene.types.datetime.Date()
    notes = graphene.String()
    rating = graphene.Float()

    class Meta:
        model= Rating

    def resolve_movie(self, info):
        return self.movie

    def resolve_date(self, info, *_):
        return self.date
    def resolve_notes(self, info, *_):
        return self.notes
    def resolve_rating(self, info, *_):
        return self.rating

class ProfileType2(DjangoObjectType):
    token = graphene.String()
    ratings = graphene.types.json.JSONString()
    len_bookmarks = graphene.Int()
    len_ratings = graphene.Int()
    points = graphene.Int()
    rates = graphene.Field(RatingType)

    class Meta:
        model = Profile
    def resolve_rates(self, info, *_):
        return self.rates.all()

    def resolve_points(self, info):
        return len(self.ratings.items())
    def resolve_ratings(self, info, *_):
        return self.ratings
    
    def resolve_len_bookmarks(self, info):
        return self.bookmarks.count()
    def resolve_len_ratings(self, info):
        return len(self.ratings)


class PersonType(DjangoObjectType):
    jobs = graphene.List(graphene.String)
    data = graphene.types.json.JSONString()
    poster = graphene.String()
    square_poster = graphene.String()
    images = graphene.List(PersonImageType) #for property types

    isActive = graphene.Boolean()
    isFollowed = graphene.Boolean()
    movies = graphene.List(MovieType)
    class Meta:
        model = Person

    def resolve_jobs(self,info,):
        history=  Crew.objects.filter(person=self).only("job").values_list("job", flat=True).distinct()
        job_list = []
        for x in history:
            if x=="a":
                job_list.append("ACTOR/ACTRESS")
            if x=="d":
                job_list.append("DIRECTOR")
            elif x=="w":
                job_list.append("WRITER")
            elif x=="e":
                job_list.append("EDITOR")
        return job_list

    def resolve_isActive(self,info,*_):
        return self.active

    def resolve_isFollowed(self, info, *_):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            qs = self.followers.select_related("profile")
            qs_profiles = [x.profile for x in qs]
            if profile in qs_profiles:
                return True
        return False

    def resolve_data(self,info,*_):
        return self.data

    def resolve_images(self,info, *_):
        return self.images.all()

    def resolve_poster(self, info, *_):
        if self.poster and hasattr(self.poster, "url"):
            return self.poster.url
        else:
            self.save_poster_from_url()
            if self.poster and hasattr(self.poster, "url"):
                return self.poster.url
            else:
                return "https://s3.eu-west-2.amazonaws.com/cbs-static/static/images/default.jpg"


    def resolve_square_poster(self, info, *_):
        if self.square_poster and hasattr(self.square_poster, "url"):
            return self.square_poster.url
    
    def resolve_movies(self, info, *_):
        crew_qs = Crew.objects.filter(person=self).select_related("movie").defer("job","character")
        return list(set([x.movie for x in crew_qs]))

class CrewType(DjangoObjectType):
    person = graphene.Field(PersonType)
    class Meta:
        model = Crew
    
    def resolve_person(self, info, *_):
        return self.person



class DirectorType(DjangoObjectType):
    data = graphene.types.json.JSONString()
    jobs = graphene.List(graphene.String)
    movies = graphene.List(MovieType)
    favourite_movies = graphene.List(MovieType)

    poster = graphene.String()
    square_poster = graphene.String()
    has_cover = graphene.Boolean()
    cover_poster = graphene.String()

    isActive = graphene.Boolean()
    images = graphene.List(PersonImageType) #for property types
    isFollowed = graphene.Boolean()
    lenMovies = graphene.Int()
    viewer_points = graphene.Int()
    
    #Viewer rated movies for this director
    viewer_movies = graphene.List(MovieType)
    #Viewer rated movies for this director's favourite film list
    viewer_favourite_movies = graphene.List(MovieType)


    class Meta:
        model = Person

    def resolve_jobs(self,info,):
        history=  Crew.objects.filter(person=self).only("job").values_list("job", flat=True).distinct()
        job_list = []
        for x in history:
            if x=="d":
                job_list.append("DIRECTOR")
            elif x=="w":
                job_list.append("WRITER")
            elif x=="e":
                job_list.append("EDITOR")
        return job_list

    def resolve_viewer_favourite_movies(self, info, *_):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            profile_rated_movies = profile.rated_movie_list()

            qs_list = List.objects.prefetch_related("movies").filter(list_type="df",
                        related_persons=self, movies__in=profile_rated_movies).only("id","movies", "list_type")
            movie_list = []
            for x in qs_list:
                movie_qs = x.movies.only("id","name","poster","year").all()
                for m in movie_qs:
                    movie_list.append(m)
            return list(set(movie_list))

    def resolve_favourite_movies(self, info, *_):
        qs_list = List.objects.prefetch_related("movies").filter(list_type="df",
                    related_persons=self).only("id","movies", "list_type")
        movie_list = []
        for x in qs_list:
            movie_qs = x.movies.only("id","name","poster","year").all()
            for m in movie_qs:
                movie_list.append(m)
        return list(set(movie_list))

    def resolve_viewer_movies(self, info, *_):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            profile_rated_movies = profile.rated_movie_list()
            crew_qs = Crew.objects.filter(person=self, movie__in=profile_rated_movies).select_related("movie").defer("job","character")
            return [x.movie for x in crew_qs]
            
    def resolve_movies(self, info, *_):
        crew_qs = Crew.objects.filter(person=self).select_related("movie").defer("job","character")
        return list(set([x.movie for x in crew_qs]))

    def resolve_isActive(self,info,):
        return self.active

    def resolve_lenMovies(self,info,*_):
        return Crew.objects.filter(person=self, job="d").count()

    def resolve_isFollowed(self, info, *_):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            qs = self.followers.select_related("profile")
            qs_profiles = [x.profile for x in qs]
            if profile in qs_profiles:
                return True
        return False

    def resolve_data(self,info,*_):
        return self.data
    def resolve_images(self,info, *_):
        return self.images.all()

    def resolve_poster(self, info, *_):
        if self.poster and hasattr(self.poster, "url"):
            return self.poster.url
        return "https://s3.eu-west-2.amazonaws.com/cbs-static/static/images/directors-default.jpg"

    def resolve_square_poster(self, info, *_):
        if self.square_poster and hasattr(self.square_poster, "url"):
            return self.square_poster.url

    def resolve_has_cover(self,info):
        if self.cover_poster and hasattr(self.cover_poster, "url"):
            return True
        return False

    def resolve_cover_poster(self, info, *_):
        if self.cover_poster and hasattr(self.cover_poster, "url"):
            return self.cover_poster.url
        return "https://s3.eu-west-2.amazonaws.com/cbs-static/static/images/director-cover-background-default.jpg"

    def resolve_viewer_points(self, info, *_):
        if info.context.user.is_authenticated:
            profile= info.context.user.profile
            return len(profile.ratings.items())
        return 0

class PredictionType(DjangoObjectType):
    class Meta:
        model = Prediction



class DirectorPersonMixType(DjangoObjectType):
    filtered_data = graphene.types.json.JSONString()
    social_media = graphene.types.json.JSONString()

    jobs = graphene.List(graphene.String)
    movies = graphene.List(MovieType)
    favourite_movies = graphene.List(MovieType)

    poster = graphene.String()
    square_poster = graphene.String()
    has_cover = graphene.Boolean()
    cover_poster = graphene.String()

    isActive = graphene.Boolean()
    images = graphene.List(PersonImageType) #for property types
    isFollowed = graphene.Boolean()
    lenMovies = graphene.Int()
    viewer_points = graphene.Int()
    
    #Viewer rated movies for this director
    viewer_movies = graphene.List(MovieType)
    #Viewer rated movies for this director's favourite film list
    viewer_favourite_movies = graphene.List(MovieType)


    class Meta:
        model = Person

    def resolve_jobs(self,info,):
        history=  Crew.objects.filter(person=self).only("job").values_list("job", flat=True).distinct()
        job_list = []
        for x in history:
            if x=="d":
                job_list.append("DIRECTOR")
            elif x=="w":
                job_list.append("WRITER")
            elif x=="e":
                job_list.append("EDITOR")
        return job_list

    def resolve_viewer_favourite_movies(self, info, *_):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            profile_rated_movies = profile.rated_movie_list()

            qs_list = List.objects.prefetch_related("movies").filter(list_type="df",
                        related_persons=self, movies__in=profile_rated_movies).only("id","movies", "list_type")
            movie_list = []
            for x in qs_list:
                movie_qs = x.movies.only("id","name","poster","year").all()
                for m in movie_qs:
                    movie_list.append(m)
            return list(set(movie_list))

    def resolve_favourite_movies(self, info, *_):
        qs_list = List.objects.prefetch_related("movies").filter(list_type="df",
                    related_persons=self).only("id","movies", "list_type")
        movie_list = []
        for x in qs_list:
            movie_qs = x.movies.only("id","name","poster","year").all()
            for m in movie_qs:
                movie_list.append(m)
        return list(set(movie_list))

    def resolve_viewer_movies(self, info, *_):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            profile_rated_movies = profile.rated_movie_list()
            crew_qs = Crew.objects.filter(person=self, movie__in=profile_rated_movies).select_related("movie").defer("job","character")
            return [x.movie for x in crew_qs]
            
    def resolve_movies(self, info, *_):
        crew_qs = Crew.objects.filter(person=self).select_related("movie").defer("job","character")
        crew_movies_list = [x.movie for x in crew_qs]
        person_movies_qs_list = list(self.movies.all())
        result = person_movies_qs_list + crew_movies_list
        return list(set(result))

    def resolve_isActive(self,info,):
        return self.active

    def resolve_lenMovies(self,info,*_):
        return Crew.objects.filter(person=self, job="d").count()

    def resolve_isFollowed(self, info, *_):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            qs = self.followers.select_related("profile")
            qs_profiles = [x.profile for x in qs]
            if profile in qs_profiles:
                return True
        return False

    def resolve_filtered_data(self,info,*_):
        person_data = self.data
        filtered_data = {}
        keywords = ["gender", "birthday", "deathday","also_known_as", "place_of_birth"]
        for kw in keywords:
            if person_data.get(kw)!="" and person_data.get(kw)!=None:
                if kw=="also_known_as":
                    filtered_data[kw] = person_data.get(kw)[:2]
                else:
                    filtered_data[kw] = person_data.get(kw)
        return filtered_data

    def resolve_social_media(self,info,*_):
        person_data = self.data
        filtered_data = {"imdb": "https://www.imdb.com/name/{}".format(self.id)}
        keywords = ["homepage", "instagram_id", "facebook_id", "twitter_id"]
        for kw in keywords:
            if person_data.get(kw)!="" and person_data.get(kw)!=None:
                if kw=="twitter_id":
                    filtered_data["twitter"] = "https://twitter.com/{}".format(person_data.get(kw))
                if kw=="instagram_id":
                    filtered_data["instagram"] = "https://www.instagram.com/{}".format(person_data.get(kw))
                if kw=="facebook_id":
                    filtered_data["facebook"] = "https://www.facebook.com/{}".format(person_data.get(kw))
                if kw=="homepage":
                    filtered_data["homepage"] = "https://www.facebook.com/{}".format(person_data.get(kw))
        return filtered_data

    def resolve_images(self,info, *_):
        return self.images.all()



    def resolve_poster(self, info, *_):
        if self.poster and hasattr(self.poster, "url"):
            return self.poster.url
        else:
            self.save_poster_from_url()
            if self.poster and hasattr(self.poster, "url"):
                return self.poster.url
            else:
                return "https://s3.eu-west-2.amazonaws.com/cbs-static/static/images/default.jpg"

    def resolve_square_poster(self, info, *_):
        if self.square_poster and hasattr(self.square_poster, "url"):
            return self.square_poster.url

    def resolve_has_cover(self,info):
        if self.cover_poster and hasattr(self.cover_poster, "url"):
            return True
        return False

    def resolve_cover_poster(self, info, *_):
        if self.cover_poster and hasattr(self.cover_poster, "url"):
            return self.cover_poster.url
        return "https://s3.eu-west-2.amazonaws.com/cbs-static/static/images/director-cover-background-default.jpg"

    def resolve_viewer_points(self, info, *_):
        if info.context.user.is_authenticated:
            profile= info.context.user.profile
            return len(profile.ratings.items())
        return 0

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
    def resolve_token(self, info, **kwargs):
        return graphql_jwt.shortcuts.get_token(self)

class ListType(DjangoObjectType):
    image = graphene.List(graphene.String)
    isFollowed = graphene.Boolean()
    viewer_points = graphene.Int()
    followers = graphene.List("gql.types.ProfileType")
    num_movies = graphene.Int()
    

    class Meta:
        model=List
    def resolve_num_movies(self, info, *_):
        return self.movies.count()

    def resolve_followers(self,info, *_):
        qs = Follow.objects.select_related("profile").filter(liste=self, 
            typeof="l").defer("target_profile","person","topic","updated_at","created_at")
        return [x.profile for x in qs]

    def resolve_image(self, info, *_):
        return self.image

    def resolve_isFollowed(self, info, *_):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            qs = self.followers.select_related("profile")
            qs_profiles = [x.profile for x in qs]
            if profile in qs_profiles:
                return True
        return False

    def resolve_viewer_points(self, info, *_):
        if info.context.user.is_authenticated:
            profile= info.context.user.profile
            return len(profile.ratings.items())
        return 0


class TopicType(DjangoObjectType):
    poster = graphene.String()
    isFollowed = graphene.Boolean()
    viewer_points = graphene.Int()
    class Meta:
        model = Topic
    def resolve_poster(self, info, *_):
        if self.poster:
            return self.poster.url
        return ""
    def resolve_isFollowed(self, info, *_):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            qs = self.followers.select_related("profile")
            qs_profiles = [x.profile for x in qs]
            if profile in qs_profiles:
                return True
        return False

    def resolve_viewer_points(self, info, *_):
        if info.context.user.is_authenticated:
            profile= info.context.user.profile
            return len(profile.ratings.items())
        return 0



class ProfileType(DjangoObjectType):
    token = graphene.String()
    is_self = graphene.Boolean()
    avatar = graphene.String()
    country = graphene.List(graphene.String)

    bookmarks = graphene.List(MovieType)
    ratings = graphene.List(RatingType)
    diaries = graphene.List(RatingType)

    latest_ratings = graphene.List(RatingType)
    ratings_movieset = graphene.List(graphene.Int)

    lists = graphene.List(ListType)

    points = graphene.Int()
    num_bookmarks = graphene.Int()
    is_followed = graphene.Boolean()

    favourite_movies = graphene.List(MovieType)
    favourite_videos = graphene.List(VideoType)

    following_lists = graphene.List(ListType)
    following_topics = graphene.List(TopicType)
    following_persons =  graphene.List(PersonType)
    following_profiles =  graphene.List("gql.types.ProfileType")

    followers = graphene.List("gql.types.ProfileType")
    ratingset = graphene.types.json.JSONString()

    class Meta:
        model = Profile
    
    def resolve_ratingset(self, info):
        return self.ratings

    def resolve_avatar(self, info, *_):
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        return "https://s3.eu-west-2.amazonaws.com/cbs-static/static/images/user-avatar.svg"

    def resolve_latest_ratings(self, info, *_):
        return self.rates.select_related("movie").order_by("-created_at")[:5]

    def resolve_country(self, info, *_):
        if self.country and hasattr(self.country, "name"):
            return [self.country.name, self.country.code]

    def resolve_is_self(self, info, *_):
        user = info.context.user
        if user.username == self.username:
            return True
        return False

    def resolve_bookmarks(self, info, *_):
        return self.bookmarks.all().defer(*movie_defer)

    def resolve_ratings(self, info, *_):
        return self.rates.select_related("movie").order_by("-created_at").all()
        #return Rating.objects.select.related("movie").filter(profile=self).all()
        

    def resolve_diaries(self, info, *_):
        q_filter = Q(date__isnull=False)
        my_diaries = self.rates.filter(q_filter).select_related("movie").order_by("-date")
        return my_diaries



    def resolve_ratings_movieset(self, info, *_):
        if is_owner(self,info):
            return self.rates.values_list("movie_id",flat=True)
        raise("Not owner of rates")

    def resolve_lists(self, info, *_):
        if is_owner(self,info):
            return self.lists.all().defer("movies", "reference_notes", "related_persons")
        return self.lists.filter(public=True).defer("movies", "reference_notes", "related_persons")

    def resolve_points(self, info):
        return len(self.ratings.items())

    def resolve_num_bookmarks(self, info):
        return len(self.ratings.items())

    def resolve_is_followed(self, info, *_):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            qs = Follow.objects.filter(profile=profile, target_profile=self, typeof="u")
            if qs:
                return True
            return False

    def resolve_favourite_movies(self, info, *_):
        qs = self.liked_movies.all().defer("imdb_id","imdb_rating","summary",
                "tmdb_id","director","data", "tags")
        return  qs

    def resolve_favourite_videos(self, info, *_):
        qs = self.videos.defer("duration","channel_url","channel_name",
                "related_persons","related_movies","related_topics","tags").all()
        return  qs


    def resolve_following_lists(self, info, *_):
        qs = Follow.objects.select_related("liste").filter(profile=self,
            typeof="l").defer("target_profile","person","topic","liste__movies",
            "updated_at","created_at")
        return [x.liste for x in qs]

    def resolve_following_topics(self, info, *_):
        qs = Follow.objects.select_related("topic").filter(profile=self,
            typeof="t").defer("target_profile","person","liste",
            "updated_at","created_at")
        return [x.topic for x in qs]

    def resolve_following_persons(self, info, *_):
        qs = Follow.objects.select_related("person").filter(profile=self,
            typeof="p").defer("target_profile","topic","liste",
            "updated_at","created_at")
        return [x.person for x in qs]
            
    def resolve_following_profiles(self, info, *_):
        qs = Follow.objects.select_related("target_profile").filter(profile=self,
            typeof="u").defer("person","topic","liste","updated_at","created_at")
        return [x.target_profile for x in qs]



    def resolve_followers(self, info, *_):
        qs = Follow.objects.select_related("profile").filter(target_profile=self,
            typeof="u").defer("person","topic","liste","updated_at","created_at")
        return [x.profile for x in qs]


class MovieListType(DjangoObjectType):
    is_self = graphene.Boolean()
    image = graphene.types.json.JSONString()
    isFollowed = graphene.Boolean()
    viewer_points = graphene.Int()

    followers = graphene.List("gql.types.ProfileType")
    num_followers = graphene.Int()
    child_movies = graphene.List(MovieType)
    length = graphene.Int()
    description = graphene.String()

    class Meta:
        model=List
    def resolve_is_self(self, info):
        if info.context.user.is_authenticated:
            if self.owner.username==info.context.user.username:
                return True
        return False
    
    def resolve_description(self, info, *_):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            #if private
            if not self.public:
                if self.owner==profile:
                    return self.summary
                else:
                    return "This is a private list"
            return self.summary

    def resolve_length(self, info, *_):
        return self.movies.count()

    def resolve_child_movies(self, info, *_, **kwargs):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            #if private
            if not self.public:
                if self.owner==profile:
                    qs = self.movies.all().defer(*movie_defer)
                    return qs
                if self.owner!=profile:
                    return []
            return self.movies.all().defer(*movie_defer)


    def resolve_followers(self,info, *_):
        qs = Follow.objects.select_related("profile").filter(liste=self, 
            typeof="l").defer("target_profile","person","topic","updated_at","created_at")
        return [x.profile for x in qs]

    def resolve_num_followers(self,info, *_):
        qs = Follow.objects.filter(liste=self, typeof="l")
        return qs.count()

    def resolve_image(self, info, *_):
        return self.image

    def resolve_isFollowed(self, info, *_):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            qs = self.followers.select_related("profile")
            qs_profiles = [x.profile for x in qs]
            if profile in qs_profiles:
                return True
        return False



class CustomListType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    summary = graphene.String()
    list_type = graphene.String()

    owner = graphene.Field(ProfileType)
    is_self = graphene.Boolean()
    
    movies = graphene.List(MovieType)
    movieset = graphene.List(graphene.Int)
    num_movies = graphene.Int()

    image = graphene.List(graphene.String)

    followers = graphene.List(ProfileType)
    viewer = graphene.Field(ProfileType)

    isFollowed = graphene.Boolean()

    num_followers = graphene.Int()


    def __init__(self, id, first=None, skip=None, viewer=None):
        self.id = id
        self.liste = List.objects.only("id").get(id=id)
        self.viewer = viewer
        self.first = first
        self.skip = skip

    def resolve_list_type(self, info):
        if self.liste.list_type!=None:
            return self.liste.list_type

    def resolve_viewer(self, info):
        if self.viewer:
            return self.viewer

    def resolve_name(self, info, *_):
        return self.liste.name

    def resolve_summary(self, info, *_):
        return self.liste.summary

    def resolve_owner(self, info, *_):
        return self.liste.owner

    def resolve_movies(self, info):
        if info.context.user.is_authenticated:
            if self.first:
                return self.liste.movies.defer(*movie_defer).all()[self.skip : self.skip + self.first]
            return self.liste.movies.defer(*movie_defer).all()

    def resolve_movieset(self, info):
        return self.movies.values_list("id", flat=True)

    def resolve_num_movies(self, info, *_):
        return self.liste.movies.count()

    def resolve_is_self(self, info):
        if info.context.user.is_authenticated:
            if self.liste.owner==info.context.user.profile:
                return True
        return False
    


    def resolve_followers(self,info, *_):
        qs = self.liste.followers.only("profile","liste")

    def resolve_num_followers(self,info, *_):
        return self.liste.followers.count()

    def resolve_image(self, info, *_):
        return self.liste.image

    def resolve_isFollowed(self, info, *_):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            qs = self.liste.followers.select_related("profile")
            qs_profiles = [x.profile for x in qs]
            if profile in qs_profiles:
                return True
        return False




class CustomMovieType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    summary = graphene.String()
    year = graphene.Int()

    poster = graphene.String()
    has_cover = graphene.Boolean()
    cover_poster = graphene.String()


    data = graphene.types.json.JSONString()
    videos = graphene.List(VideoType)
    director = graphene.List(PersonType)
    crew = graphene.List(CrewType)

    isBookmarked = graphene.Boolean()
    isFaved = graphene.Boolean()
    #liked = graphene.List(ProfileType)
    prediction_history = graphene.Float()
    viewer = graphene.Field(ProfileType)
    viewer_rating = graphene.Float()
    viewer_points = graphene.Int()
    viewer_notes = graphene.String()
    viewer_rating_date = graphene.types.datetime.Date()
    appears = graphene.List(ListType)


    def __init__(self, id, viewer=None):
        self.id = id
        self.movie = Movie.objects.only("id").get(id=id)
        self.viewer = viewer #Profile

    def resolve_name(self,info):
        return self.movie.name

    def resolve_summary(self,info):
        return self.movie.summary

    def resolve_year(self,info):
        return self.movie.year

    def resolve_prediction_history(self, info):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            is_eligible = profile.prediction_history_eligibility(self.movie)
            if is_eligible==True:
                return 0
            else:
                return Prediction.objects.filter(profile=profile, movie=self.movie)[0].prediction


    def resolve_poster(self,info):
        if self.movie.poster!="" and self.movie.poster!=None:
            return self.movie.poster.url
        else:
            return "https://s3.eu-west-2.amazonaws.com/cbs-static/static/images/default.jpg"
        #else:
        #    self.movie.save_poster_from_url()
        #    if self.movie.poster!="" and self.movie.poster!=None:
        #        return self.movie.poster.url
        #    return "https://s3.eu-west-2.amazonaws.com/cbs-static/static/images/default.jpg"

    def resolve_has_cover(self,info):
        if self.movie.cover_poster and hasattr(self.movie.cover_poster, "url"):
            return True
        return False

    def resolve_cover_poster(self, info, *_):
        if self.movie.cover_poster and hasattr(self.movie.cover_poster, "url"):
            return self.movie.cover_poster.url

    def resolve_data(self,info,*_):
        data = self.movie.data
        new_data = {}
        new_data["plot"] = data.get("Plot")
        new_data["director"] = data.get("Director")
        new_data["country"] = data.get("Country")
        new_data["runtime"] = data.get("Runtime")
        new_data["website"] = data.get("Website")
        new_data["imdb_id"] = self.movie.imdb_id
        new_data["tmdb_id"] = self.movie.tmdb_id
        if self.movie.imdb_rating:
            new_data["imdb_rating"] = str(self.movie.imdb_rating)

        return {k:v for k,v in new_data.items() if v!=None}


    def resolve_videos(self, info):
        qs = self.movie.videos.all()
        return qs


    def resolve_director(self, info):
        qs = Crew.objects.filter(movie=self.movie, job="d")
        if qs.count()>=1:
            return [x.person for x in qs]

        elif qs.count()==0:
            if self.movie.data.get("Director"):
                if Person.objects.filter(name=self.movie.data.get("Director"), job="d").count()==1:
                    return Person.objects.filter(name=self.movie.data.get("Director"), job="d")
        else:
            return []


    def resolve_crew(self, info):
        qs = Crew.objects.filter(movie=self.movie, job__in=["a","d"])
        qs_list = list(qs)
        if not qs.filter(job="d").exists():
            if self.movie.director:
                if Crew.objects.filter(person=self.movie.director, job="d").exists():
                    qs_list.append( Crew.objects.filter(person=self.movie.director, job="d")[0] )
        return qs_list

    def resolve_isBookmarked(self,info, *_):
        if info.context.user.is_authenticated:
            user = info.context.user
            if user.profile in self.movie.bookmarked.only("username", "id").all():
                return True
        return False

    def resolve_isFaved(self,info, *_):
        if self.viewer and self.viewer in self.movie.liked.only("id", "username").all():
            return True
        return False

    def resolve_viewer(self, info):
        if self.viewer:
            return self.viewer

    def resolve_viewer_rating(self, info, *_):
        if info.context.user.is_authenticated:
            user= info.context.user
            return user.profile.ratings.get(str(self.id))

    def resolve_viewer_rating_date(self, info, *_):
        if info.context.user.is_authenticated:
            profile= info.context.user.profile
            try:
                return profile.rates.get(movie=self.movie).date
            except:
                return None

    def resolve_viewer_notes(self, info, *_):
        if info.context.user.is_authenticated:
            profile= info.context.user.profile
            try:
                return profile.rates.get(movie=self.movie).notes
            except:
                return ""

    def resolve_viewer_points(self, info, *_):
        if info.context.user.is_authenticated:
            profile= info.context.user.profile
            return len(profile.ratings.items())
        return 0
    
    def resolve_appears(self, info):
        qs = self.movie.lists.filter(list_type="df").defer("movies")
        return qs




"""

class FollowType(DjangoObjectType):
    =  graphene.List(PersonType)

    class Meta:
        model = Follow

def resolve_poster(self, info, *_):
        if self.poster and hasattr(self.poster, "url"):
            return self.poster.url
        else:
            if self.data.get("tmdb_poster_path"):
                return self.data.get("tmdb_poster_path")
            else:
                return "https://s3.eu-west-2.amazonaws.com/cbs-static/static/images/directors-default.jpg" 
"""