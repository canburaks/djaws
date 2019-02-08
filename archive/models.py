from django.db import models
from django.db.models import IntegerField, Model
from django_mysql.models import SetCharField, SetTextField, JSONField

from items.models import Movie
from persons.profile import Profile
from algorithm import custom_functions as cbs

import os, sys, inspect
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"cython")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import cfunc as cc

USER_TYPE = (("u", "user"), ("d", "dummy"))




class MovieArchive(Model):
    movie_id = models.IntegerField(primary_key=True)
    dummyset = SetTextField(default=set,base_field=IntegerField())
    userset = SetTextField(default=set,base_field=IntegerField())

    def __str__(self):
        print(f"Movie Archive Id:{self.movie_id}")


class UserArchive(Model):
    user_id = models.IntegerField() # !!! User Id !!! 
    user_type = models.CharField(max_length=1, choices=USER_TYPE)

    movieset = SetTextField(base_field=IntegerField())
    ratings = JSONField(default=dict)

    average =  models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    class Meta:
        unique_together = ("user_id","user_type",)

    def values(self, c=True):
        values = list(self.ratings.values())
        if c:
            return cc.carray(values)
        return values
    def get_mean(self):
        return round(cc.mean(self.values()), 3)
    
    def set_mean(self):
        self.average = self.get_mean()
        self.save()

    def stdev(self):
        return cc.stdev(self.values())

    def commons(self, other):
        return self.movieset.intersection(other.movieset)
    
    def target_users(self, movie_id, minimum_shared=12, bring=500):
        movie = MovieArchive.objects.get(movie_id=int(movie_id))
        dummyset = set(cbs.random_sample(movie.dummyset, 8000))
        real_userset = set(cbs.random_sample(movie.userset, 8000))

        userset = dummyset.union(real_userset)
        usersets = UserArchive.objects.filter(user_id__in=userset).defer("ratings")
        target_user_dict = {}
        for user in usersets:
            if len(self.commons(user)) > minimum_shared:
                neigbour_and_shared = target_user_dict.update({ user : len(self.commons(user)) })
        return cbs.sort_dict(target_user_dict)[:bring]

    def neighbours(self, target_users_list,minimum_similarity=0.25, bring=25):
        neigbours_dict = {}
        ubar = self.get_mean()
        for user_tuple in target_users_list:
            user = user_tuple[0]
            common_movies = list(self.commons(user))
            uvalues =  cc.carray([v for k,v in self.ratings.items() if int(k) in common_movies])
            vvalues =  cc.carray([v for k,v in user.ratings.items() if int(k) in common_movies])

            vbar = user.get_mean()
            similarity = cc.pearson(uvalues, vvalues, ubar, vbar)
            if similarity==0:
                continue
            if similarity >minimum_similarity:
                neigbours_dict.update({ user:similarity })
        print("Number of neighbours:{}".format(len(neigbours_dict.values())))
        return cbs.sort_dict(neigbours_dict)[:bring]

            

    def prediction(self, movie_id, final="mean"):
        target_users = self.target_users(movie_id)
        neighbours = self.neighbours(target_users)
        v_ratings = []
        v_bars = []
        v_sims = []
        v_stdevs = []
        if final=="mean":
            for n in neighbours:
                user = n[0]
                v_ratings.append(user.ratings.get(str(movie_id)))
                v_bars.append(user.get_mean())
                v_sims.append(n[1])
            
            m_score = cc.mean_score(cc.carray(v_ratings),
                    cc.carray(v_bars), cc.carray(v_sims))

            result = self.get_mean() + m_score
            return result

        elif final.startswith("z"):
            for n in neighbours:
                user = n[0]
                v_ratings.append(user.ratings.get(str(movie_id)))
                v_bars.append(user.get_mean())
                v_sims.append(n[1])
                v_stdevs.append(user.stdev())
            
            z_score = cc.z_score(cc.carray(v_ratings),cc.carray(v_bars),
                    cc.carray(v_sims), cc.carray(v_stdevs))

            result = self.get_mean() + self.stdev() * z_score
            return result


    def post_prediction(self, movie_id):
        result = self.prediction(movie_id)
        print(f"mean 1: {result}")
        final_result = float()

        #if unsense result, try z-score normalization
        if result>4.9 or result<=0.6:
            z_result =  self.prediction(movie_id, final="z")
            print(f"z 1: {result}")

            if z_result>4.9 or z_result<=0.6:
                return 0
            else:
                final_result = round(z_result,1)
        else:
            final_result = round(result,1)
        
        #fine tuning
        if final_result>4.6:
            return final_result - 0.3
        elif final_result>4.4 and final_result<=4.6:
            return final_result - 0.2
        elif final_result>4.2 and final_result<=4.4:
            return final_result - 0.1
        else:
            return final_result


class MovSim(Model):
    base=  models.ForeignKey(Movie, related_name='base', on_delete=models.DO_NOTHING)
    target=  models.ForeignKey(Movie, related_name='target', on_delete=models.DO_NOTHING)
    users = models.IntegerField()
    pearson= models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True)
    acs= models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True)

    class Meta:
        unique_together = ("base","target",)

    def __str__(self):
        bn = self.base.name
        tn = self.target.name
        return "{}---{}".format(bn, tn)



"""
u1 = UserArchive.objects.filter(user_id=10, user_type="d")[0]
tu = u1.target_users(1, bring=50)

n1 = tu[1][0]
n = u1.neighbours(tu)


u2 = UserArchive.objects.filter(user_id=14, user_type="d")[0]
ts = MovieArchive.objects.get(id=1)


cbs = Profile.objects.get(id=1)
cua = cbs.archive

cua.post_prediction()
mmax = MovieArchive.objects.get(movie_id=122882)
"""