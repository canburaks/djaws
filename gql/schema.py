from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import get_user_model
from django_mysql.models import JSONField
from items.models import Movie, List, MovieImage, Video, Rating
from persons.models import Person, Profile, PersonImage, Director
from algorithm.models import Dummy
import graphene
import graphql_jwt
from graphql_jwt.decorators import login_required
from graphene_django.types import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Q
from django.conf import settings

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


class ProfileType(DjangoObjectType):
    token = graphene.String()
    ratings = graphene.types.json.JSONString()
    len_bookmarks = graphene.Int()
    len_ratings = graphene.Int()
    points = graphene.Int()

    class Meta:
        model = Profile

    def resolve_points(self, info):
        return len(self.ratings.items())
    def resolve_ratings(self, info, *_):
        return self.ratings
    
    def resolve_len_bookmarks(self, info):
        return self.bookmarks.count()
    def resolve_len_ratings(self, info):
        return len(self.ratings)

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

class Query(graphene.ObjectType):
    list_of_lists = graphene.List(ListType)
    new_lists = graphene.List(graphene.types.json.JSONString,
            id=graphene.Int(default_value=None), 
        name=graphene.String(default_value=None)
    )

    directors = graphene.List(DirectorType)
    prediction = graphene.Float(movieId=graphene.Int())
    dummy = graphene.types.json.JSONString(dummyId=graphene.String())

    person = graphene.Field(PersonType,
        id=graphene.String(default_value=None))

    viewer = graphene.Field(ProfileType, username=graphene.String())
    all_movies = graphene.List(MovieType)
    lists = graphene.List(MovieType, 
        id=graphene.Int(default_value=None), 
        name=graphene.String(default_value=None),
        search=graphene.String(default_value=None),
        first=graphene.Int(default_value=None),
        skip=graphene.Int(default_value=None)
        )

    length = graphene.Int(
        id=graphene.Int(default_value=None), 
        name=graphene.String(default_value=None),
        search=graphene.String(default_value=None)
    )
    movie = graphene.Field(MovieType,id=graphene.Int(),name=graphene.String())
    all_profiles = graphene.List(ProfileType)
    


    def resolve_list_of_lists(self, info, **kwargs):
        return List.objects.all()

    def resolve_directors(self, info, **kwargs):
        return Director.objects.all()
    
    def resolve_dummy(self, info, **kwargs):
        dummyId = kwargs.get("dummyId")
        return Dummy.Votes.get(dummyId)

    def resolve_prediction(self, info,**kwargs):
        movid = kwargs.get("movieId")
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            if len(profile.ratings.items())<30:
                return 0
            movie = Movie.objects.get(id=movid)
            result = profile.predict(movie)
            return result

    def resolve_person(self, info, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")
        if id is not None:
            return Person.objects.get(id=id)


    def resolve_viewer(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Authentication credentials were not provided')
        if info.context.user.is_authenticated:
            user = info.context.user
            profile = user.profile
            return profile

    def resolve_length(self, info, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")
        search = kwargs.get("search")

        if id is not None:
            if id==0:
                result = Movie.objects.all()[:5000]
                return result.count()
                
            result = List.objects.get(id=id).movies.all().count()
            return result

        if name is not None:
            user = info.context.user
            if user.is_authenticated:
                if name=="ratings":
                    profile_ratings = user.profile.ratings.keys()
                    return Movie.objects.filter(id__in=profile_ratings).count()
                if name=="bookmarks":
                    result = user.profile.bookmarks.all().count()
                    return result
            else :
                raise Exception('Authentication credentials were not provided')

        if search:
            filter = (
                Q(name__icontains=search) 
                #| Q(summary__icontains=search)
            )
            result = Movie.objects.filter(filter).count()
            return result

    def resolve_all_movies(self, info, **kwargs):
        return Movie.objects.all().order_by("-year")[:1000]

    #@login_required
    def resolve_lists(self, info, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")
        search = kwargs.get("search")
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        if id is not None:
            if id==0:
                result = Movie.objects.all().defer("imdb_id",
                "tmdb_id","actors","data","ratings_dummy","director","summary","tags","ratings_user")[:3000]
                if skip:
                    result = Movie.objects.all()[skip::]
                if first:
                    result = result[:first]
                return result.order_by("-imdb_rating")
                
            result = List.objects.get(id=id).movies.defer("imdb_id",
                "tmdb_id","actors","data","ratings_dummy","director","summary","tags","ratings_user")

            if skip:
                result = result[skip::]
            if first:
                result = result[:first]
            return result

        if name is not None:
            user = info.context.user
            if user.is_authenticated:
                if name=="ratings":
                    profile_ratings = user.profile.ratings.keys()
                    result = Movie.objects.filter(id__in=profile_ratings).defer("imdb_id",
                "tmdb_id","actors","data","ratings_dummy","director","summary","tags","ratings_user")
                    if skip:
                        result = result[skip::]
                    if first:
                        result = result[:first]
                    return result
                
                if name=="ratings2":

                    return Movie.objects.filter(id__in=user.profile.rates.all())

                if name=="bookmarks":
                    result = user.profile.bookmarks.all().defer("imdb_id",
                "tmdb_id","actors","data","ratings_dummy","director","summary","tags","ratings_user")
                    if skip:
                        result = result[skip::]
                    if first:
                        result = result[:first]
                    return result
            else :
                raise Exception('Authentication credentials were not provided')

        if search:
            filter = (
                Q(name__icontains=search) 
                #| Q(summary__icontains=search)
            )
            result = Movie.objects.filter(filter).defer("imdb_id",
                "tmdb_id","actors","data","ratings_dummy","director","summary","tags","ratings_user")
            if skip:
                result = result[skip::]
            if first:
                result = result[:first]
            return result


    def resolve_movie(self, info, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")

        if id is not None:
            return Movie.objects.get(id=id)

        if name is not None:
            return Movie.objects.get(name=name)

    def resolve_all_profiles(self, info, **kwargs):
        return Profile.objects.all()


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)
    profile = graphene.Field(ProfileType)
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)


    def mutate(self, info, username, password, email):
        user = get_user_model()(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()
        profile = user.profile
        #token_auth = graphql_jwt.ObtainJSONWebToken.Field()
        #token = graphql_jwt.shortcuts.get_token(user)
        return CreateUser(user=user, profile=profile)

class Bookmark(graphene.Mutation):
    user = graphene.Field(UserType)
    movie = graphene.Field(MovieType)
    class Arguments:
        id = graphene.Int()
    def mutate(self,info,id):
        if info.context.user.is_authenticated:
            user = info.context.user
            profile = user.profile
            movie = Movie.objects.get(id=id)
            profile.bookmarking(movie)
            return Bookmark(user=user, movie=movie)

class Follow(graphene.Mutation):
    user = graphene.Field(UserType)
    person = graphene.Field(PersonType)
    liste = graphene.Field(ListType)
    class Arguments:
        id = graphene.String()
        obj = graphene.String()
    def mutate(self,info,id, obj):
        if info.context.user.is_authenticated:
            user = info.context.user
            profile = user.profile
            if obj=="p" or obj=="person":
                person = Person.objects.get(id=id)
                profile.follow_person(person)
                return Follow(user=user, person=person)
            elif obj.startswith("l"):
                liste = List.objects.get(id=int(id))
                profile.follow_list(liste)
                return Follow(user=user, liste=liste)

class Rating(graphene.Mutation):
    user = graphene.Field(UserType)
    movie = graphene.Field(MovieType)
    class Arguments:
        id = graphene.Int()
        rate = graphene.Float()
        date = graphene.types.datetime.Date(required=False)
        notes = graphene.String(required=False)

    def mutate(self,info,id, rate, date=None, notes=None):
        if info.context.user.is_authenticated:
            user = info.context.user
            profile = user.profile
            movie = Movie.objects.get(id=id)
            profile.rate(movie, rate, notes=notes, date=date )
            return Rating(user=user, movie=movie)



class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info):
        return cls(user=info.context.user)



class Mutation(graphene.ObjectType):
    follow= Follow.Field()
    rating = Rating.Field()
    bookmark = Bookmark.Field()
    create_user = CreateUser.Field()
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()



schema = graphene.Schema(query=Query, mutation=Mutation)

"""
mutation TokenAuth($username: String!, $password: String!) {
  tokenAuth(username: $username, password: $password) {
    token
  }
}


mutation VerifyToken($token: String!) {
  verifyToken(token: $token) {
    payload
  }
}

mutation RefreshToken($token: String!) {
  refreshToken(token: $token) {
    token
    payload
  }
}


"""
