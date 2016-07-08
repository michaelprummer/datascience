from __future__ import print_function
import numpy
from time import time
from preprocessing import Preprocessing
import re, codecs
from clustering import Clustering

class Geo():
    """
    Loads data, loads preprocessing and does country mapping.
    """
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
        empty_row = []      
        for i in range(len(data)):
            
            counter+=1
            
            tweet = self.pp.preprocess_tweet(data[i][2])
            data[i][2] = tweet
            if tweet == "":
                empty_row.append(i)
            if limit and counter >= limit:
                if len(empty_row) > 1:
                    empty_row.sort(reverse=True)
                for id in empty_row:
                    data = numpy.delete(data, (id), axis=0)
                print("done in %0.3fs" % (time() - t0))
                print()

                return data[:limit]
            
        print("done in %0.3fs" % (time() - t0))
        print()
        if len(empty_row) > 1:
            empty_row.sort(reverse=True)

        for id in empty_row:
            data = numpy.delete(data, (id), axis=0)
        return data
    
    def country_mapping(self, data):
        """
        Mapping: country (key) - corresponding tweet ids (value list).
        """
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