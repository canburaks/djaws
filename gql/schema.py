from django.conf import settings
from django.contrib.auth import get_user_model
from django_mysql.models import JSONField
from items.models import Movie, List, MovieImage, Video, Topic
from persons.models import Person, Profile, PersonImage, Director

from items.models import Rating
from algorithm.models import Dummy
import graphene
import graphql_jwt
from graphql_jwt.decorators import login_required
from graphene_django.types import DjangoObjectType
from django.db.models import Q
from graphene_django.converter import convert_django_field

from .types import (VideoType, MovieType, ProfileType, PersonType,
        DirectorType, TopicType, ListType, UserType, RatingType)

def paginate(query, first, skip):
    return query[int(skip) : int(skip) + int(first)]

class ListQuery(object):

    list_of_lists = graphene.List(ListType,
            first=graphene.Int(default_value=None),
            skip=graphene.Int(default_value=None))

    list_of_topics = graphene.List(TopicType,
            first=graphene.Int(default_value=None),
            skip=graphene.Int(default_value=None))

    liste = graphene.List(MovieType, id=graphene.Int(default_value=None),
            name=graphene.String(default_value=None),
            search=graphene.String(default_value=None),
            first=graphene.Int(default_value=None),
            skip=graphene.Int(default_value=None))

    list_of_directors = graphene.List(DirectorType,
            first=graphene.Int(default_value=None),
            skip=graphene.Int(default_value=None))

    length = graphene.Int(
        id=graphene.Int(default_value=None),
        name=graphene.String(default_value=None),
        search=graphene.String(default_value=None))


    def resolve_list_of_directors(self, info, **kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        qs =  Director.objects.all()
        if first:
            return paginate(qs, first, skip)
        return qs

    def resolve_list_of_lists(self, info, **kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        qs = List.objects.all()
        if first:
            return paginate(qs, first, skip)
        return qs

    def resolve_list_of_topics(self, info, **kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        qs = Topic.objects.all()
        if first:
            return paginate(qs, first, skip)
        return qs

    def resolve_liste(self, info, **kwargs):
        id = kwargs.get("id")
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        name = kwargs.get("name")
        search = kwargs.get("search")
        if id is not None:
            qs = List.objects.get(id=id).movies.defer("imdb_id",
                    "tmdb_id","actors","data","ratings_dummy","director","summary",
                    "tags","ratings_user").order_by("-imdb_rating")
            if first:
                return paginate(qs, first, skip)
            return qs

        if name is not None:
            user = info.context.user
            if user.is_authenticated:
                if name=="ratings":
                    qs = Movie.objects.filter(rates__in=user.profile.rates.only("movie").all()).defer("imdb_id",
                            "tmdb_id","actors","data","ratings_dummy","director","summary",
                            "tags","ratings_user")
                    if first:
                        return paginate(qs, first, skip)
                    return qs

                if name=="bookmarks":
                    qs = Movie.objects.filter(bookmarked=user.profile).defer("imdb_id",
                            "tmdb_id","actors","data","ratings_dummy","director","summary",
                            "tags","ratings_user")
                    if first:
                        return paginate(qs, first, skip)
                    return qs
            else :
                raise Exception('Authentication credentials were not provided')

        if search:
            filter = ( Q(name__icontains=search) )
            qs = Movie.objects.filter(filter).defer("imdb_id","tmdb_id","actors","data",
                    "ratings_dummy","director","summary","tags","ratings_user")
            if first:
                return paginate(qs, first, skip)
            return qs

    def resolve_length(self, info, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")
        search = kwargs.get("search")

        if id is not None:
            return List.objects.get(id=id).movies.all().count()

        if name is not None:
            user = info.context.user
            if user.is_authenticated:
                if name=="ratings":
                    return user.profile.rates.all().count()
                elif name=="bookmarks":
                    return user.profile.bookmarks.all().count()
                elif name=="list_of_lists":
                    return List.objects.all().count()
                elif name=="list_of_directors":
                    return  Director.objects.all().count()
                elif name=="list_of_topics":
                    return Topic.objects.all().count()
            else :
                raise Exception('Authentication credentials were not provided')

        if search:
            filter = (
                Q(name__icontains=search)
                #| Q(summary__icontains=search)
            )
            return Movie.objects.filter(filter).count()



class Query(ListQuery, graphene.ObjectType):

    topic = graphene.Field(TopicType,id=graphene.Int())

    prediction = graphene.Float(movieId=graphene.Int())

    person = graphene.Field(PersonType,id=graphene.String(default_value=None))

    viewer = graphene.Field(ProfileType, username=graphene.String())

    movie = graphene.Field(MovieType,id=graphene.Int(),name=graphene.String())


    def resolve_topic(self, info, **kwargs):
        id = kwargs.get("id")
        return Topic.objects.get(id=id)

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


    def resolve_movie(self, info, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")

        if id is not None:
            return Movie.objects.get(id=id)

        if name is not None:
            return Movie.objects.get(name=name)






from .mutations import CreateUser, Bookmark, Follow, Rating, ObtainJSONWebToken

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
