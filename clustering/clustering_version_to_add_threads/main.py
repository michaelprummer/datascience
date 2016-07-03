from __future__ import print_function

from time import time
from clustering import Clustering
from frequencies import Frequencies
from preprocessing import Preprocessing
from geo_locations import Geo
import os, numpy, re, codecs
from sklearn import metrics

class MainProgram():
    
    def __init__(self, path="data/", special_files=None, limit=None, number_of_clusters=10,out_path="/", threshold=100):
        self.path = path
        self.special_files = special_files
        self.limit = limit
        self.number_of_clusters = number_of_clusters
        self.out_path = out_path
        self.threshold = threshold
        self.cluster_ID = 0
        
        self.cluster_out_file = codecs.open(self.out_path + "cluster_terms.txt", "w", "utf-8")
        self.id_out_file = codecs.open(self.out_path + "ids.txt", "w", "utf-8")
        
        self.startProcess()           

    def startProcess(self):    
        
        if self.special_files:
            files = self.special_files
        else:
            files = os.listdir(self.path)
            
        for file in files:

            self.startCountrySpecificClustering(file)
        
        self.cluster_out_file.close()
        self.id_out_file.close()
          
    def startFreq(self, file):
        freq = Frequencies(self.path + file, self.limit)
        freq.countFreq()
    
    def startCountrySpecificClustering(self, file):
        geo = Geo()
        data, country_map = geo.getGeoTweets(self.path + file, self.limit)

        if not sum([len(country_map[country]) for country in country_map]) == len(data):
            print(sum([len(country_map[country]) for country in country_map]))
            print(len(data))
            
            print("ERROR in length of loaded data!")
            exit()
        
        # decide if results are printed on stdout (top terms and how many tweets are in one cluster).
        cl = Clustering(results=False)
        
        for country in country_map.keys():
            country_specific_tweets = []
            
            relevant_tweet_ids = country_map[country]
            #self.info_out.write(country + "\t" + str(len(relevant_tweets_ids)) + "\n")
            
            
            for relevant_tweet_id in relevant_tweet_ids:
                country_specific_tweets.append(data[relevant_tweet_id][2])
            
            if len(relevant_tweet_ids) > self.threshold:
                                   
                print("Clustering for " + country + " (" + str(len(relevant_tweet_ids)) + " Tweets)")
                t0 = time()
                print()
                                
                # NMF
                name, parameters, top10, clusters = cl.applyNMF(self.number_of_clusters, country_specific_tweets)    
                self.printResults(name, country, top10, clusters, relevant_tweet_ids, data, file)

                # LDA tfidf
                name, parameters, top10, clusters = cl.applyLDA2(self.number_of_clusters, country_specific_tweets)
                self.printResults(name, country, top10, clusters, relevant_tweet_ids, data, file)
  
                # Kmeans++
                name, parameters, top10, clusters = cl.applyKmeans_plus(self.number_of_clusters, country_specific_tweets)
                self.printResults(name, country, top10, clusters, relevant_tweet_ids, data, file)
                
                print()
                print("done in %0.3fs" % (time() - t0))
            
            
                
    def printResults(self, name, country, top10, clusters, relevant_tweet_ids, data, filename):
        nmf = str(-1)
        lda = str(-1)
        kmeans = str(-1)
        
        if len(clusters) != len(relevant_tweet_ids):
            print("Geclusterte Tweets:" + str(len(clusters)))
            print("Gesuchte Tweets:" + str(len(relevant_tweet_ids)))                    
            print("ERROR: Clustered Tweets not equal to read tweets")
        else:
            clusterID_mapping = dict()
            for i in range(self.number_of_clusters):
                clusterID_mapping[i] = self.cluster_ID
                self.cluster_ID+=1
            
            
            # write file with top terms: cluster_id    term    datum    land
            date = filename[:-4]
            for top in top10.keys():
                self.cluster_out_file.write(str(clusterID_mapping[top]) + "\t" + name + "\t" + " ".join(top10[top]) + "\t" + date + "\t" + country + "\n")
            
            # write file with cluster-tweet mapping: cluster_id    latitude    longitude    tweet text           
            for i in range(len(relevant_tweet_ids)):
                tweet_id = relevant_tweet_ids[i]    
                geo1, geo2 = tuple((data[tweet_id][0]).split(","))
                tweet_text = data[tweet_id][3].decode("utf-8")
                id = data[tweet_id][4]
                clusterID = str(clusterID_mapping[clusters[i]])
                if name == "nmf":
                    nmf = clusterID
                elif name == "lda":
                    lda = clusterID
                elif name == "kmeans":
                    kmeans = clusterID
                else:
                    print("ERROR cluster name")
                    exit()
                    
                self.id_out_file.write(id + "\t")
                self.id_out_file.write(nmf + "\t")
                self.id_out_file.write(lda + "\t")
                self.id_out_file.write(kmeans + "\t")
                self.id_out_file.write(geo1 + "\t")
                self.id_out_file.write(geo2 + "\t")
                self.id_out_file.write(tweet_text + "\n")



              

if __name__ == "__main__":
    begin = time()

    path = "C:/Users/Jennifer/Documents/data/ab_sept/"
    limit = None
    special_files = None #["20151126.csv"]
    number_of_clusters = 3
    output_path="C:/test/"
        
    threshold = 100 # country must have enough tweets for clustering
    
    main = MainProgram(path,special_files, limit, number_of_clusters, output_path, threshold)
    
    print("Whole programm needed %0.3fs" % (time() - begin))

