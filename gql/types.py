from items.models import Rating,Movie, List, MovieImage, Video, Topic
from persons.models import Person, PersonImage, Director, Crew
from persons.profile import Profile, Follow
from django.contrib.auth import get_user_model
import graphene
from django_mysql.models import JSONField
from graphene_django.types import DjangoObjectType
from graphene_django.converter import convert_django_field

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





class VideoType(DjangoObjectType):
    tags = graphene.List(graphene.String)
    isFaved = graphene.Boolean()
    #tags = graphene.types.json.JSONString()
    class Meta:
        model=Video
    def resolve_tags(self, info, *_):
        return [x for x in self.tags]

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
    class Meta:
        model= Rating


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
    data = graphene.types.json.JSONString()
    poster = graphene.String()
    images = graphene.List(PersonImageType) #for property types
    isFollowed = graphene.Boolean()
    movies = graphene.List(MovieType)
    class Meta:
        model = Person

    
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
        if self.poster:
            return self.poster.url
    
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
    poster = graphene.String()

    images = graphene.List(PersonImageType) #for property types
    isFollowed = graphene.Boolean()
    lenMovies = graphene.Int()
    viewer_points = graphene.Int()


    class Meta:
        model = Person
    def resolve_lenMovies(self,info,*_):
        return self.movies.count()

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
        if self.poster:
            return self.poster.url
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

    bookmarks = graphene.List(MovieType)
    ratings = graphene.Field(RatingType)
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

    class Meta:
        model = Profile
    def resolve_avatar(self, info, *_):
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        return "https://s3.eu-west-2.amazonaws.com/cbs-static/static/images/user-avatar.svg"

    def resolve_latest_ratings(self, info, *_):
        return self.rates.select_related("movie").order_by("updated_at")[:5]

    def resolve_is_self(self, info, *_):
        user = info.context.user
        if user.username == self.username:
            return True
        return False

    def resolve_bookmarks(self, info, *_):
        return self.bookmarks.all().defer(*movie_defer)

    def resolve_ratings(self, info, *_):
        if is_owner(self,info):
            return self.rates.all()
        raise("Not owner of rates")

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

    owner = graphene.Field(ProfileType)
    is_self = graphene.Boolean()
    
    movies = graphene.List(MovieType)
    movieset = graphene.List(graphene.Int)
    num_movies = graphene.Int()

    image = graphene.List(graphene.String)

    followers = graphene.List(ProfileType)
    isFollowed = graphene.Boolean()

    num_followers = graphene.Int()


    def __init__(self, id, first=None, skip=None):
        self.id = id
        self.liste = List.objects.only("id").get(id=id)
        self.first = first
        self.skip = skip

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


    data = graphene.types.json.JSONString()
    videos = graphene.List(VideoType)
    director = graphene.List(PersonType)
    crew = graphene.List(CrewType)

    isBookmarked = graphene.Boolean()
    isFaved = graphene.Boolean()
    #liked = graphene.List(ProfileType)

    viewer_rating = graphene.Float()
    viewer_points = graphene.Int()
    viewer_notes = graphene.String()
    viewer_rating_date = graphene.types.datetime.Date()
    appears = graphene.List(ListType)


    def __init__(self, id):
        self.id = id
        self.movie = Movie.objects.only("id").get(id=id)


    def resolve_name(self,info):
        return self.movie.name

    def resolve_summary(self,info):
        return self.movie.summary

    def resolve_year(self,info):
        return self.movie.year
    
    def resolve_poster(self,info):
        if self.movie.poster!="" and self.movie.poster!=None:
            return self.movie.poster.url
        return ""

    def resolve_data(self,info,*_):
        data = self.movie.data
        new_data = {}
        new_data["plot"] = data.get("Plot")
        new_data["director"] = data.get("Director")
        new_data["country"] = data.get("Country")
        new_data["runtime"] = data.get("Runtime")
        new_data["website"] = data.get("Website")
        new_data["imdb_rating"] = str(self.movie.imdb_rating)
        new_data["imdb_id"] = self.movie.imdb_id
        new_data["tmdb_id"] = self.movie.tmdb_id

        return {k:v for k,v in new_data.items() if v!=None}


    def resolve_videos(self, info):
        qs = self.movie.videos.all()


    def resolve_director(self, info):
        qs = Crew.objects.filter(movie=self.movie, job="d")
        if qs.count()>=1:
            return [x.person for x in qs]

        elif qs.count()==0:
            if self.movie.data.get("Director"):
                if Person.objects.filter(name=self.movie.data.get("Director"), job="d").count()==1:
                    return Person.objects.filter(name=self.movie.data.get("Director"), job="d")
        else:
            return None


    def resolve_crew(self, info):
        qs = Crew.objects.filter(movie=self.movie, job__in=["a"])
        return qs


    def resolve_isBookmarked(self,info, *_):
        if info.context.user.is_authenticated:
            user = info.context.user
            if user.profile in self.movie.bookmarked.only("username", "id").all():
                return True
        return False

    def resolve_isFaved(self,info, *_):
        if info.context.user.is_authenticated:
            user= info.context.user
            if user.profile in self.movie.liked.only("id", "username").all():
                return True
        return False


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
                return ""

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
"""