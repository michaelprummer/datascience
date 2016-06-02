##################################################################
#                                                                #
#                         IMPORTS                                #
#                                                                #
##################################################################

from __future__ import print_function
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn import metrics
from sklearn.cluster import KMeans, MiniBatchKMeans

from time import time
from preprocessing import Preprocessing



class Clustering():
    
    def __init__(self, tweets_path, special_files=None, limit=None):
        self.path = tweets_path
        self.special_files = special_files
        self.limit = limit
        
        self.preprocessing = Preprocessing()
    
    def apply_clustering(self):
        terms = ""
               
        t0 = time()
        data = self.preprocessing.read_with_numpy(self.path, self.special_files, self.limit)
        print("Number of loaded Tweets: " + str(len(data)) + " - loaded and preprocessed in %0.3fs" % (time()-t0))
        
        training_matrix, terms = self.useTfidfVectorizer(data)
               
        number_of_clusters = 10
        km = KMeans(n_clusters=number_of_clusters, init='k-means++', max_iter=100, n_init=1,
                    verbose=False)
        
        print("Clustering sparse data with %s" % km, end=" - ")
        t0 = time()
        km.fit(training_matrix)
        print("done in %0.3fs" % (time() - t0))
        print()
        
        print("Top terms per cluster:")
        order_centroids = km.cluster_centers_.argsort()[:, ::-1]
        
        if terms:
            for i in range(number_of_clusters):
                print("Cluster %d:" % i, end='')
                for ind in order_centroids[i, :10]:
                    print(' %s' % terms[ind], end='')
                print()
    
    def useTfidfVectorizer(self, data):
        print()
        print("Extracting features from the training dataset using a sparse vectorizer", end=" - ")
        t0 = time()
        vectorizer = TfidfVectorizer(max_df=0.5, max_features=10000,
                                     min_df=2, stop_words='english',norm='l2',
                                     use_idf=True)
        matrix = vectorizer.fit_transform(data)
        
        print("done in %0.3fs" % (time() - t0))
        print("n_samples: %0.3d, n_features: %d" % matrix.shape)
        print()
        terms = vectorizer.get_feature_names()
        
        return matrix, terms
    
    def useTfidfTransformer(self, data):
        print()
        print("Extracting features from the training dataset using a sparse vectorizer", end=" - ")
        t0 = time()
        # include counter to generate count matrix
        count_matrix = CountVectorizer(stop_words='english').fit_transform(data)
        vectorizer = TfidfTransformer(norm='l2', use_idf=True, smooth_idf=True, sublinear_tf=False)
        matrix = vectorizer.fit_transform(count_matrix)
        
        print("done in %0.3fs" % (time() - t0))
        print("n_samples: %d, n_features: %d" % matrix.shape)
        print()
        
        return matrix
    
    def useHashingVectorizer(self, data):
        print()
        print("Extracting features from the training dataset using a sparse vectorizer", end=" - ")
        t0 = time()
        vectorizer = HashingVectorizer(n_features=10000, non_negative=True, norm='l2', stop_words='english')
        matrix = vectorizer.fit_transform(data)
        
        print("done in %0.3fs" % (time() - t0))
        print("n_samples: %d, n_features: %d" % matrix.shape)
        print()
        
        return matrix
