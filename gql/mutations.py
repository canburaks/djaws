
from items.models import Movie, List, MovieImage, Video, Rating, Topic, Article
from persons.models import Director, Person, Profile, PersonImage
from django.contrib.auth import get_user_model
from django_mysql.models import JSONField

from graphene_django.types import DjangoObjectType
from graphene_django.converter import convert_django_field

import graphene
import graphql_jwt
from graphql_jwt.decorators import login_required

from .types import (VideoType, MovieType, ProfileType, PersonType,
        DirectorType, TopicType, ListType, UserType, RatingType)

@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return graphene.String()


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
    topic = graphene.Field(TopicType)

    class Arguments:
        id = graphene.String()
        obj = graphene.String()
    def mutate(self,info,id, obj):
        if info.context.user.is_authenticated:
            user = info.context.user
            profile = user.profile
            if obj.startswith("p"):
                person = Person.objects.get(id=id)
                profile.follow_person(person)
                return Follow(user=user, person=person)
            elif obj.startswith("l"):
                liste = List.objects.get(id=int(id))
                profile.follow_list(liste)
                return Follow(user=user, liste=liste)
            elif obj.startswith("t"):
                topic = Topic.objects.get(id=int(id))
                profile.follow_topic(topic)
                return Follow(user=user, topic=topic)
            
            

class Rating(graphene.Mutation):
    user = graphene.Field(UserType)
    movie = graphene.Field(MovieType)
    rating = graphene.Field(RatingType)
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
            rating = profile.rates.get(movie=movie)
            return Rating(user=user, movie=movie, rating=rating)

class Logout(graphene.Mutation):
    user = graphene.Field(UserType)

    def mutate(self, info):
        if info.context.user.is_authenticated:
            user = info.context.user
            from django.contrib.auth import logout
            logout()
        return Logout(user=user)



class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info):
        return cls(user=info.context.user)