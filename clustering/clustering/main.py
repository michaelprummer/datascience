from __future__ import print_function

from time import time
from clustering import Clustering
from frequencies import Frequencies
from preprocessing import Preprocessing
from geo_locations import Geo

"""
ToDo:
- get IDs of tweets corresponding to one cluster
"""

def main():
    
    path = "C:/data/"
    limit = 10 # None
    special_files=["20151103.csv"]
    number_of_clusters = 3
    begin = time()
    
#     from scipy.sparse import csr_matrix, coo_matrix
#     B = [[1, 2, 0], [0, 0, 3], [4, 0, 5]]
#     A = csr_matrix([[1, 2, 0], [0, 0, 3], [4, 0, 5]])
#     for row in A:
#         print(row)
#     print(A.toarray())

    #print(coo_matrix(B))

    #startFreq(path, special_files, limit)
    startClustering(number_of_clusters, path, special_files, limit)
    #startCountrySpecificClustering(number_of_clusters, path, special_files, limit)
    
    print("Whole programm needed %0.3fs" % (time() - begin))

def startFreq(path, special_files, limit):
    freq = Frequencies(path, special_files, limit)
    freq.countFreq()

def startCountrySpecificClustering(number_of_clusters, path, special_files, limit):
    geo = Geo()
    tweet_texts, country_map = geo.getGeoTweets(path, special_files, limit)
    
    cl = Clustering(number_of_clusters)
    
    for country in country_map.keys():
        country_specific_tweets = []
        country = "United Kingdom"
        relevant_tweet_ids = country_map[country]
        print("Relevant tweets for " + country + ": " + str(len(relevant_tweet_ids)))
        
        for relevant_tweet_id in relevant_tweet_ids:
            country_specific_tweets.append(tweet_texts[relevant_tweet_id])
        
        print("Clustering for " + country, end = " - ")
        t0 = time()
        cl.apply(country_specific_tweets)
        print("done in %0.3fs" % (time() - t0))
        print()
        cl.topic_modeling(country_specific_tweets)
        print()
        exit()

def startClustering(number_of_clusters, path, special_files, limit):
    pp = Preprocessing()
    data = pp.read_with_numpy(path, special_files, limit)
    
    cl = Clustering(number_of_clusters)
    #cl.apply(data)
    cl.topic_modeling(data) 


if __name__ == "__main__":
    main()
