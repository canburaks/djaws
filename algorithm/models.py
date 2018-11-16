from django.db import models
import os, sys, inspect
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"cython")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import cfunctions as c


from django.core.cache import cache

average = c.average
getKeySet = c.getKeySet
getKeySetS = c.getKeySetS
getValueSet = c.getValueSet
intersection = c.intersection
pearson = c.pearson
predict = c.predict
voterSet = c.MovieVoters



# Create your models here.



class Dummy():
    Votes = cache




    @classmethod
    def mean(cls,id):
        return c.average(cls.Votes.get(str(id)))




    @classmethod
    def greatDict(cls, movid):
        "Bring users that rated target movie and their all votes"
        import random
        from items.models import Movie
        userList = Movie.objects.get(id=movid).ratings_dummy
        num_of_user_list = len(userList)
        if (num_of_user_list>10000) and (num_of_user_list<20000):
            userList = random.sample(userList, num_of_user_list//2)

        elif (num_of_user_list>20000) and (num_of_user_list<40000):
            userList = random.sample(userList, num_of_user_list//4)

        elif (num_of_user_list>40000):
            userList = random.sample(userList,num_of_user_list//8)

        dic = {key:cls.Votes.get(key) for key in userList}
        "{'key': {2571:4.0}, ... }"
        return dic


    @classmethod
    def prediction(cls, profile, target):
        movid = target.id

        profileVotes = {int(key): value for key,value in profile.ratings.items()}
        "{ '2571': 4, '1' : 3.5, ...}" # to {2571 : 4, 1:}
        profileMean = c.average(profileVotes)
        greatDict = cls.greatDict(movid)
        "{'157000': {2571:4.0}, ... }"

        lowerLimit = 15 #len(profileVotes)//2
        #middleLimit = 10
        commons = dict()
        for d in greatDict.keys():
            interectionQuantity = len(intersection(profileVotes, greatDict.get(d)))
            if interectionQuantity >= lowerLimit:
                commons.update({d:interectionQuantity})
        #if len(commons)<50:
        #    for d in greatDict.keys():
        #        interectionQuantity = len(intersection(profileVotes, greatDict.get(d)))
        #        if interectionQuantity > middleLimit:
        #            commons.update({d:interectionQuantity})

        NQ= sorted(commons.items(), key=lambda x:x[1], reverse=True)[:100]
        "[ ('157000', 5)....]"
        print("{} number of Neighbours brought".format(len(NQ)))

        PQ = []
        for n in NQ:
            dummyId = n[0] # "157000"
            dummyVotes = greatDict.get(dummyId)
            vbar = cls.mean(dummyId)
            corr = c.pearson(profileVotes, dummyVotes)
            rate = dummyVotes.get(target.id)
            if corr>0.2 and rate:
                PQ.append(( vbar, corr, rate ))
        PQsorted = sorted(PQ, key=lambda x: x[1], reverse=True)[:20]
        print("Number of correlated Neigbours:{}".format(len(PQ)))
        if len(PQ)<4:
            return 0

        pred = predict(PQsorted, profileMean)
        greatDict = {}
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



"""
def opening():
    import _pickle as pickle
    import bz2
    with bz2.BZ2File("static/pickles/newdummies.pbz2","r") as f:
        p = pickle.load(f)
    for d in p.keys():
        cache.set(d,p.get(d),None)
    print("\n Dummies added\n")
opening()


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
