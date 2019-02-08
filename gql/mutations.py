
from items.models import Movie, List, MovieImage, Video, Rating, Topic, Article
from persons.models import Director, Person, PersonImage
from persons.profile import Profile

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

def string_to_date(text):
    from datetime import date
    elements = text.strip().split("-")
    print(elements)
    return date(int(elements[0]), int(elements[1]), int(elements[2]))






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

class Fav(graphene.Mutation):
    user = graphene.Field(UserType)
    video = graphene.Field(VideoType)
    movie = graphene.Field(MovieType)


    class Arguments:
        id = graphene.Int()
        type = graphene.String()
    def mutate(self,info,id, type):
        if info.context.user.is_authenticated:
            user = info.context.user
            profile = user.profile
            if type.lower().startswith("v"):
                video = Video.objects.get(id=id)
                profile.fav(video, type="video")
                return Fav(user=user, video=video)

            elif type.lower().startswith("m"):
                movie = Movie.objects.get(id=id)
                profile.fav(movie, type="movie")
                return Fav(user=user, movie=movie)

class Follow(graphene.Mutation):
    user = graphene.Field(UserType)
    target_profile = graphene.Field(ProfileType)
    person = graphene.Field(PersonType)
    liste = graphene.Field(ListType)
    topic = graphene.Field(TopicType)

    class Arguments:
        obj = graphene.String()
        id = graphene.String(required=False)
        username = graphene.String(required=None)

    def mutate(self,info, obj, id=None, username=None):
        if info.context.user.is_authenticated:
            print("auth")
            user = info.context.user
            profile = user.profile
            if obj.startswith("p"):
                person = Person.objects.get(id=id)
                profile.follow_person(person)
                return Follow(user=user, person=person)

            elif obj.startswith("d"):
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

            elif obj.startswith("u"):
                target_profile = Profile.objects.get(username=username)
                profile.follow_profile(target_profile)
                return Follow(user=user, target_profile=target_profile)
        else:
            print("not auth")
            
            

class Rating(graphene.Mutation):
    user = graphene.Field(UserType)
    movie = graphene.Field(MovieType)
    rating = graphene.Field(RatingType)
    class Arguments:
        id = graphene.Int()
        rate = graphene.Float()
        date = graphene.String(required=False)
        notes = graphene.String(required=False)

    def mutate(self,info,id, rate, date=None, notes=None):
        if info.context.user.is_authenticated:
            user = info.context.user
            profile = user.profile
            movie = Movie.objects.get(id=id)
            if date:
                profile.rate(movie, rate, notes=notes, date=string_to_date(date))
            profile.rate(movie, rate, notes=notes)
            rating = profile.rates.get(movie=movie)
            return Rating(user=user, movie=movie, rating=rating)

class DummyMutation(graphene.Mutation):
    rating = graphene.String()
    class Arguments:
        id = graphene.String()
        dictionary = graphene.String()

    def mutate(self, info, id, dictionary):
        import json
        from django.core.cache import cache
        ddict = json.loads(dictionary)
        cache.set(id,ddict, None)
        resp = json.dumps(cache.get(id))
        return DummyMutation(rating=str(resp))

class RedisMutation(graphene.Mutation):
    result = graphene.String()
    class Arguments:
        start = graphene.Int()
        stop = graphene.Int()

    def mutate(self, info, start, stop):
        from algorithm.models import redis_setter
        result = redis_setter(start,stop)
        
        return RedisMutation(result=result)

class Logout(graphene.Mutation):
    user = graphene.Field(UserType)

    def mutate(self, info):
        if info.context.user.is_authenticated:
            user = info.context.user
            from django.contrib.auth import logout
            logout()
        return Logout(user=user)

class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)
    profile = graphene.Field(ProfileType)
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)


    def mutate(self, info, username, password, email):
        if User.objects.filter(username__iexact=username).exclude(email=email).exists():
            raise ValidationError('This username has already been taken!')
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


class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info):
        return cls(user=info.context.user)