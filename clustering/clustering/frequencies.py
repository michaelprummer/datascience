##################################################################
#                                                                #
#                         IMPORTS                                #
#                                                                #
##################################################################

from __future__ import print_function
import codecs, re, csv, unicodecsv
from time import time
from tokenizer import MyTokenizer
from preprocessing import Preprocessing

class Frequencies():
    def __init__(self, tweets_path, special_files, limit):
        self.path = tweets_path
        self.special_files = special_files
        self.limit = limit
        
        self.preprocessing = Preprocessing()
    
    def countFreq(self):
        t0 = time()
        data = self.preprocessing.read_with_numpy(self.path, self.special_files, self.limit)
        print("Number of loaded Tweets: " + str(len(data)) + " - loaded and preprocessed in %0.3fs" % (time()-t0))
        print()
        
        print("Count frequencies", end=": ")
        t0 = time()
        # Use a dictionary to keep track of the frequency of tokens.
        token_counter = {}
          
        # Get a line/tweet from the corpus.
        for line in data:
 
            # Split the text on whitespace to get a list of words.
            for word in line.split():
 
                # Counting with a dictionary the EAFP way.
                # Try to add one to value of a key in the dictionary.
                try: 
                    token_counter[word] += 1
 
                # If the dictionary raises a KeyError,
                # add the key to the dictionary and set its value to 1.
                except KeyError:
                    token_counter[word] = 1
 
        # Sort the dictionary by frequency.
        frequency_list = sorted(token_counter.iteritems(), key=lambda x: x[1],
                reverse=True)
     
        # Print the 100 most frequent tokens.
#         print("Most frequent tokens (top 100):")
#         index = 1
#         for pair in frequency_list[:100]:
#             print(str(index).ljust(2), pair[0].ljust(20), str(pair[1]))
#             index += 1
     
        # Print the 100 least frequent tokens.
        print("\nLeast common tokens (top 100):")
        index = 1
        for pair in frequency_list[-10000:]:
            if pair[1] < 11:
                print(str(index).ljust(2), pair[0].ljust(20), str(pair[1]))
                index += 1
        
        print("done in %0.3fs" % (time()-t0))
        