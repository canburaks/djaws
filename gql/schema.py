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

@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return graphene.String()


class MovieType(DjangoObjectType):
    image = graphene.String() #for property types
    
    class Meta:
        model = Movie

    """
    def resolve_poster(self, *_):
        if self.poster:
            return '{}{}'.format(settings.MEDIA_URL, self.poster)
        else:
            return """

class ProfileType(DjangoObjectType):
    token = graphene.String()
    class Meta:
        model = Profile

class PersonType(DjangoObjectType):
    class Meta:
        model = Person

class UserType(DjangoObjectType):
    
    class Meta:
        model = get_user_model()
    def resolve_token(self, info, **kwargs):
        return graphql_jwt.shortcuts.get_token(self)

class Query(graphene.ObjectType):
    all_movies = graphene.List(MovieType)
    lists = graphene.List(MovieType, id=graphene.Int(), name=graphene.String())
    movie = graphene.Field(MovieType,id=graphene.Int(),name=graphene.String())

    all_profiles = graphene.List(ProfileType)


    def resolve_all_movies(self, info, **kwargs):
        return Movie.objects.all().order_by("-year")[:1000]

    def resolve_lists(self, info, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")

        if id is not None:
            if id==0:
                return Movie.objects.all().order_by("-year")[:1000]
            return List.objects.get(id=id).movies.all().order_by("imdb_rating")
        if name is not None:
            return List.objects.get(name=name).movies.all()
        return Movie.objects.all().order_by("-year")[:1000]

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



class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
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
