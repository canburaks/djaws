from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import get_user_model
from django_mysql.models import JSONField
from items.models import Movie, List
from persons.models import Person, Profile
import graphene
import graphql_jwt
from graphql_jwt.decorators import login_required
from graphene_django.types import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Q
@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return graphene.String()


class MovieType(DjangoObjectType):
    image = graphene.String() #for property types
    pic = graphene.String()
    isBookmarked = graphene.Boolean()
    viewer_rating = graphene.Float()
    data = graphene.types.json.JSONString()
    tags = graphene.types.json.JSONString()

    class Meta:
        model = Movie

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

class ProfileType(DjangoObjectType):
    token = graphene.String()
    ratings = graphene.types.json.JSONString()
    len_bookmarks = graphene.Int()
    len_ratings = graphene.Int()
    class Meta:
        model = Profile
    def resolve_ratings(self, info, *_):
        return self.ratings
    
    def resolve_len_bookmarks(self, info):
        return self.bookmarks.count()
    def resolve_len_ratings(self, info):
        return len(self.ratings)
class PersonType(DjangoObjectType):
    class Meta:
        model = Person

class UserType(DjangoObjectType):

    class Meta:
        model = get_user_model()
    def resolve_token(self, info, **kwargs):
        return graphql_jwt.shortcuts.get_token(self)


class Query(graphene.ObjectType):
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
                result = Movie.objects.all().order_by("imdb_rating")
                if skip:
                    result = result[skip::]
                if first:
                    result = result[:first]
                return result
                
            result = List.objects.get(id=id).movies.all().order_by("imdb_rating")

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
                    result = Movie.objects.filter(id__in=profile_ratings)
                    if skip:
                        result = result[skip::]
                    if first:
                        result = result[:first]
                    return result
                if name=="bookmarks":
                    result = user.profile.bookmarks.all()
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
            result = Movie.objects.filter(filter)
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

class Rating(graphene.Mutation):
    user = graphene.Field(UserType)
    movie = graphene.Field(MovieType)
    class Arguments:
        id = graphene.Int()
        rate = graphene.Float()

    def mutate(self,info,id, rate):
        if info.context.user.is_authenticated:
            user = info.context.user
            profile = user.profile
            movie = Movie.objects.get(id=id)
            profile.rate(movie, rate)
            return Rating(user=user, movie=movie)

class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info):
        return cls(user=info.context.user)



class Mutation(graphene.ObjectType):
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
