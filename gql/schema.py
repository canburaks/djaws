from django.conf import settings
from django.contrib.auth import get_user_model
from django_mysql.models import JSONField
from items.models import Movie,Rating, List, MovieImage, Video, Topic
from persons.models import Person, PersonImage, Director, Crew
from persons.profile import Profile, Follow

import graphene
import graphql_jwt
from graphql_jwt.decorators import login_required
from graphene_django.types import DjangoObjectType
from django.db.models import Q
from graphene_django.converter import convert_django_field
from graphene_django.debug import DjangoDebug

from .types import (VideoType, MovieType, MovieListType, RatingType, ProfileType,ProfileType2, PersonType,
        CustomListType, CustomMovieType, DirectorPersonMixType,
        DirectorType, TopicType, ListType, UserType, CrewType, movie_defer)
from .search import CustomSearchType

def paginate(query, first, skip):
    return query[int(skip) : int(skip) + int(first)]

def multi_word_search(text):
    text = text.replace("'" , " ")
    text = text.replace("," , " ")
    text_filtered = text.split(" ")
    word_list = list(filter(lambda x: len(x)>1 and (x.lower() !="the"), text_filtered))
    word_list = list(map( lambda x: x.lower(), word_list ))
    return word_list

def multi_word_query(*arg):
    if len(arg)==1:
        one_word = ( Q(name__icontains=arg[0]) )

def is_owner(self, info):
    user = info.context.user
    if user.username == self.username:
        return True
    return False

