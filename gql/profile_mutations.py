from persons.profile import Profile, Follow
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

class CreateList(graphene.Mutation):
    profile = graphene.Field(ProfileType)
    liste = graphene.Field(ListType)
    message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        summary = graphene.String(required=False)
        public = graphene.Boolean(required=False)
    
    def mutate(self, info, name, public=True, summary=None):
        if info.context.user.is_authenticated:
            if List.objects.filter(name=name).exists():
                raise Exception("Choose another name for the list")
            print("public", public)
            user = info.context.user
            profile = user.profile
            new_list_id = List.autokey()
            try:
                new_list = List(id=new_list_id, name=name,
                    summary=summary, owner=profile, public=public)
                new_list.save()
                return CreateList(profile=profile, liste=new_list, message="List successfully created" )
            except:
                try:
                    incremented_id = new_list_id + 1
                    new_list = List(id=incremented_id, name=name,
                        summary=summary, owner=profile, public=public)
                    new_list.save()
                    return CreateList(profile=profile, liste=new_list, message="List successfully created")
                except:
                    raise Exception("List was not create, check list id")

class DeleteList(graphene.Mutation):
    profile = graphene.Field(ProfileType)
    message = graphene.String()
    class Arguments:
        id = graphene.Int(required=True)

    def mutate(self, info, id):
        if info.context.user.is_authenticated:
            user = info.context.user
            profile = user.profile

            target_list = List.objects.get(id=id)
            if target_list.owner==profile:
                target_list.delete()
                return DeleteList(profile=profile, message="List successfully deleted.")
            else:
                raise Exception("You are not the owner")
        else:
            raise Exception("Please Login")

class AddMovie(graphene.Mutation):
    movie = graphene.Field(MovieType)
    liste = graphene.Field(ListType)
    message= graphene.String()
    class Arguments:
        movie_id = graphene.Int(required=True)
        liste_id = graphene.Int(required=True)

    def mutate(self, info, id):
        if info.context.user.is_authenticated:
            user = info.context.user
            profile = user.profile
            target_list = List.objects.select_related("owner").only("id","owner","public").get(id=liste_id)
            if target_list.owner==profile:
                target_movie = Movie.objects.only("id").get(id=movie_id)
                target_list.movies.add(target_movie)
                return AddMovie(movie=movie, liste=target_list, message="Movie was added.")
            else:
                raise Exception("You are not the owner of the list")
        else:
            raise Exception("Please login again.")

class RemoveMovie(graphene.Mutation):
    movie = graphene.Field(MovieType)
    liste = graphene.Field(ListType)
    message= graphene.String()
    class Arguments:
        movie_id = graphene.Int(required=True)
        liste_id = graphene.Int(required=True)

    def mutate(self, info, id):
        if info.context.user.is_authenticated:
            user = info.context.user
            profile = user.profile
            target_list = List.objects.select_related("owner").prefetch_related("movies").only("id","owner","movies").get(id=liste_id)
            if target_list.owner==profile:
                target_movie = Movie.objects.only("id").get(id=movie_id)
                target_list.movies.remove(target_movie)
                return RemoveMovie(movie=movie, liste=target_list, message="Movie was removed.")
            else:
                raise Exception("You are not the owner of the list")
        else:
            raise Exception("Please login again.")