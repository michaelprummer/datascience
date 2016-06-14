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

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation

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
                
        print("********* NMF with LDA ****************")
        
        def print_top_words(model, feature_names, n_top_words):
            for topic_idx, topic in enumerate(model.components_):
                print("Topic #%d:" % topic_idx)
                print(" ".join([feature_names[i]
                                for i in topic.argsort()[:-n_top_words - 1:-1]]))
            print()
        
        n_samples = 200000
        n_features = 100000
        n_topics = 3
        n_top_words = 6
        

        # Use tf-idf features for NMF.
        print("Extracting tf-idf features for NMF...")
        tfidf_vectorizer = TfidfVectorizer(max_df=0.5, min_df=2, max_features=n_features,
                                           stop_words='english',
                                           norm='l2',
                                           ngram_range=(1,3),
                                           use_idf=True)
        t0 = time()
        tfidf = tfidf_vectorizer.fit_transform(data)
        print("done in %0.3fs." % (time() - t0))
        
        # Use tf (raw term count) features for LDA.
        print("Extracting tf features for LDA...")
        tf_vectorizer = CountVectorizer(max_df=0.5, min_df=2, max_features=n_features,
                                        stop_words='english')
        t0 = time()
        tf = tf_vectorizer.fit_transform(data)
        print("done in %0.3fs." % (time() - t0))
        
        # Fit the NMF model
        print("Fitting the NMF model with tf-idf features,"
              "n_samples=%d and n_features=%d..."
              % (n_samples, n_features))
        t0 = time()
        nmf = NMF(n_components=n_topics, random_state=1, alpha=.1, l1_ratio=.5).fit(tfidf)
        print("done in %0.3fs." % (time() - t0))
        
        print("\nTopics in NMF model:")
        tfidf_feature_names = tfidf_vectorizer.get_feature_names()
        print_top_words(nmf, tfidf_feature_names, n_top_words)
        
        print("Fitting LDA models with tf features, n_samples=%d and n_features=%d..."
              % (n_samples, n_features))
        lda = LatentDirichletAllocation(n_topics=n_topics, max_iter=5,
                                        learning_method='online', learning_offset=50.,
                                        random_state=0)
        t0 = time()
        lda.fit(tf)
        print("done in %0.3fs." % (time() - t0))
        
        print("\nTopics in LDA model:")
        tf_feature_names = tf_vectorizer.get_feature_names()
        print_top_words(lda, tf_feature_names, n_top_words)
        
    
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
