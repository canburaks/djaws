from items.models import Rating,Movie, List, MovieImage, Video, Topic
from persons.models import Person, PersonImage, Director, Crew
from persons.profile import Profile, Follow
from django.contrib.auth import get_user_model
import graphene
from django_mysql.models import JSONField
from graphene_django.types import DjangoObjectType
from graphene_django.converter import convert_django_field
from django.db.models import Q

from .types import (VideoType, MovieType, MovieListType, RatingType, ProfileType,ProfileType2, PersonType,
        CustomListType, CustomMovieType, DirectorPersonMixType,
        DirectorType, TopicType, ListType, UserType, CrewType, movie_defer)

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



class CustomSearchType(graphene.ObjectType):
    movies = graphene.List(MovieType)
    length = graphene.Int()

    def __init__(self, search, first=None, skip=None, viewer=None):
        self.search = search
        self.first = first
        self.skip = skip
        self.count = 0

    def resolve_length(self,info):
        return self.count

    def resolve_movies(self, info, **kwargs):
        first = self.first
        skip = self.skip
        search = self.search
        words = multi_word_search(search)
        if len(words)==1:
            filter = ( Q(name__icontains=words[0]) )
            result = Movie.objects.defer(*movie_defer).filter(filter)
            self.count += result.count()
            if first:
                return result[skip : skip + first]
            else:
                return result

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
            self.count += result.count()
            if first:
                return result[ skip : skip + first ]

            else:
                return result

