from django.db import models
import os, sys, inspect
import random
import numpy as np
from django.core.cache import cache
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"cython")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)
import calculations as af



from items.models import Movie
class Ms():
    def __init__(self, movie_id):
        from items.models import Movie
        if isinstance(movie_id, Movie):
            self.movie_id = "m{}".format(movie_id.id)
        elif isinstance(movie_id, int ):
            self.movie_id = "m{}".format(movie_id)
        elif isinstance(movie_id, str) and not movie_id.startswith("m"):
            self.movie_id = "m{}".format(movie_id)
        elif isinstance(movie_id, str) and movie_id.startswith("m"):
            self.movie_id = movie_id

    @property
    def userset(self):
        return cache.get(self.movie_id)
    
    def commons(self, other_movie):
        return np.intersect1d(np.array(self.userset), np.array(other_movie.userset))

    def commons_length(self, other_movie):
        return np.intersect1d(np.array(self.userset), np.array(other_movie.userset)).shape[0]

class Rs():
    def __init__(self, user_id):
        self.ratings = cache.get(user_id)
    
    """
    property
    def ratings(self):
        return cache.get(self.user_id)
    """

    @property
    def movieset(self):
        return np.array([x for x in self.ratings.keys()], dtype=np.uint32)

    @property
    def average(self):
        return af.mean(self.ratings)

    def commons(self,other_user):
        umovies = self.movieset
        vmovies = other_user.movieset
        return np.intersect1d(umovies, vmovies)
    
    def commons_length(self, other_user):
        return np.intersect1d( self.movieset, other_user.movieset).shape[0] 
    
    def vector(self, common_movies):
        return np.array([self.ratings.get(str(x)) for x in common_movies ], dtype=np.float64)
    
    def normalized_vector(self, common_movies):
        self_vector = self.vector(common_movies)
        mean_vector = np.full(len(common_movies), self.average)
        return self_vector - mean_vector

    def pearson(self, other_user):
        common_movies = self.commons(other_user)
        if len(common_movies)>0:
            self_vector = self.vector(common_movies)
            other_vector = other_user.vector(common_movies)
            ubar = self.average
            vbar = self.average
            return af.pearson(self_vector, other_vector, ubar, vbar)
        else:
            return 0

    def final_calculation(self,list_of_highly_correlated_users, movie_id):
        # [ [average, rating_of_target_movie, correlation],[]...]
        userlist = [[x[0].average, x[0].ratings.get(movie_id), x[1]] for x in list_of_highly_correlated_users]
        return af.final(userlist)
        

    def prediction(self,movie):
        if isinstance(movie, Movie):
            movid = str(movie.id)
        elif isinstance(movie, int):
            movid = str(movie)
        elif isinstance(movie, str):
            movid = movie
        else:
            print("no movie id")
        movie_all_userset = Ms(movie).userset
        length_of_movie_userset = len(movie_all_userset)
        if length_of_movie_userset>8000:
            movie_userset = random.sample(movie_all_userset, 8000)
        else:
            movie_userset = movie_all_userset
        print("{} of users that rated target movie".format(len(movie_userset)))
        users_that_have_commons = {}
        for user_id in movie_userset:
            rs_user = Rs(user_id)

            if len(movie_userset)>7000:
                minimum_common_threshold = 24
            elif len(movie_userset)>2000 and len(movie_userset)<7000:
                minimum_common_threshold = 19
            else:
                minimum_common_threshold = 12
            
            if self.commons_length(rs_user)>minimum_common_threshold:
                users_that_have_commons.update({ rs_user:self.commons_length(rs_user) })
        neighbours_that_max_shared = sorted(users_that_have_commons.items(), key=lambda x:x[1], reverse=True)[:300]
        print("Neighbours that brought:{}".format(len(neighbours_that_max_shared)))
        
        users_with_pearson = {}
        for neighbour in neighbours_that_max_shared:
            correlation = self.pearson(neighbour[0])
            if correlation>0.2:
                users_with_pearson.update({ neighbour[0] : correlation })
        
        highest_correlated_users = sorted(users_with_pearson.items(), key=lambda x:x[1], reverse=True)[:20]
        print("{} number of Highest correlated person".format(len(highest_correlated_users)))
        pred = self.average + self.final_calculation(highest_correlated_users, str(movid))
        
        if pred>5 or pred<=0:
                return 0
        elif (pred>=4.4) and (pred<4.6):
            return 4.2
        elif (pred>=4.6) and (pred<4.8):
            return 4.3
        elif (pred>=4.8) and (pred<5):
            return 4.4
        elif pred==5:
            return 4.5
        return pred - 0.2






