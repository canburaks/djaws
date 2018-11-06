from django.db import models
from django.core.cache import cache
import os, sys, inspect
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"cython")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)


import cfunctions as c

average = c.average
getKeySet = c.getKeySet
getKeySetS = c.getKeySetS
getValueSet = c.getValueSet
intersection = c.intersection
pearson = c.pearson
predict = c.predict
voterSet = c.MovieVoters


# Create your models here.



class Dummy(models.Model):
    Votes = cache
    KeySet = set()
    id = models.IntegerField(primary_key=True)

    @classmethod
    def mean(cls,id):
        return c.average(cls.Votes.get(str(id)))

    @classmethod
    def keys(cls, id):
        "Returns set objects"
        return c.getKeySet(cls.Votes.get(str(id)))


    @classmethod
    def greatDict(cls, movid):
        "Bring users that rated target movie and their all votes"
        from items.models import Movie
        userList = Movie.objects.get(id=movid).ratings_dummy
        #dic = {key:cls.Votes.get(key) for key in userList if cls.Votes.get(key)}
        dic = {key:cls.Votes.get(key) for key in userList}
        "{'key': {2571:4.0}, ... }"
        return dic


    @classmethod
    def prediction(cls, profile, target):
        movid = target.id

        profileVotes = profile.ratings["movie"]
        "{ 2571: 4, 1:3.5, ...}"
        profileMean = c.average(profileVotes)
        greatDict = cls.greatDict(movid)
        "{'157000': {2571:4.0}, ... }"

        lowerLimit = 15 #len(profileVotes)//2
        #middleLimit = 10
        commons = dict()
        for d in greatDict.keys():
            interectionQuantity = len(intersection(profileVotes, greatDict.get(d)))
            if interectionQuantity > lowerLimit:
                commons.update({d:interectionQuantity})
        #if len(commons)<50:
        #    for d in greatDict.keys():
        #        interectionQuantity = len(intersection(profileVotes, greatDict.get(d)))
        #        if interectionQuantity > middleLimit:
        #            commons.update({d:interectionQuantity})

        NQ= sorted(commons.items(), key=lambda x:x[1], reverse=True)[:200]
        "[ ('157000', 5)....]"
        print("{} number of Neighbours brought".format(len(NQ)))

        PQ = []
        for n in NQ:
            dummyId = n[0] # "157000"
            dummyVotes = greatDict.get(dummyId)
            vbar = cls.mean(dummyId)
            corr = c.pearson(profileVotes, dummyVotes)
            rate = dummyVotes.get(target.id)
            if corr>0.2:
                PQ.append(( vbar, corr, rate ))
        PQsorted = sorted(PQ, key=lambda x: x[1], reverse=True)[:10]
        print("Number of correlated Neigbours:{}".format(len(PQ)))

        pred = predict(PQsorted, profileMean)
        if pred>5:
            pred = 4.87

        greatDict = {}
        return pred

def opening():
    import _pickle as pickle

    with open("static/pickles/KeySet.pickle","rb") as f:
        p = pickle.load(f)
        Dummy.KeySet = p.copy()
opening()


"""
def opening():
    import _pickle as pickle

    with open("static/sixtyP4.pickle","rb") as f:
        p = pickle.load(f)
        Dummy.Votes.update(p)
opening()


MODEL_BUCKET = os.environ['MODEL_BUCKET']
MODEL_FILENAME = os.environ['MODEL_FILENAME']
MODEL = None
def load_model():
    import _pickle as pickle
    from google.cloud import storage
    global MODEL
    client = storage.Client()
    bucket = client.get_bucket(MODEL_BUCKET)
    blob = bucket.get_blob(MODEL_FILENAME)
    s = blob.download_as_string()

    MODEL = pickle.loads(s)
    Dummy.Votes.update(MODEL)

load_model()

def opening():
    import _pickle as pickle
    import bz2
    with bz2.BZ2File("static/Midi.pbz2","r") as f:
        p = pickle.load(f)
        Dummy.Votes.update(p)
opening()

def getVotes():
    import gcsfs
    import _pickle as pickle
    import bz2
    fs = gcsfs.GCSFileSystem(project='discovery-214900', token="cloud")
    with fs.open('discoverystatic/static/shelve/pickle.pbz2') as f:
        with bz2.BZ2File(f) as pb:
            p = pickle.load(pb)
            Dummy.Votes.update(p)
getVotes()


TOKEN = os.environ['MODEL_BUCKET']


with open("/home/cbs/Documents/Pickle/Big.pickle","rb") as f:
    Dummy.Votes = pickle.load(f)

MODEL_BUCKET = os.environ['MODEL_BUCKET']
MODEL_FILENAME = os.environ['MODEL_FILENAME']

def load_model():
    import _pickle as pickle
    from google.cloud import storage
    client = storage.Client()
    bucket = client.get_bucket(MODEL_BUCKET)
    blob = bucket.get_blob(MODEL_FILENAME)
    s = blob.download_as_string()

    Dummy.Votes = pickle.loads(s)

load_model()
"""
