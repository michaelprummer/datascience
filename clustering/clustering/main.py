from time import time

from clustering import Clustering
from frequencies import Frequencies

def main():
    
    path = "C:/data/"
    limit = 1000000 # None
    special_files=["20151021.csv"]
    
    begin = time()
    
    #startFreq(path, special_files, limit)
    startClustering(path, special_files, limit)
    
    print("Whole programm needed %0.3fs" % (time() - begin))

def startFreq(path, special_files, limit):
    freq = Frequencies(path, special_files, limit)
    freq.countFreq()

def startClustering(path, special_files, limit):
    cl = Clustering(path, special_files, limit)
    cl.apply_clustering()


if __name__ == "__main__":
    main()
