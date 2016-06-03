import codecs, os,sys, time
import threading
import time

class ReDuplicates(threading.Thread):
    def __init__(self, input_path, out_path, threadID, threadName, maxThreads, split_tweets, tmp_tweets):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName
        self.num_threads = maxThreads
        self.input_path = input_path
        self.output_path = out_path

        #Duplicates
        self.threshold = 0.8
        self.tweets = split_tweets
        self.temp_tweets = tmp_tweets
        self.collect = []
        self.deleted_duplicates = 0

    def run(self):
        #print("Starting " + self.threadName)
        self.detectDuplicates(self.threadID)
        print("###### FINISHED " + self.threadName + " / Tweets: " + str(len(self.collect)) + " ######")



    #range(0, len(self.tweets) - 1)
    def detectDuplicates(self, i):
        chunk = len(self.tweets) / self.num_threads
        start_i = int(chunk * i)
        end_i = int((chunk * (i + 1)) - 1)

        #print(str(start_i) + " / " + str(end_i))

        for i in range(start_i, end_i):
            if i < len(self.tweets):
                tweet1 = self.tweets[i]
                isDup = False
                for j in range(i + 1, len(self.tweets)):
                    if j < len(self.tweets):
                        tweet2 = self.tweets[j]
                        sim = self.computeJaccard(set(tweet1), set(tweet2))

                        if sim > self.threshold:
                            del self.tweets[j]
                            if isDup == False:
                                self.collect.append(self.temp_tweets[i])

                            isDup = True
                            self.deleted_duplicates += 1
                            print("Thread-" + str(self.threadID) + ": %.5f " % (   (i-start_i) / (end_i-start_i)   ))
                    else:
                        break

            else:
                break

            if isDup == False:
                self.collect.append(self.temp_tweets[i])

    def computeJaccard(self, set1, set2):
        x = len(set1.intersection(set2))
        y = len(set1.union(set2))
        return x / float(y)

if __name__ == '__main__':
    input_path = "E:/data/"
    output_path = "E:/out/"
    num_threads = 16
    files_in_folder = os.listdir(input_path + "/")
    splited_tweets = []
    temp_tweets = []

    join_arr = [None]*num_threads

    for file in files_in_folder:
        log = codecs.open(output_path + "log.txt", "a", "utf-8")
        out = codecs.open(output_path + file, "w", "utf-8")

        with codecs.open(input_path + "/" + file, encoding='utf-8') as infile:
            for line in infile:
                values = line.split("\t")

                if len(values) > 3:
                    tweet = values[3]
                    splited_tweets.append(tweet.split())
                    temp_tweets.append(line)


        threads = []
        for i in range(num_threads):
            threads.append(ReDuplicates(input_path, output_path, i, "Thread-" + str(i), num_threads, splited_tweets, temp_tweets))
            threads[i].start()

        for i in range(num_threads):
            threads[i].join()

        print("Finished: " + str(len(join_arr)))
        sum = 0
        for t in threads:
            sum += t.deleted_duplicates
            for line in t.collect:
                out.write(line)
        log.write("Deleted-Tweets: " + str(sum) + "\n")