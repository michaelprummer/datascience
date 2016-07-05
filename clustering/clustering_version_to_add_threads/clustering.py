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
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import k_means, KMeans, MiniBatchKMeans, DBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from scipy.sparse import coo_matrix, csr_matrix
from time import time
import codecs
import numpy

class Clustering():
    
    def __init__(self, results=False):
       
        self.results = results
                    
    def extractFeatures(self, data, tf=False):
                
        tfidf_training_matrix, tfidf_terms = self.useTfidfVectorizer(data)
        
        if tf:
            tf_vectorizer = CountVectorizer(max_df=0.5, min_df=2, max_features=10000,
                                        stop_words='english')
        
            tf_training_matrix = tf_vectorizer.fit_transform(data)
            tf_terms = tf_vectorizer.get_feature_names()
                
            return tfidf_training_matrix, tfidf_terms, tf_training_matrix, tf_terms
        
        else:
            return tfidf_training_matrix, tfidf_terms
        
    def applyNMF(self, number_of_clusters, country_specific_tweets):
        train, feature_names = self.extractFeatures(country_specific_tweets,False)
        name = "nmf"
        
        # Fit the NMF model
        if self.results:
            print("Fitting the NMF model", end=" - ")
        
        t0 = time()
        nmf = NMF(n_components=number_of_clusters, random_state=1, alpha=.1, l1_ratio=.5).fit(train)
        
        if self.results:
            print("done in %0.3fs." % (time() - t0))
        
        if self.results:
            print("\nNMF:")
        
        parameters = nmf.get_params()
        
        if self.results:
            print("Parameter: " + str(parameters))
        topics = nmf.components_
        doc_topic = nmf.transform(train)
        top10, labels = self.printLDACluster(topics, doc_topic, feature_names)
        labels = numpy.asarray(labels)
        
        if self.results:
            print("Silhouette Coefficient {0}: {1}".format(name, metrics.silhouette_score(train, labels)))
                   
        
        return name, parameters, top10, labels
             
    
    def applyLDA2(self, number_of_clusters, country_specific_tweets):
        train, feature_names = self.extractFeatures(country_specific_tweets,False)
        
        name = "lda"
        if self.results:
            print("Fitting LDA model with tfidf", end= " - ")
        t0 = time()     
        lda = LatentDirichletAllocation(n_topics=number_of_clusters, max_iter=5,
                                        learning_method='online', learning_offset=50.,
                                        random_state=0)

        lda.fit(train)
        
        if self.results:
            print("done in %0.3fs." % (time() - t0))
        
        parameters = lda.get_params()
        topics = lda.components_
        doc_topic = lda.transform(train)
        top10, labels = self.printLDACluster(topics, doc_topic, feature_names)
        labels = numpy.asarray(labels)
        
        if self.results:
            print("Silhouette Coefficient {0}: {1}".format(name, metrics.silhouette_score(train, labels)))
        
        
        return name, parameters, top10, labels


    def applyKmeansMiniBatch(self, number_of_clusters, country_specific_tweets):
        train, feature_names = self.extractFeatures(country_specific_tweets,False)
        
        name = "kmeans"
        if self.results:
            print("Performing dimensionality reduction using LSA")
        t0 = time()
        
        # Vectorizer results are normalized, which makes KMeans behave as
        # spherical k-means for better results. Since LSA/SVD results are
        # not normalized, we have to redo the normalization.
        
        #svd = TruncatedSVD(len(feature_names)-1)
        #normalizer = Normalizer(copy=False)
        #lsa = make_pipeline(svd, normalizer)
        #print(train.toarray())
        #train = lsa.fit_transform(train)
        
        if self.results:
            print("done in %fs" % (time() - t0))
    
        # explained_variance = svd.explained_variance_ratio_.sum()
        #print("Explained variance of the SVD step: {}%".format(int(explained_variance * 100)))
    
        #print()
        if self.results:
            print("Clustering sparse data", end=" - ")                 
        t0 = time()
        
        km = MiniBatchKMeans(n_clusters=number_of_clusters, init='k-means++',init_size=1000,batch_size=1000, verbose=False)

        km.fit(train)
        if self.results:
            print("done in %0.3fs" % (time() - t0))

        parameters = km.get_params()
        labels = km.labels_
        # without SVD:
        order_centroids = km.cluster_centers_.argsort()[:, ::-1]
        
        # using SVD:
        #original_space_centroids = svd.inverse_transform(km.cluster_centers_)
        #order_centroids = original_space_centroids.argsort()[:, ::-1]
        top10 = self.printKMeansCluster(number_of_clusters, labels, order_centroids, feature_names)
        
        if self.results:
            print("Silhouette Coefficient {0}: {1}".format(name, metrics.silhouette_score(train, labels)))
        
        return name, parameters, top10, labels
    
    def printKMeansCluster(self, number_of_clusters, clusters, order_centroids, terms=None):

        cluster_counter = dict()
        for cluster in clusters:
            try:
                cluster_counter[cluster] += 1
            except KeyError:
                cluster_counter[cluster] = 1
        
        if self.results:
            for cluster in cluster_counter:
                print("Cluster " + str(cluster) + " contains " + str(cluster_counter[cluster]) + " tweets")
            print()
        
        top10 = dict()           
        if terms:
            for i in range(number_of_clusters):
                if self.results:
                    print("Cluster %d:" % i, end='')
                tmp = []
                for ind in order_centroids[i, :10]:
                    if self.results:
                        print(' %s' % terms[ind].encode("utf-8"), end='')
                    tmp.append(terms[ind])
                top10[i] = tmp
                if self.results:
                    print()
        
        return top10
    
    def printLDACluster(self, topics, doc_topic, feature_names):
        top10 = dict()
        clusters = []
        doc_counter = dict()
        for doc in doc_topic:
            
            cluster = doc.argmax()
            clusters.append(cluster)
            try:
                doc_counter[cluster] += 1
            except KeyError:
                doc_counter[cluster] = 1
        
        if self.results:
            for cluster in doc_counter:
                print("Cluster " + str(cluster) + " contains " + str(doc_counter[cluster]) + " tweets")
        
        for nr, topic in enumerate(topics):
            if self.results:
                print("Topic #%d: " %nr, end=" ")
                print(" ".join([feature_names[i].encode("utf-8") for i in topic.argsort()[:-10-1:-1]]))
            top10[nr] = [feature_names[i] for i in topic.argsort()[:-10-1:-1]]
        
        if self.results:
            print()
        
        return top10, clusters
    
    def useTfidfVectorizer(self, data):
        if self.results:
            print()
            print("Extracting features from the training dataset using a sparse vectorizer", end=" - ")
        t0 = time()
    
        vectorizer = TfidfVectorizer(max_features=10000, stop_words='english',norm='l2',use_idf=True, sublinear_tf=False,encoding='utf-8')
        matrix = vectorizer.fit_transform(data)
        
        if self.results:
            print("done in %0.3fs" % (time() - t0))
            print("n_samples: %0.3d, n_features: %d" % matrix.shape)
            print()
        
        feature_names = vectorizer.get_feature_names()
        return matrix, feature_names
    
    
    def useTfidfTransformer(self, data):
        if self.results:
            print()
            print("Extracting features from the training dataset using a sparse vectorizer", end=" - ")
        t0 = time()
        # include counter to generate count matrix
        count_vectorizer = CountVectorizer(stop_words='english')
        count_matrix = count_vectorizer.fit_transform(data)
        vectorizer = TfidfTransformer(norm='l2', use_idf=True, smooth_idf=True, sublinear_tf=False)
        matrix = vectorizer.fit_transform(count_matrix)
        if self.results:
            print("done in %0.3fs" % (time() - t0))
            print("n_samples: %d, n_features: %d" % matrix.shape)
            print()
        
        feature_names = count_vectorizer.get_feature_names()
        
        return matrix, feature_names
    

            
