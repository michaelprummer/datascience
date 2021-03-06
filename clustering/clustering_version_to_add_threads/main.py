from __future__ import print_function
import time
from time import time
from time import sleep
from clustering import Clustering
from frequencies import Frequencies
from multiprocessing import Process, Manager, Lock
from multiprocessing.sharedctypes import Value
from geo_locations import Geo
import os, numpy, re, codecs
from sklearn import metrics

"""
Distribute country processing on different threads by creating so called jobs for them.
"""

def job(job_data, number_of_clusters, shared_val):
    #print("JOB DATA: " + str(len(job_data)))

    nmfData = []
    ldaData = []
    kmeansData = []

    for j in job_data:
        country = j[0]
        country_specific_tweets = j[1]
        relevant_tweet_ids = j[2]
        cl = j[3]

        #print("Clustering for " + country + " (" + str(len(relevant_tweet_ids)) + " Tweets)")
        #t0 = time()

        # NMF
        name, parameters, top10, clusters = cl.applyNMF(number_of_clusters, country_specific_tweets)
        nmfData.append([name, country, top10, clusters, relevant_tweet_ids])

        # LDA tfidf
        name, parameters, top10, clusters = cl.applyLDA2(number_of_clusters, country_specific_tweets)
        ldaData.append([name, country, top10, clusters, relevant_tweet_ids])

        # Kmeans++
        name, parameters, top10, clusters = cl.applyKmeansMiniBatch(number_of_clusters, country_specific_tweets)
        kmeansData.append([name, country, top10, clusters, relevant_tweet_ids])

        #print(country + " done in %0.3fs" % (time() - t0))

    shared_val[0] = nmfData
    shared_val[1] = ldaData
    shared_val[2] = kmeansData



class MainProgram():
    """
    For each country in a country map (key: country, value: tweets of this country) 
    clustering is started here and finally results are printed.
    Each loaded file contains tweets from all over the world for one day in 2015.
    File format: tweet_id, date, geo_location, tweet_text, country_code, city_code.
    """
    def __init__(self, path="data/", special_files=None, limit=None, number_of_clusters=10,out_path="/", threshold=100):
        
        # All files in path will be loaded. 
        # Otherwise you should specificy the file name you want to load from this path.
        self.path = path
        self.special_files = special_files
        
        # define if you only want to cluster a specific number of tweets.
        self.limit = limit
        
        # define number of clusters.
        self.number_of_clusters = number_of_clusters
                
        # country needs specific number of tweets to be able to do clustering.
        self.threshold = threshold
        
        # each cluster gets unique id
        self.cluster_ID = 146649
        
        # open output files.
        self.out_path = out_path
        self.cluster_out_file = codecs.open(self.out_path + "_cluster_terms.txt", "w", "utf-8")
        self.tweet_counter = 0
        self.file_counter = 1
        self.id_out_file = codecs.open(self.out_path + "ids_" + str(self.file_counter) + ".txt", "w", "utf-8")
        
        self.startProcess()

    def startProcess(self):
        """
        For each files clustering will be started.
        """
        
        if self.special_files:
            files = self.special_files
        else:
            files = os.listdir(self.path)
            
        for file in files:
            self.startCountrySpecificClustering(file)

        self.cluster_out_file.close()
        self.id_out_file.close()
          
    def startFreq(self, file):
        """
        Get term frequencies (Top 100) for definition of corpus specific stopwords.
        """
        freq = Frequencies(self.path + file, self.limit)
        freq.countFreq()
    
    def startCountrySpecificClustering(self, file):
        """
        Load tweets of one file and then process country per country.
        """
        geo = Geo()
        data, country_map = geo.getGeoTweets(self.path + file, self.limit)

        if not sum([len(country_map[country]) for country in country_map]) == len(data):
            print(sum([len(country_map[country]) for country in country_map]))
            print(len(data))
            
            print("ERROR in length of loaded data!")
            exit()
        
        # load clustering object; decide if results are printed on stdout (top terms and how many tweets are in one cluster).
        cl = Clustering(results=False)

        # Processes
        processes = []
        jobs = []
        countryJobs = []
        p_shared_vals = []
        m = Manager()

        for country in country_map.keys():
            country_specific_tweets = []
            relevant_tweet_ids = country_map[country]
                      
            for relevant_tweet_id in relevant_tweet_ids:
                country_specific_tweets.append(data[relevant_tweet_id][2])
            
            if len(relevant_tweet_ids) > self.threshold:
                countryJobs.append([country, country_specific_tweets, relevant_tweet_ids, cl])

        numOfProcesses = min(30, len(countryJobs))
        #numOfProcesses = 8

        print("NumOfProcesses: " + str(numOfProcesses) + ", country jobs: " + str(len(countryJobs)))

        for k, job_data in enumerate(countryJobs, 0):
            index = k % numOfProcesses
            if not len(jobs) > index:
                jobs.append([job_data])
            else:
                jobs[index].append(job_data)

        for i, j in enumerate(jobs, 0):
            p_shared_vals.append(
                m.list([
                    [],
                    [],
                    []
                ])
            )

            p = Process(target=job, args=([j, self.number_of_clusters, p_shared_vals[i]]))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        #name, parameters, top10, clusters
        for sharedObj in p_shared_vals:
            nmfList = sharedObj[0]
            ldaList = sharedObj[1]
            kmeansList = sharedObj[2]

            for nmf in nmfList:
                self.printResults(nmf[0], nmf[1], nmf[2], nmf[3], nmf[4], data, file)

            for lda in ldaList:
                self.printResults(lda[0], lda[1], lda[2], lda[3], lda[4], data, file)

            for kmeans in kmeansList:
                self.printResults(kmeans[0], kmeans[1], kmeans[2], kmeans[3], kmeans[4], data, file)


    def printResults(self, name, country, top10, clusters, relevant_tweet_ids, data, filename):
        """
        write two output files: cluster_terms and ids.
        """
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
                self.cluster_ID += 1
            
            # write file with top terms: cluster_id, algorithm_name, terms, date, country
            date = filename[:-4]
            for top in top10.keys():
                self.cluster_out_file.write(str(clusterID_mapping[top]) + "\t" + name + "\t" + " ".join(
                    top10[top]) + "\t" + date + "\t" + country + "\n")

            # write file with cluster-tweet mapping: tweet_id, nmf_cluster_id, lda_cluster_id, kmeans_cluster_id, latitude, longitude, tweet text
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
                self.tweet_counter+= 1
            
        # Avoiding that id output file gets to big.
        if self.tweet_counter > 1000000:
            self.tweet_counter = 0
            self.id_out_file.close()
            self.file_counter += 1
            self.id_out_file = codecs.open(self.out_path + "ids_" + str(self.file_counter) + ".txt", "w", "utf-8")
        



if __name__ == "__main__":
    begin = time()
    path = "data/"
    limit = None # limit number of tweets per loaded file.
    special_files = None #["20151126.csv"]
    number_of_clusters = 20
    output_path = "out/"

    threshold = 100 # country must have enough tweets for clustering
    
    main = MainProgram(path, special_files, limit, number_of_clusters, output_path, threshold)
    
    print("Whole program needed %0.3fs" % (time() - begin))

