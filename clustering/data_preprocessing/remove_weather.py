import json,codecs, re, os
import gzip
from timeit import timeit

class Weather():
    def __init__(self,input_path,out_path):
        self.input_path = input_path
        self.output_path = out_path
        self.tweets = []
        self.threshold = 0.08

        files_in_folder = os.listdir(self.input_path + "/")


        for file in files_in_folder:
            log = codecs.open(self.output_path + "log.txt", "a", "utf-8")
            out = codecs.open(self.output_path + file, "w", "utf-8")
            deleted=0
            try:
                with codecs.open(self.input_path + "/" + file, encoding='utf-8') as infile:
                    for line in infile:
                        values = line.split("\t")
                        tweet = values[3].lower()

                        self.tweets.append(tweet.split())

                        count=0
                        if "weather" in tweet:
                            count+=1
                        if "temperature" in tweet:
                            count+=1
                        if "wind" in tweet:
                            count+=1
                        if "barometer" in tweet:
                            count+=1
                        if "humidity" in tweet:
                            count+=1
                        if "rain" in tweet:
                            count+=1

                        if count < 2:
                            out.write(line)
                        else:
                            deleted+=1
            except:
                continue

            self.detectDuplicates()
            log.write("Deleted Tweets in " + file + ": " + str(deleted) + "\n")


    def detectDuplicates(self):
        for i in range(0, len(self.tweets) - 1):
            tweet1 = self.tweets[i]

            for j in range(i + 1, len(self.tweets)):
                tweet2 = self.tweets[j]
                sim = self.computeJaccard(set(tweet1), set(tweet2))

                if sim > self.threshold:
                    print("Dublikat")

    def computeJaccard(self, set1, set2):
        x = len(set1.intersection(set2))
        y = len(set1.union(set2))
        return x / float(y)


if __name__ == '__main__':
    input_path = "C:/data/"
    output_path = "C:/out/"
    weather = Weather(input_path, output_path)