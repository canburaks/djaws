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
    image = graphene.types.json.JSONString()
    isFollowed = graphene.Boolean()
    viewer_points = graphene.Int()
    followers = graphene.List("gql.types.ProfileType")

    class Meta:
        model=List

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

    bookmarks = graphene.List(MovieType)
    ratings = graphene.Field(RatingType)
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


    def resolve_is_self(self, info, *_):
        user = info.context.user
        if user.username == self.username:
            return True
        return False

    def resolve_bookmarks(self, info, *_):
        return self.bookmarks.all().defer("imdb_id","imdb_rating","summary",
            "tmdb_id","director","data","ratings_dummy","tags","ratings_user")

    def resolve_ratings(self, info, *_):
        if is_owner(self,info):
            return self.rates.all()
        raise("Not owner of rates")

    def resolve_lists(self, info, *_):
        return self.lists.all().defer("movies", "reference_notes", "related_persons")

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
                "tmdb_id","director","data","ratings_dummy", "tags", "ratings_user")
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
"""

class FollowType(DjangoObjectType):
     =  graphene.List(PersonType)

    class Meta:
        model = Follow
"""