from .models import Movie
import os, sys, inspect
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"cython")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

from django.core.cache import cache

"""

ts = Movie.objects.get(id=1)
m = Movie.objects.get(id=2571)

"""

def similarity(movie1, movie2):
    dummy_set1 = movie1.ratings_dummy
    dummy_set2 = movie2.ratings_dummy
    dummy_commons = dummy_set1.intersection(dummy_set2)
    