class ListQuery(object):
    list_of_movie_search = graphene.List(MovieType,
                search=graphene.String(default_value=None),
                first=graphene.Int(default_value=None),
                skip=graphene.Int(default_value=None))

    list_of_bookmarks = graphene.List(MovieType,
                username=graphene.String(required=True),
                first=graphene.Int(default_value=None),
                skip=graphene.Int(default_value=None))

    list_of_ratings_movie = graphene.List(MovieType,
                username=graphene.String(required=True),
                first=graphene.Int(default_value=None),
                skip=graphene.Int(default_value=None))

    list_of_crew = graphene.List(CrewType, movie_id=graphene.Int())

    list_of_diary = graphene.List(MovieType,
            first=graphene.Int(default_value=None),
            skip=graphene.Int(default_value=None))

    list_of_lists = graphene.List(CustomListType,
            first=graphene.Int(default_value=None),
            skip=graphene.Int(default_value=None))

    list_of_categorical_lists= graphene.List(CustomListType,
            admin=graphene.Boolean(default_value=True), # return only admin created lists or not 
            list_type=graphene.String(),
            first=graphene.Int(default_value=None),
            skip=graphene.Int(default_value=None))

    list_of_topics = graphene.List(TopicType,
            first=graphene.Int(default_value=None),
            skip=graphene.Int(default_value=None))

    list_of_movies = graphene.List(MovieType, 
            id=graphene.Int(default_value=None),
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


    def resolve_list_of_bookmarks(self, info, **kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        username = kwargs.get("username")
        user = info.context.user
        if user.is_authenticated:
            qs = user.profile.bookmarks.defer(*movie_defer).all()
            if first:
                return  qs[skip : skip + first]
            else:
                return  qs

    def resolve_list_of_ratings_movie(self, info, **kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        username = kwargs.get("username")
        user = info.context.user
        if user.is_authenticated:
            qs = Movie.objects.defer(*movie_defer).filter(rates__profile=user.profile)
            if first:
                return  qs[skip : skip + first]
            else:
                return  qs  


    def resolve_list_of_movie_search(self, info, **kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        search = kwargs.get("search")
        if search:
            words = multi_word_search(search)
            if len(words)==1:
                filter = ( Q(name__icontains=words[0]) )
                if first:
                    return Movie.objects.defer(*movie_defer).filter(filter)[skip : skip + first]
                else:
                    return Movie.objects.defer(*movie_defer).filter(filter)
            elif len(words)>1:
                term1 = " ".join(words)
                filter1 = ( Q(name__icontains=term1))
                qs1 = Movie.objects.defer(*movie_defer).filter(filter1)
                result = [x for x in qs1]


                filter2 = (Q(name__icontains=words[0]))
                qs2 = Movie.objects.defer(*movie_defer).filter(filter2)

                for i in range(1, len(words)):
                    kw = words[i]
                    qs2 = qs2.filter(Q(name__icontains=kw))

                for mov in qs2:
                    result.append(mov)

                result = list(set(result))
                if first:
                    return result[ skip : skip + first ]

                else:
                    return result
    
    def resolve_list_of_crew(self, info, **kwargs):
        movie_id = kwargs.get("movie_id")
        show_jobs = ["d", "a"]
        qs = Crew.objects.filter(movie=Movie.objects.get(id=movie_id),
            job__in=show_jobs, person__bio__isnull=False).select_related("person").defer("data").exclude(
                person__bio__isnull=True).exclude(person__bio__exact='')
        return qs

    
    def resolve_list_of_diary(self, info, **kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        user = info.context.user
        if user.is_authenticated:
            Q1 = Q(notes__isnull=False)
            Q2 = Q(date__isnull=False)
            rates = user.profile.rates.filter(Q1 | Q2)
            qs = Movie.objects.filter(rates__in=rates).defer(*movie_defer)
        if first:
            return paginate(qs, first, skip)
        return qs

    def resolve_list_of_ratings(self, info, **kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        user = info.context.user
        if user.is_authenticated:
            qs =  Rating.objects.select_related("movie", "profile").filter(profile__username=user.username)
            if first:
                return paginate(qs, first, skip)
            return qs

    def resolve_list_of_directors(self, info, **kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        qs =  Director.objects.filter(active=True)
        if first:
            return paginate(qs, first, skip)
        return qs

    def resolve_list_of_lists(self, info, **kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        qs = List.objects.filter(owner__username="admin").only("id").values_list("id", flat=True)
        if first:
            qs = qs[skip : skip + first]
        else:
            qs = qs
        return [CustomListType(id=x) for x in qs ]

    def resolve_list_of_categorical_lists(self, info, **kwargs):
        user = info.context.user
        if user.is_authenticated:
            first = kwargs.get("first")
            skip = kwargs.get("skip")
            list_type = kwargs.get("list_type")
            admin = kwargs.get("admin")
            model_types = ["df", "fw", "gr", "ms"]

            if list_type!=None and (list_type.lower() in model_types):
                qs = List.objects.filter(list_type=list_type).only("id").values_list("id", flat=True)
            else:
                qs = List.objects.filter(list_type__in=model_types).only("id").values_list("id", flat=True)

            if admin==True or admin==None:
                qs = qs.filter(owner__username="admin")
            if first:
                qs = qs[skip : skip + first]
            else:
                qs = qs
            return [CustomListType(id=x) for x in qs ]
        else:
            raise Exception('Authentication credentials were not provided')


    def resolve_list_of_topics(self, info, **kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        qs = Topic.objects.all()
        if first:
            return paginate(qs, first, skip)
        return qs

    def resolve_list_of_movies(self, info, **kwargs):
        id = kwargs.get("id")
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        name = kwargs.get("name")
        search = kwargs.get("search")
        if id is not None:
            """
            qs = List.objects.get(id=id).movies.defer(*movie_defer)
            """
            ls = List.objects.only("movies").get(id=id)
            if first:
                return Movie.objects.defer("imdb_id","imdb_rating","summary",
                            "tmdb_id","director","data",
                            "tags").filter(lists=ls)[skip : skip + first]
            else:
                return  Movie.objects.defer("imdb_id","imdb_rating","summary",
                            "tmdb_id","director","data",
                            "tags").filter(lists=ls)

        if name is not None:
            user = info.context.user
            if user.is_authenticated:
                if name=="ratings":
                    if first:
                        return Movie.objects.defer("imdb_id","imdb_rating",
                                "tmdb_id","data","director","summary",
                                "tags").filter(rates__in=user.profile.rates.only("movie"))[skip : skip + first]
                    else:
                        return Movie.objects.defer("imdb_id","imdb_rating",
                                "tmdb_id","data","director","summary",
                                "tags").filter(rates__in=user.profile.rates.only("movie"))

                if name=="bookmarks":
                    if first:
                        return  Movie.objects.defer("imdb_id","imdb_rating",
                                "tmdb_id","data","director","summary",
                                "tags").filter(bookmarked=user.profile)[skip : skip + first]
                    else:
                        return  Movie.objects.defer("imdb_id","imdb_rating",
                                "tmdb_id","data","director","summary",
                                "tags").filter(bookmarked=user.profile)        

            else :
                raise Exception('Authentication credentials were not provided')

        if search:
            words = multi_word_search(search)
            if len(words)==1:
                filter = ( Q(name__icontains=words[0]) )
                if first:
                    return Movie.objects.defer("imdb_id","imdb_rating","tmdb_id","data",
                    "director","summary","tags").filter(filter)[skip : skip + first]
                else:
                    return Movie.objects.defer("imdb_id","imdb_rating","tmdb_id","data",
                    "director","summary","tags").filter(filter)
            elif len(words)>1:
                term1 = " ".join(words)
                filter1 = ( Q(name__icontains=term1))
                qs1 = Movie.objects.defer("imdb_id","imdb_rating","tmdb_id","data",
                    "director","summary","tags").filter(filter1)
                result = [x for x in qs1]


                filter2 = (Q(name__icontains=words[0]))
                qs2 = Movie.objects.defer("imdb_id","imdb_rating","tmdb_id","data",
                    "director","summary","tags").filter(filter2)

                for i in range(1, len(words)):
                    kw = words[i]
                    qs2 = qs2.filter(Q(name__icontains=kw))

                for mov in qs2:
                    result.append(mov)

                result = list(set(result))
                """
                for word in words:
                    if len(word)>4:
                        filter2 = ( Q(name__icontains=word) )
                        qs2 = Movie.objects.defer("imdb_id","imdb_rating","tmdb_id","data",
                        ,"director","summary","tags").filter(filter2)
                        for mov in qs2:
                            result.append(mov)
                """
                if first:
                    return result[ skip : skip + first ]

                else:
                    return result


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
                    return  Director.objects.filter(active=True).count()
                elif name=="list_of_topics":
                    return Topic.objects.all().count()
                elif name=="list_of_diary":
                    return user.profile.rates.filter(notes__isnull=False).count()
            else :
                raise Exception('Authentication credentials were not provided')

        if search:
            filter = (
                Q(name__icontains=search)
                #| Q(summary__icontains=search)
            )
            return Movie.objects.filter(filter).count()

class SearchQuery(object):
    search = graphene.Field(CustomSearchType,
                search=graphene.String(),
                first=graphene.Int(default_value=None),
                skip=graphene.Int(default_value=None))

    search_movie = graphene.List(MovieType,
                search=graphene.String(),
                first=graphene.Int(default_value=None),
                skip=graphene.Int(default_value=None))

    search_list = graphene.List(CustomListType,
                search=graphene.String(),
                first=graphene.Int(default_value=None),
                skip=graphene.Int(default_value=None))

    search_director = graphene.List(DirectorType,
                search=graphene.String(),
                first=graphene.Int(default_value=None),
                skip=graphene.Int(default_value=None))

    search_length = graphene.List(graphene.Int,
                search=graphene.String(),
                first=graphene.Int(default_value=None),
                skip=graphene.Int(default_value=None))

    def resolve_search(self, info, **kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        search = kwargs.get("search")
        return CustomSearchType(search=search, first=first, skip=skip)


    def resolve_search_movie(self, info, **kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        search = kwargs.get("search")
        words = multi_word_search(search)
        if len(words)==1:
            filter = ( Q(name__icontains=words[0]) )
            if first:
                return Movie.objects.defer(*movie_defer).filter(filter)[skip : skip + first]
            else:
                return Movie.objects.defer(*movie_defer).filter(filter)
        elif len(words)>1:
            term1 = " ".join(words)
            filter1 = ( Q(name__icontains=term1))
            qs1 = Movie.objects.defer(*movie_defer).filter(filter1)
            result = [x for x in qs1]


            filter2 = (Q(name__icontains=words[0]))
            qs2 = Movie.objects.defer(*movie_defer).filter(filter2)

            for i in range(1, len(words)):
                kw = words[i]
                qs2 = qs2.filter(Q(name__icontains=kw))

            for mov in qs2:
                result.append(mov)

            result = list(set(result))
            if first:
                return result[ skip : skip + first ]

            else:
                return result

    def resolve_search_list(self, info, **kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        search = kwargs.get("search")
        words = multi_word_search(search)
        if len(words)==1:
            filter1 = ( Q(name__icontains=words[0]) )
            if first:
                qs = List.objects.filter(filter1).only("id", "name")[skip : skip + first]
                liste_list = [CustomListType(id=x.id) for x in qs]
                return liste_list
            else:
                qs = List.objects.filter(filter1).only("id", "name")
                liste_list = [CustomListType(id=x.id) for x in qs]
                return liste_list
        elif len(words)>1:
            term1 = " ".join(words)
            filter2 = ( Q(name__icontains=term1))
            qs1 = List.objects.only("id","name").filter(filter2)
            result = [x for x in qs1]


            filter3 = (Q(name__icontains=words[0]))
            qs2 = List.objects.only("id","name").filter(filter3)

            for i in range(1, len(words)):
                kw = words[i]
                qs2 = qs2.filter(Q(name__icontains=kw))

            for mov in qs2:
                result.append(mov)

            result = list(set(result))
            if first:
                liste_list = [CustomListType(id=x.id) for x in result]
                return liste_list[ skip : skip + first ]
            else:
                liste_list = [CustomListType(id=x.id) for x in result]
                return liste_list

    def resolve_search_director(self, info, **kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        search = kwargs.get("search")
        words = multi_word_search(search)
        if len(words)==1:
            director_filter = ( Q(name__icontains=words[0]))
            if first:
                return Director.objects.defer("bio", "data").filter(director_filter)[skip : skip + first]
            else:
                return Director.objects.defer("bio", "data").filter(director_filter)

        elif len(words)>1:
            term1 = " ".join(words)
            filter1 = ( Q(name__icontains=term1))
            qs1 = Director.objects.defer("bio", "data").filter(filter1)

            filter2 = (Q(name__icontains=words[0]))
            qs2 = Director.objects.defer("bio", "data").filter(filter2)

            for i in range(1, len(words)):
                kw = words[i]
                qs2 = qs2.filter(Q(name__icontains=kw))

            result = qs1 | qs2
            result = list(set(result))
            if first:
                return result[ skip : skip + first ]
            else:
                return result


class Query(ListQuery, SearchQuery, graphene.ObjectType):
    #debug = graphene.Field(DjangoDebug, name='__debug')
    liste = graphene.Field(CustomListType, id=graphene.Int(required=True),
                    first=graphene.Int(default_value=None),
                    skip=graphene.Int(default_value=None))

    rating = graphene.Field(RatingType,id=graphene.Int())

    topic = graphene.Field(TopicType,id=graphene.Int())

    prediction = graphene.Float(movieId=graphene.Int(default_value=None), id=graphene.Int(default_value=None))

    person = graphene.Field(PersonType,id=graphene.String(default_value=None))
    
    director = graphene.Field(DirectorType,id=graphene.String(default_value=None))

    director_person_mix = graphene.Field(DirectorPersonMixType,id=graphene.String(default_value=None))


    viewer = graphene.Field(ProfileType)

    profile = graphene.Field(ProfileType, username=graphene.String())
    #myself = graphene.Field(MyProfileType, username=graphene.String(default_value=None))

    omovie = graphene.Field(MovieType,id=graphene.Int(),name=graphene.String())

    movie = graphene.Field(CustomMovieType,id=graphene.Int())

    dummy =  graphene.types.json.JSONString(id=graphene.String())

    def resolve_liste(self, info, **kwargs):
        id = kwargs.get("id")
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        if info.context.user.is_authenticated:
            user = info.context.user
            return CustomListType(id, first=first, skip=skip, viewer=user.profile)

        return CustomListType(id, first=first, skip=skip)




    def resolve_profile(self, info, **kwargs):
        username = kwargs.get("username")
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Authentication credentials were not provided')
            return None
        elif info.context.user.is_authenticated:
            user = info.context.user
            if user.username==username:
                is_self=True
                return user.profile
            else:
                is_self=False
            return Profile.objects.get(username=username)

    def resolve_dummy(self, info, **kwargs):
        from django.core.cache import cache
        id = kwargs.get("id")
        return cache.get(id)
        
    def resolve_rating(self, info,**kwargs):
        movid = kwargs.get("id")
        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            rates = profile.rates.get(movie__id=movid)
            return rates
            #return Rating.objects.get(profile=profile, movie=Movie.objects.get(id=id))

    def resolve_topic(self, info, **kwargs):
        id = kwargs.get("id")
        return Topic.objects.get(id=id)

    def resolve_prediction(self, info,**kwargs):
        # Change in future, only use "id"
        if kwargs.get("id"):
            movid = kwargs.get("id")
        elif kwargs.get("movieId"):
            movid = kwargs.get("movieId")

        if info.context.user.is_authenticated:
            profile = info.context.user.profile
            if len(profile.ratings.items())<30:
                return 0
            movie = Movie.objects.get(id=movid)
            result = profile.predict(movie)
            return result

    def resolve_director(self, info, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")
        if id is not None:
            return Person.objects.get(id=id)

    def resolve_director_person_mix(self, info, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")
        if id is not None:
            return Person.objects.get(id=id)

    def resolve_person(self, info, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")
        if id is not None:
            return Person.objects.get(id=id)

    def resolve_viewer(self, info, **kwargs):
        if info.context.user.is_authenticated:
            user = info.context.user
            return user.profile
        else:
            raise Exception('Authentication credentials were not provided')

    def resolve_movie(self, info, **kwargs):
        id = kwargs.get("id")
        if info.context.user.is_authenticated:
            user = info.context.user
            return CustomMovieType(id=id, viewer=user.profile)
        return CustomMovieType(id=id)

    def resolve_omovie(self, info, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")

        if id is not None:
            return Movie.objects.defer(*movie_defer).get(id=id)

        if name is not None:
            return Movie.objects.defer(*movie_defer).get(name=name)


from .mutations import CreateUser, Bookmark, Follow, Rating, ObtainJSONWebToken, Logout,Prediction, DummyMutation, RedisMutation, Fav
from .profile_mutations import CreateList, DeleteList, AddMovie, RemoveMovie, ProfileInfo, AddMovies


class Mutation(graphene.ObjectType):
    prediction = Prediction.Field()
    profile_info_mutation = ProfileInfo.Field()
    add_movies = AddMovies.Field()
    add_movie = AddMovie.Field()
    remove_movie = RemoveMovie.Field()
    create_list = CreateList.Field()
    delete_list = DeleteList.Field()
    #redis = RedisMutation.Field()
    dummy = DummyMutation.Field()
    follow= Follow.Field()
    fav= Fav.Field()
    logout = Logout.Field()
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
