from items.models import Movie, List, MovieImage, Video, Topic
from persons.models import Person, Profile, PersonImage, Director
from algorithm.models import Dummy
from items.models import Rating
        
from django.contrib.auth import get_user_model

import graphene
from django_mysql.models import JSONField
from graphene_django.types import DjangoObjectType
from graphene_django.converter import convert_django_field

@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return graphene.String()

class VideoType(DjangoObjectType):
    tags = graphene.types.json.JSONString()
    class Meta:
        model=Video
    def resolve_tags(self, info, *_):
        return self.tags

class MovieImageType(DjangoObjectType):
    info = graphene.types.json.JSONString()
    class Meta:
        model= MovieImage
    def resolve_info(self, info, *_):
        return self.image_info

class PersonImageType(DjangoObjectType):
    info = graphene.types.json.JSONString()
    videos = graphene.List(VideoType)
    class Meta:
        model= PersonImage
    def resolve_info(self, info, *_):
        return self.image_info
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


    class Meta:
        model = Movie

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
            user= info.context.user
            if self in user.profile.bookmarks.all():
                return True
        return False

    def resolve_viewer_rating(self, info, *_):
        if info.context.user.is_authenticated:
            user= info.context.user
            return user.profile.ratings.get(str(self.id))
    def resolve_data(self,info,*_):
        return self.data
    def resolve_tags(self, info, *_):
        return self.tags

class DummyType():
    ratings = graphene.types.json.JSONString()
    class Meta:
        model= Dummy
    def resolve_ratings(self,info, *_):
        return Dummy.Votes.get(1)

class RatingType(DjangoObjectType):
    
    movie = graphene.Field(MovieType)
    class Meta:
        model= Rating
    def resolve_movie(self, info, *_):
        return self.movie

class ProfileType(DjangoObjectType):
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
    images = graphene.List(PersonImageType) #for property types
    isFollowed = graphene.Boolean()
    class Meta:
        model = Person
    def resolve_isFollowed(self, info, *_):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            if profile in self.followers.all():
                return True
        return False
    def resolve_data(self,info,*_):
        return self.data
    def resolve_images(self,info, *_):
        return self.images.all()

class DirectorType(DjangoObjectType):
    data = graphene.types.json.JSONString()
    images = graphene.List(PersonImageType) #for property types
    isFollowed = graphene.Boolean()
    class Meta:
        model = Person
    def resolve_isFollowed(self, info, *_):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            if profile in self.followers.all():
                return True
        return False
    def resolve_data(self,info,*_):
        return self.data
    def resolve_images(self,info, *_):
        return self.images.all()

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
    def resolve_token(self, info, **kwargs):
        return graphql_jwt.shortcuts.get_token(self)

class ListType(DjangoObjectType):
    image = graphene.types.json.JSONString()
    isFollowed = graphene.Boolean()
    class Meta:
        model=List

    def resolve_image(self, info, *_):
        return self.image

    def resolve_isFollowed(self, info, *_):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            if profile in self.followers.all():
                return True
        return False

class TopicType(DjangoObjectType):
    poster = graphene.String()
    isFollowed = graphene.Boolean()
    class Meta:
        model = Topic
    def resolve_poster(self, info, *_):
        if self.poster:
            return self.poster.url
        return ""
    def resolve_isFollowed(self, info, *_):
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            if profile in self.followers.all():
                return True
        return False