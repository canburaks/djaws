import requests
key = "64fdf8453969abf3a5df3c2eac6c367f"
baseUrl = "https://image.tmdb.org/t/p/w185"# + "poster_path"

class Movie:
    key = "64fdf8453969abf3a5df3c2eac6c367f"
    poster_base_url = "https://image.tmdb.org/t/p/w185"# + "poster_path"

    def __init__(self, tmdb_id):
        self.tmdb_id = tmdb_id
    
    def details(self):
        """
        ==> {}
        keys:[  homepage, imdb_id, original_title, overview,poster_path
                production_companies:[{}, {}..], production_companies:[{}..]
                release_date, title, runtime    ]
        """
        url = "https://api.themoviedb.org/3/movie/{}?api_key={}".format(self.tmdb_id, Movie.key)
        istek = requests.get(url)
        response = istek.json()
        return response

    def credits(self):
        """
        cast==>    [{cast_id:34, "name":"Keanu Reeves", "character":"Thomas Anderson",
                "tmdb_id":6384, "profile_path": "/jhjhbbjb.jpg"  }]
        crew==>    ["department":"Directing", ,id:4762, "job":"Director", "name": "PTA", "profile_path":"/sda.jpg]
        """
        key = "64fdf8453969abf3a5df3c2eac6c367f"
        url = "https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(self.tmdb_id, Movie.key )
        istek = requests.get(url)
        response = istek.json()
        cast, crew = response.get("cast"), response.get("crew")
        if crew:
            crew = [x for x in crew if x.get("job")=="Director" if x.get("job")=="Screenplay" if x.get("job")=="Director of Photography"]
        return cast, crew

    def external_ids(self):
        """
        Return Dictionary ==> {id, twitter_id, facebook_id, instagram_id, imdb_id}
        """
        key = "64fdf8453969abf3a5df3c2eac6c367f"
        url = "https://api.themoviedb.org/3/tv/{}/external_ids?api_key={}".format(self.tmdb_id, Movie.key )
        istek = requests.get(url)
        response = istek.json()
        return response


class Person:
    key = "64fdf8453969abf3a5df3c2eac6c367f"
    poster_base_url = "https://image.tmdb.org/t/p/w185"# + "poster_path"

    def __init__(self, tmdb_id):
        self.tmdb_id = tmdb_id
    
    @property
    def details_url(self):
        key = "64fdf8453969abf3a5df3c2eac6c367f"
        return "https://api.themoviedb.org/3/person/{}?api_key={}".format(self.tmdb_id, key)

    @property
    def external_url(self):
        key = "64fdf8453969abf3a5df3c2eac6c367f"
        return "https://api.themoviedb.org/3/person/{}/external_ids?api_key={}".format(self.tmdb_id, key )
    
    @property
    def complex_url(self):
        key = "64fdf8453969abf3a5df3c2eac6c367f"
        return "https://api.themoviedb.org/3/person/{}?api_key={}&append_to_response=external_ids".format(self.tmdb_id, key)

    def details(self):
        """
        ==> {}
        keys:[  homepage, imdb_id, original_title, overview,poster_path
                production_companies:[{}, {}..], production_companies:[{}..]
                release_date, title, runtime    ]
        """
        url = "https://api.themoviedb.org/3/person/{}?api_key={}".format(self.tmdb_id, Person.key)
        istek = requests.get(url)
        response = istek.json()
        return response

    def credits(self):
        """
        cast==>    [{cast_id:34, "name":"Keanu Reeves", "character":"Thomas Anderson",
                "tmdb_id":6384, "profile_path": "/jhjhbbjb.jpg", original_title  }]
        crew==>    ["department":"Directing", ,id:4762, "job":"Director", "name": "PTA", "profile_path":"/sda.jpg]
        """
        key = "64fdf8453969abf3a5df3c2eac6c367f"
        url = "https://api.themoviedb.org/3/person/{}/credits?api_key={}".format(self.tmdb_id, Person.key )
        istek = requests.get(url)
        response = istek.json()
        cast, crew = response.get("cast"), response.get("crew")
        return cast, crew

    def external_ids(self):
        """
        Return Dictionary ==> {id, twitter_id, facebook_id, instagram_id, imdb_id}
        """
        key = "64fdf8453969abf3a5df3c2eac6c367f"
        url = "https://api.themoviedb.org/3/person/{}/external_ids?api_key={}".format(self.tmdb_id, Person.key )
        istek = requests.get(url)
        response = istek.json()
        return response


