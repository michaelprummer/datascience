##################################################################
#                                                                #
#                         IMPORTS                                #
#                                                                #
##################################################################

from __future__ import print_function
import codecs, re, csv
from time import time
from tokenizer import MyTokenizer
import numpy

class Preprocessing():
    
    def __init__(self):
        self.tok = MyTokenizer(preserve_case=True)
        self.personal_pronomen = ["i", "me", "we", "us", "you", "she", "her", "he", "him" ,"it","they","them","that","which","who","whom","whose","whichever","whoever","whomever", "this", "these", "that", "those", "anybody", "anyone", "anything", "each", "either", "everybody", "everyone", "everything", "neither", "nobody", "no", "one", "nothing", "one", "somebody", "someone", "something", "both", "few", "many", "several", "all", "any", "most", "none", "some", "what", "who", "which", "whom", "whose", "myself", "ourselves", "yourself", "yourselves", "himself", "herself", "itself", "themselves", "my", "your", "his", "her", "its", "our", "your", "their", "mine", "yours", "his", "hers", "ours", "yours", "theirs"]
        self.praepositionen = ["at", "on", "in", "by", "from", "to", "a", "an", "a","an","aboard","about","'bout","bout","above","bove","abreast","abroad","absent","across","cross","adjacent","after","against","'gainst","gainst","along","'long","alongside","amid","amidst","mid","midst","among","amongst","'mong","mong","'mongst","apropos","apud","around","'round","round","as","astride","at","@","atop","ontop","bar","before","afore","tofore","B4","behind","ahind","below","ablow","allow","beneath","'neath","neath","beside","besides","between","atween","beyond","ayond","but","by","chez","circa","c.","ca.","come","dehors","despite","spite","down","during","except","for","4","from","in","inside","into","less","like","minus","near","nearer","anear","notwithstanding","of","o'","off","on","onto","opposite","out","outen","outside","over","o'er","pace","past","per","post","pre","pro","qua","re","sans","save","sauf","short","since","sithence","than","through","thru","throughout","thruout","to","2","toward","towards","under","underneath","unlike","until","'til","til","till","up","upon","'pon","pon","upside","versus","vs.","v.","via","vice","vis-a-vis","with","w/c","within","w/i","without","w/o","worth"]
        self.stopwords = ["amp", "ive", "don", "when","and","why","here","now","never","sometimes","too","the","not","youre","are","have","be","been","always","never","forever","would","should","has", "ahead","aint","and","another","anymore","apart","because","best","big","can","cant","could","cum","cuz","damn","did","doesnt","done","fast","get","goes","going","got","had","hey","how","in","it","it","just","keep","last","latest","let","lets","lol","lot","makes","meant","might","more","much","nah","new","no","no","of","omg","on","once","other","our","own","please","put","same","set","set","somewhere","soo","soon","stay","still","such","sweet","tha","there","there","theres","thing","things","though","up","very","want","was","we","well","were","whats","whole","why","will","with","yes","yet","you","your","yall"]
        self.ignored_terms = set(self.personal_pronomen).union(set(self.praepositionen)).union(set(self.stopwords))
    def read_with_numpy(self, path, limit=None):
        counter = 0
        
        print("Loading tweets from " + path, end=" - ")
        t0 = time()
        tweets = numpy.loadtxt(path, dtype='str', delimiter="\t", usecols = [6],comments=None)
        
        print("done in %0.3fs" % (time() - t0))
        
        print("Preprocessing tweets", end=" - ")
        t0 = time()
        
        for i in range(len(tweets)):
            counter+= 1
            tweet = self.preprocess_tweet(tweets[i])
            tweets[i] = tweet
            #print(tweet)
            if limit and counter >= limit:
                print("done in %0.3fs" % (time() - t0))
                print()
                return tweets[:limit]
            
        print("done in %0.3fs" % (time() - t0))
        print()
        
        
        return tweets                 

    def preprocess_tweet(self, tweet):
        tweet = tweet.decode(encoding="utf-8")
        
        tweet = self.tok.tokenize(tweet)

        for i in range(len(tweet)):
            
            # Handle URLs
            if re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet[i]): 
                #tweet[i] = "<URL>"
                tweet[i] = ""
                        
            elif tweet[i].startswith("@"):
                tweet[i] = ""
            
            # Handle hashtags
            elif tweet[i].startswith("#"):
                # split on upper case: #NiceTalk -> Nice Talk
                hashtag = re.findall('[A-Z][^A-Z]*', tweet[i][1:])
                
                if len(hashtag) > 0:
                    tweet[i] = " ".join(hashtag)
                else:
                    tweet[i] = tweet[i][1:]
            
            elif tweet[i] == "i've" or tweet[i] == "don't":
                tweet[i] = ""
                
            tweet[i] = re.sub("[^A-Za-z ]", "", tweet[i])
            tweet[i] = tweet[i].lower()
            if len(tweet[i]) < 3:
                tweet[i] = "" 
            elif tweet[i] in self.ignored_terms:
                tweet[i]= ""   
            elif tweet[i].endswith("ly"):
                tweet[i] = ""

        preprocessed_tweet = ""
        for token in tweet:
            if token:
                preprocessed_tweet += token + " "
        preprocessed_tweet = preprocessed_tweet.strip().encode("utf-8")

        return preprocessed_tweet