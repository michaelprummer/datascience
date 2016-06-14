from __future__ import print_function
import numpy
from time import time
import os, re, codecs
import countries
from timeit import timeit

class GeoPreprocessing():
    def __init__(self, input_path, output_path, special_files=None, limit=None):
        self.input_path = input_path
        self.cc = countries.CountryChecker('TM_WORLD_BORDERS-0.3.shp')
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        self.output_path = output_path
        self.not_usable_files = open(self.output_path + "tweets_without_gps.txt", "a") 
        
        self.limit = limit
        
        if special_files:
            files = special_files
        else:
            files = os.listdir(self.input_path)
        
        for file in files:
            self.getCountry(file)
        
    def loadIDs(self, file):
        counter = 0
        
        print("Loading IDs from " + file, end=" - ")
        t0 = time()
        ids = numpy.loadtxt(self.input_path + file, dtype='str', delimiter="\t", usecols = [2], comments=None)
        
        for i in range(len(ids)):
            counter+= 1
                            
            if self.limit and counter >= self.limit:
                print("done in %0.3fs" % (time() - t0))
                return ids[:self.limit]
            
        print("done in %0.3fs" % (time() - t0))
        return ids
        
    
    def loadGeoCoordinates(self, file):
        
        counter = 0
        
        print("Loading Geo locations from " + file, end=" - ")
        t0 = time()
        geo_data = numpy.loadtxt(self.input_path + file, dtype='str', delimiter="\t", usecols = [4], comments=None)
        
        for i in range(len(geo_data)):
            counter+= 1
            geo_data[i] = geo_data[i].strip("[]")
            
            if self.limit and counter >= self.limit:
                print("done in %0.3fs" % (time() - t0))
                return geo_data[:self.limit]
            
        print("done in %0.3fs" % (time() - t0))
        return geo_data
    
    def getCountry(self, filename):
        ids = self.loadIDs(filename)
        geo_data = self.loadGeoCoordinates(filename)
        
        t0 = time()
        print("Getting country for each tweet in file " + filename, end=" - ")
        if len(geo_data) != len(ids):
            print("ERROR: different length of geo data and ids")
            exit()
            
        out = open(self.output_path + filename, "w")
               
        for i in range(len(geo_data)):
            lng, lat = tuple(geo_data[i].split(","))
            lng = float(lng)
            lat = float(lat)
            
            country = self.cc.getCountry(countries.Point(lng,lat))
            
            if not country:
                self.not_usable_files.write(ids[i] + "\n")
            else:
                
                abbr = country.iso               
                out.write(ids[i] + "\t" + geo_data[i] + "\t" + str(country) + "\t" + abbr + "\n")
        
        out.close()
        print("done in %0.3fs" % (time() - t0))
        print()

def showDuration(duration):
    print()
    print("Elapsed time for saving country tagged files: {duration}s".format(file=file,duration=duration[0]))
    print()


if __name__ == "__main__":
    data_path = "C:/data/"
    output_path = "C:/data_country_tagged/"
    
    limit = None
    special_files = None
    
    duration = timeit(lambda: GeoPreprocessing(data_path, output_path, special_files, limit), number=1),             
    showDuration(duration)
