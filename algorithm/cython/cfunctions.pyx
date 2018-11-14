from collections import Counter, defaultdict
from libc.math cimport pow, sqrt, fabs, floor



def average(dict votes):
    cdef dict allVotes = votes
    cdef unsigned int length = len(allVotes)
    cdef double value,result, sum = 0.0
    if length==0:
        print("Average Error: length=0")
        return 0
    for value in votes.values():
        sum += value
    return sum /length


def getKeySetS(dict votes):
    cdef dict allVotes = votes
    cdef set keys = set()
    if len(allVotes)==0:
        return keys
    cdef str key
    for key in votes.keys():
        keys.add(key)
    return keys

def MovieVoters(set s1, set s2):
    cdef set s3
    s3 = s1.intersection(s2)
    return s3




def getKeySet(dict votes):
    cdef dict allVotes = votes
    cdef set keys = set()
    if len(allVotes)==0:
        return keys
    cdef int key
    for key in votes.keys():
        keys.add(key)
    return keys

def getValueSet(dict votes):
    cdef dict allVotes = votes
    cdef set vals = set()
    if len(allVotes)==0:
        return vals
    cdef unsigned  short val
    for val in votes.values():
        vals.add(val)
    return vals

def intersection(dict v1, dict v2):
    cdef set s1, s2, s3, s4 = set()
    s1 = getKeySet(v1)
    s2 = getKeySet(v2)
    if s1 and s2:
        s3 = s1.intersection(s2)
        return s3
    else:
        return



cdef double calculate(double top, double bl, double br):
    cdef double result
    result = top / pow(bl*br, 0.5)
    return result

cdef double amplification( double korelasyon):
    cdef double alpha, change, finalWeight
    change = (0.6 - korelasyon)
    alpha = 1 - (change/2.0)
    finalWeight = pow(korelasyon, alpha)
    return finalWeight

def pearson(dict v1, dict v2):
    cdef set inters
    cdef int movid
    cdef double ubar, vbar, u, v, result
    cdef double top=0.0, bl= 0.0, br=0.0
    inters = intersection(v1, v2)
    ubar = average(v1)
    vbar = average(v2)
    if inters:
        for movid in inters:
            u = v1.get(movid)
            v = v2.get(movid)
            top += (u-ubar)*(v-vbar)
            bl += pow(u-ubar, 2)
            br += pow(v-vbar, 2)
        if bl==0 or br==0:
            print("bl or br is zero")
            return 0.0
        else:
            result = calculate(top, bl, br)
            return result
    else:
        print("No common items")
        return 0

def predict(list PQList, double ubar):
    cdef list PQ = PQList
    cdef tuple element
    cdef str dummyid
    cdef double vbar, rate, corr, result
    cdef double top = 0.0, sigmaCorr = 0.0
    for element in PQ:
        vbar = element[0]
        corr = amplification(element[1])
        rate = element[2]
        top += corr*(rate - vbar)
        sigmaCorr += fabs(corr)
        dbg += 1
        print(dbg)
    if sigmaCorr == 0.0:
        print("Correlation sum is zero")
        return 0
    result = ubar + (top/sigmaCorr)
    print(result)
    return result
