import _pickle as pickle
from tqdm import tqdm
db_folder = "/home/jb/Projects/AWS/database/"
movie_id_list = db_folder + "movie_id_list" #only movie ids
movie_dummy_file = db_folder + "movie_dummy_dict.pickle"# {1:[dummy_id158...], 2:[dummy_id158, dummy_id1....]}
movie_movie_corr_file = db_folder + "movie_movie_corr.pickle" # { 1:{3:0.89,..}...}
corr_dataframe  = db_folder + "corr_df.pickle"
refined_ratings = db_folder + "refined_ratings.csv"
redis_like_ratings = db_folder + "refined_ratings.pickle"
person_file = db_folder + "person.pickle"
crew_dict = db_folder + "crew.pickle"

def get_pickle(file_directory):
    import _pickle as pickle
    with open(file_directory, "rb") as f:
        r = pickle.load(f)
    return r

def save_pickle(file_directory, file):
    import _pickle as pickle
    with open(file_directory, "wb") as f:
        pickle.dump(file, f)
    print("saved")

p = get_pickle(person_file)
plist = [x for x in p.keys()]
len(plist)
pset = set(plist)
len(pset)


registered_ids = [x[0] for x in  Person.objects.all().values_list("id")]
len(registered_ids)
rset = set(registered_ids)
len(rset)

def will_create(plist, registered_ids):
    new_list = plist
    for i in registered_ids:
        if i in plist:
            new_list.remove(i)
    return new_list

def imdb_based():
    new_imdb_dic = {}
    for val in p.values():
        new_imdb_dic.update({val.get("id"): val})
    return new_imdb_dic


def bulk_person(new_list, start, stop):

    bulk_objects = []
    
    for new_pid in tqdm(new_list[start:stop]):
        new_person_dict = p.get(new_pid)
        new_person = Person(**new_person_dict)
        bulk_objects.append(new_person)
    print("Person number before:{}".format(Person.objects.all().count()))
    print("Number of bulk peron before create:{}".format(len(bulk_objects)))
    Person.objects.bulk_create(bulk_objects)
    print("After create of person: Total Person is: {}".format(Person.objects.all().count()))

def bb(start):
    for i in range(20):
        s = start + i*5000
        st = s + 5000
        if s < 105000:
            bulk_person(np ,s, st )
        else:
            print("done")

##############################################33
import _pickle as pickle
from tqdm import tqdm
db_folder = "/home/jb/Projects/AWS/database/"
movie_id_list = db_folder + "movie_id_list" #only movie ids
movie_dummy_file = db_folder + "movie_dummy_dict.pickle"# {1:[dummy_id158...], 2:[dummy_id158, dummy_id1....]}
movie_movie_corr_file = db_folder + "movie_movie_corr.pickle" # { 1:{3:0.89,..}...}
corr_dataframe  = db_folder + "corr_df.pickle"
refined_ratings = db_folder + "refined_ratings.csv"
redis_like_ratings = db_folder + "refined_ratings.pickle"
person_file = db_folder + "person.pickle"
crew_dict = db_folder + "crew.pickle"

def get_pickle(file_directory):
    import _pickle as pickle
    with open(file_directory, "rb") as f:
        r = pickle.load(f)
    return r

def save_pickle(file_directory, file):
    import _pickle as pickle
    with open(file_directory, "wb") as f:
        pickle.dump(file, f)
    print("saved")

# Crew ops
cr = get_pickle(crew_dict)
cr_movie_id_list = [x for x in cr.keys()]


valid_tmdb_ids = [x.get("tmdb_id") for x in  Person.objects.all().values("id", "tmdb_id")]


def create_crew2(start, stop):
    from tqdm import tqdm
    cr = get_pickle(crew_dict)
    cr_movie_id_list = [x for x in cr.keys()][start : stop]
    crew_bulk = []
    valid_tmdb_ids = [x.get("tmdb_id") for x in  Person.objects.all().values("id", "tmdb_id")]

    qs = Movie.objects.filter(id__in=cr_movie_id_list).defer("data","ratings_dummy", "year", "summary","poster")
    qs_persons = Person.objects.all().defer("data","bio", "job","poster")

    for movie in tqdm(qs):
        movie_crews = cr.get(movie.id)

        for c in movie_crews:
            if c.get("tmdb_id") in valid_tmdb_ids:
                person = qs_persons.get(tmdb_id=c.get("tmdb_id"))
                job = c.get("job")
                character= c.get("character")
                data = {"department" : c.get("department")}
                if character:
                    crew_bulk.append(
                        Crew(movie=movie, person=person, job=job, character=character, data=data)
                    )
                else:
                    crew_bulk.append(
                        Crew(movie=movie, person=person, job=job, data=data)
                    )
    print("before bulk create num of crew:{}".format(Crew.objects.all().count()))
    Crew.objects.bulk_create(crew_bulk)
    print("after bulk create num of crew:{}".format(Crew.objects.all().count()))

def auto_create(start, batch_size, stop):

    rrr = (stop - start)//batch_size
    for i in range(rrr):
        strt = start + i*batch_size
        stp = strt + batch_size
        create_crew2(strt, stp)
        print("{} added to db".format(batch_size))
        print("\n")

################################################################3