class Tv:
    key = "64fdf8453969abf3a5df3c2eac6c367f"
    poster_base_url = "https://image.tmdb.org/t/p/w185"# + "poster_path"

    def __init__(self, tmdb_id):
        self.tmdb_id = tmdb_id
    
    def details(self):
        """
        ==> {}
        keys:[  homepage, imdb_id, original_title, overview,poster_path
                production_companies:[{}, {}..], production_companies:[{}..]
                release_date, title, runtime    ]
        """
        url = "https://api.themoviedb.org/3/tv/{}?api_key={}".format(self.tmdb_id, Tv.key)
        istek = requests.get(url)
        response = istek.json()
        return response

    def external_ids(self):
        """
        Return Dictionary ==> {id, twitter_id, facebook_id, instagram_id, imdb_id}
        """
        key = "64fdf8453969abf3a5df3c2eac6c367f"
        url = "https://api.themoviedb.org/3/tv/{}/external_ids?api_key={}".format(self.tmdb_id, Tv.key )
        istek = requests.get(url)
        response = istek.json()
        return response

    def season_details(self,season_number):
        """
        ==> { air_date, name, overview, poster_path, 
                episodes: [episode_number, id, overview, 
                        crew:[ id, name, department, job, profile_path],
                        guest_stars:[ id, name, department, job, profile_path],
                    [ep2], [ep3]]
            }
        """
        key = "64fdf8453969abf3a5df3c2eac6c367f"
        url = "https://api.themoviedb.org/3/tv/1418/season/{}?api_key={}".format(self.tmdb_id, season_number, key)
        istek = requests.get(url)
        response = istek.json()

    def episode_details(self, season_number, episode_number):
        #Episode has 
        """
        ==> { air_date, name, overview, id:(?), season_number, 
                crew:[
                    {id,name, deparment, job, profile_path},{},{}...],
                guest_stars:[
                    { same as crew,.. },{},{},...]
            }
        """
        key = "64fdf8453969abf3a5df3c2eac6c367f"
        url = "https://api.themoviedb.org/3/tv/{}/season/{}/episode/{}?api_key={}".format(self.tmdb_id, season_number, episode_number, key)
        istek = requests.get(url)
        response = istek.json()



    def episode_external_ids(self, season_number, episode_number):
        """
        Return Dictionary ==> {id, twitter_id, facebook_id, instagram_id, imdb_id}
        """
        key = "64fdf8453969abf3a5df3c2eac6c367f"
        url = ("https://api.themoviedb.org/3/tv/{}/season/{}/episode/{}/external_ids?api_key={}").format(self.tmdb_id, season_number, episode_number, key )
        istek = requests.get(url)
        response = istek.json()
        return response

    def credits(self):
        """
        cast==>    [{cast_id:34, "name":"Keanu Reeves", "character":"Thomas Anderson",
                "tmdb_id":6384, "profile_path": "/jhjhbbjb.jpg"  }]
        crew==>    ["department":"Directing", ,id:4762, "job":"Director", "name": "PTA", "profile_path":"/sda.jpg]
        """
        key = "64fdf8453969abf3a5df3c2eac6c367f"
        url = "https://api.themoviedb.org/3/tv/{}/credits?api_key={}".format(self.tmdb_id, Tv.key )
        istek = requests.get(url)
        response = istek.json()
        cast, crew = response["cast"], response["crew"]
        return cast, crew

    @classmethod
    def populars(cls, page):
        """
        ==>[{},{}...]
            keys:[original_name, name, popularity, first_air_date, backdrop_path, id, overview,
            poster_path ]
        """
        key = "64fdf8453969abf3a5df3c2eac6c367f"
        url = "https://api.themoviedb.org/3/tv/popular?api_key={}&page={}".format(cls.key, page)
        istek = requests.get(url)
        response = istek.json()
        return response["results"]


######################################################################

"""
# ASYNC REQUESTS
import _pickle as pickle
import aiohttp

file_tmdb = "/home/jb/Documents/Database/tmdb_person.pickle"
#tmdb_person_dict = {}
with open(file_tmdb, "rb") as f:
    tmdb_person_dict = pickle.load(f)

person_tmdb_id_list = list(tmdb_person_dict.keys())

import asyncio
#loop = asyncio.get_event_loop()
import time

async def get_details(dic, start, stop):
    start_time = time.time()

    id_list = list(dic.keys())[start:stop]
    sample_dict = {x:dic.get(x) for x in id_list}

    async with aiohttp.ClientSession() as session:
        for tmdb_id in id_list:
            tperson = Person(tmdb_id)
            async with session.get(tperson.details_url) as resp:
                print(resp.status)
                print(await resp.text())
    print(time.time() - start_time)

asyncio.run(get_details(tmdb_person_dict, 0,20))

#####################################################################3
#SYNC REQUEST
import time

def sget_details(dic, start, stop):
    start_time = time.time()

    id_list = list(dic.keys())[start:stop]
    sample_dict = {x:dic.get(x) for x in id_list}

    for tmdb_id in id_list:
        tperson = Person(tmdb_id)
        print(tperson.details())
    print(time.time() - start_time)

sget_details(tmdb_person_dict, 0,20)
"""