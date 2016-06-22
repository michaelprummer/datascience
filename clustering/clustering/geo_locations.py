from __future__ import print_function
import numpy
from time import time
from preprocessing import Preprocessing
import re, codecs
from clustering import Clustering

class Geo():
    def __init__(self):
        self.pp = Preprocessing()
    
    def getGeoTweets(self, path, special_files, limit):
        tweet_texts, country_data = self.loadGeoData(path, special_files, limit)
        country_map = self.country_mapping(country_data)
    
        return tweet_texts, country_map
    
           
    def loadGeoData(self, path, special_files, limit=None):
        
        counter = 0
        places = list()
        if special_files:
            files = special_files
        else:
            files = os.listdir(path)
            
        for file in files:
            print("Loading data from " + file, end=" - ")
            t0 = time()
            tweet_texts = numpy.loadtxt(path + file, dtype='str', delimiter="\t", usecols = [6], comments=None)
            country_names = numpy.loadtxt(path + file, dtype='str', delimiter="\t", usecols = [4], comments=None)
            
            print("done in %0.3fs" % (time() - t0))
            
            print("Preprocessing tweet texts", end=" - ")
            t0 = time()
            
            if not len(country_names) == len(tweet_texts):
                
                print("ERROR in length of loaded data!")
                exit()
                
            for i in range(len(tweet_texts)):
                counter+=1
                tweet = self.pp.preprocess_tweet(tweet_texts[i])
                tweet_texts[i] = tweet
                
                if limit and counter >= limit:
                    print("done in %0.3fs" % (time() - t0))
                    print()
                    return tweet_texts[:limit], country_names[:limit]
                
            print("done in %0.3fs" % (time() - t0))
            print()
            
        return tweet_texts, country_names
    
    def country_mapping(self, country_data):
        country_map = {}
        for i in range(len(country_data)):
            country = country_data[i]
            if country in country_map.keys():
                tmp = country_map[country]
                tmp.append(i)
                country_map[country] = tmp
            else:
                country_map[country] = [i]
        
        return country_map

        
            
            
            
        
        
    

if __name__ == "__main__":
    path = "C:/geo_data/"
    limit = None # None
    special_files=["20151021.csv"]
    number_of_clusters = 3
    country = "United States" # None
    geo_processing = Geo()
    geo_processing.loadGeoData(path, special_files, limit)