##################################################################
#                                                                #
#                         IMPORTS                                #
#                                                                #
##################################################################

from __future__ import print_function
import codecs, re, csv, unicodecsv
from info_dict import smiley_list
from time import time
from tokenizer import MyTokenizer
import pandas
import numpy
from nltk.stem import snowball
from nltk.stem import WordNetLemmatizer

class Preprocessing():
    
    def __init__(self):
        self.tok = MyTokenizer(preserve_case=True)
        self.smiley_list = smiley_list
        self.punctuation = [",", ".", "..", "?", "!"]
        self.stemmer = snowball.EnglishStemmer()
        #self.stemmer = WordNetLemmatizer() # called self.stemmer.lemmatize(string)
        print("Loading corpus")
        
    def read_as_object(self, path, special_files, limit=None):
        # we have 201 384 592 tweets
        counter = 0
        tweets = list()
        if special_files:
            files = special_files
        else:
            files = os.listdir(path)
            
        for file in files:
            print("Loading file " + file + " and preprocess", end=" - ")
            t0 = time()
            with codecs.open(path + file, "r", "utf-8") as FileObj:
                for line in FileObj:
                                    
                    line = line.strip().split("\t")
                    tweet = self.preprocess_tweet(line[3])
                    tweets.append(tweet)
                    
                    counter += 1
                    if limit and counter > limit:
                        print("done in %0.3fs" % (time() - t0))
                        print()
                        return tweets
                    
            print("done in %0.3fs" % (time() - t0))
            print()
        
        return tweets
    
    def read_with_numpy(self, path, special_files, limit=None):
        counter = 0
        tweets = list()
        if special_files:
            files = special_files
        else:
            files = os.listdir(path)
            
        for file in files:
            print("Loading file " + file, end=": ")
            t0 = time()
            data = numpy.loadtxt(path + file, dtype='str', delimiter="\t", usecols = [3])
            print("done in %0.3fs" % (time() - t0))
            
            print("Preprocessing file", end=" - ")
            t0 = time()
            for i in range(len(data)):
                counter+= 1
                tweet = self.preprocess_tweet(data[i])
                data[i] = tweet
                
                if limit and counter >= limit:
                    print("done in %0.3fs" % (time() - t0))
                    print()
                    return data[:limit]
                
            print("done in %0.3fs" % (time() - t0))
            print()
            
        return data
    
    def read_with_pandas(self, path, special_files, limit=None):
        counter = 0
        tweets = list()
        if special_files:
            files = special_files
        else:
            files = os.listdir(path)
            
        for file in files:
            print("Laoding file " + file, end=" - ")
            t0 = time()
            data = pandas.read_csv(path + file, sep="\t", encoding='utf-8',names=["date", "name", "id", "tweet", "geo", "place"])
            print("done in %0.3fs" % (time() - t0))
            print()
                    
            #data.to_csv(path + file[:-4] + "_new.csv", sep="\t", encoding='utf-8')
            
        if limit:
            return data["tweet"][:limit]
        else:
            return data["tweet"]                  

    def preprocess_tweet(self, tweet):
        
        """

        - remove tagged persons, pronouns
        - content-based: co-occurrence clusters
        - Sequences of repeated symbols or punctuation signs were reduced to one instance or a sequence
        to indicate the repetition.
        - Numbers or dates were reduced to a capital letter indicating their appearance.
        - Some symbols were forced to be preceded by a white space in order to facilitate the posterior
        splitting into words.
        - Sequences of several white spaces were reduced to one white space and all white spaces
        were converted to underscores.
        - punctuation and stopwords removal
        - what happens to don't?
        """
        tweet = tweet.decode(encoding="utf-8")
        
        tweet = self.tok.tokenize(tweet)

        for i in range(len(tweet)):
            token = tweet[i]
            
            # Handle URLs
            if re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', token):
                #tweet[i] = "<URL>"
                tweet[i] = ""
                
            # Handle user-tags
            elif token.startswith("@"):
                #tweet[i] = "<USER>"
                tweet[i] = ""
            
            # Handle hashtags
            elif token.startswith("#"):
                tweet[i] = token[1:]
            
            # Handle emoticons
            elif token in self.smiley_list:
                
                #tweet[i] = "<EMOTICON>"
                tweet[i] = ""
            
            elif token in self.punctuation:
                #tweet[i] = ""
                continue
            
            elif token == "amp":
                tweet[i] = ""
            
            else:
                tweet[i] = re.sub("[^0-9A-Za-z,.?!%:/]", "", token)           
                
                
        preprocessed_tweet = ""
        for token in tweet:
            if token:
                #preprocessed_tweet += self.stemmer.stem(token.lower()) + " "
                preprocessed_tweet += token.lower() + " "
        preprocessed_tweet = preprocessed_tweet.strip().encode("utf-8")
        
        
              
        return preprocessed_tweet
    
    def save_preprocessed_corpus(self, filename, data):
        filename = filename[:-4] + "_preprocessed_tweets" + filename[-4:]
        numpy.savetxt(filename, data, newline='\n')
        print("Saved preprocessed corpus")