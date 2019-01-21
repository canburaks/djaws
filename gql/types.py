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

    class Meta:
        model=List

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
    points = graphene.Int()
    num_bookmarks = graphene.Int()
    rates = graphene.Field(RatingType)

    favourite_movies = graphene.List(MovieType)
    favourite_lists = graphene.List(ListType)
    favourite_topics = graphene.List(TopicType)
    favourite_persons =  graphene.List(PersonType)

    class Meta:
        model = Profile
    def resolve_rates(self, info, *_):
        return self.rates.all()

    def resolve_points(self, info):
        return len(self.ratings.items())

    def resolve_num_bookmarks(self, info):
        return len(self.ratings.items())

    def resolve_favourite_movies(self, info, *_):
        qs = Rating.objects.filter(profile=self).select_related("movie").order_by("-rating").defer("notes","date","created_at","updated_at")
        return  [x.movie for x in qs[:10]]


    def resolve_favourite_lists(self, info, *_):
        qs = Follow.objects.select_related("liste").filter(profile=self,
             typeof="l").defer("target_profile","person","topic",
             "updated_at","updated_at")
        return [x.liste for x in qs]

    def resolve_favourite_topics(self, info, *_):
        qs = Follow.objects.select_related("topic").filter(profile=self,
             typeof="t").defer("target_profile","person","liste",
             "updated_at","updated_at")
        return [x.topic for x in qs]

    def resolve_favourite_persons(self, info, *_):
        qs = Follow.objects.select_related("person").filter(profile=self,
             typeof="p").defer("target_profile","topic","liste",
             "updated_at","updated_at")
        return [x.person for x in qs]
            