from __future__ import print_function
import numpy
from time import time
from preprocessing import Preprocessing
from multiprocessing import Process, Manager, Lock
from multiprocessing.sharedctypes import Value
import re, codecs
from clustering import Clustering

class Geo():
    def __init__(self):
        self.pp = Preprocessing()
    
    def getGeoTweets(self, path, limit):

        data = self.loadGeoData(path, limit)
        
        country_map = self.country_mapping(data)
    
        return data, country_map
    
           
    def loadGeoData(self, path, limit=None):
        
        counter = 0
        
        print("Loading data from " + path, end=" - ")
        t0 = time()
        
        data = numpy.loadtxt(path, dtype='str', delimiter="\t", usecols = [2,5,3,3,0], comments=None)
        print("done in %0.3fs" % (time() - t0))

        print("Preprocessing tweet texts", end=" - ")
        t0 = time()
                    
        for i in range(len(data)):
            
            counter+=1
            tweet = self.pp.preprocess_tweet(data[i][2])
            data[i][2] = tweet
                
            if limit and counter >= limit:
                print("done in %0.3fs" % (time() - t0))
                print()

                return data[:limit]
            
        print("done in %0.3fs" % (time() - t0))
        print()

        return data
    
    def country_mapping(self, data):
        country_map = {}
        for i in range(len(data)):
            country = data[i][1]
            if country in country_map.keys():
                tmp = country_map[country]
                tmp.append(i)
                country_map[country] = tmp
            else:
                country_map[country] = [i]
        
        return country_map