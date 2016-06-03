import codecs, os
from multiprocessing import Process, Manager, Lock

def run(threadID, num_threads, _split_tweets, _temp_tweets, values):
    i = threadID
    temp_tweets = _temp_tweets
    result = []
    threshold = 0.8
    tweets = _split_tweets
    deleted_duplicates = 0

    chunk = len(tweets) / num_threads
    start_i = int(chunk * i)
    end_i = int((chunk * (i + 1)) - 1)
    # print(str(start_i) + " / " + str(end_i))

    for i in range(start_i, end_i):
        if i < len(tweets):
            tweet1 = tweets[i]
            isDup = False
            for j in range(i + 1, len(tweets)):
                if j < len(tweets):
                    tweet2 = tweets[j]
                    sim = computeJaccard(set(tweet1), set(tweet2))

                    if sim > threshold:
                        del tweets[j]
                        if isDup == False:
                            result.append(temp_tweets[i])

                        isDup = True
                        deleted_duplicates += 1
                        print("P-" + str(threadID) + ": %.1f " % (((i - start_i) / (end_i - start_i) * 100)) + "%")
                else:
                    break

        else:
            break

        if isDup == False:
            result.append(temp_tweets[i])

    print("###### Id-" + str(i) + ", Tweets: " + str(len(result)) + " Duplicates: " + str(
                deleted_duplicates) + " ######")

    values[1] = deleted_duplicates
    values[0] = result


def computeJaccard(set1, set2):
    x = len(set1.intersection(set2))
    y = len(set1.union(set2))
    return x / float(y)

if __name__ == '__main__':
    lock = Lock()
    input_path = "E:/data/"
    output_path = "E:/out/"
    num_threads = 32
    files_in_folder = os.listdir(input_path + "/")
    splited_tweets = []
    temp_tweets = []

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

        processes = []
        m = Manager()
        values = []
        for i in range(num_threads):
            values.append(
                m.list([[""], 0])
           )

        for i in range(num_threads):
            p = Process(target=run, args=(i, num_threads, splited_tweets, temp_tweets, values[i]))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

    sum = 0
    for val in values:
        sum += val[1]
        for line in val[0]:
            out.write(line)
    log.write("Deleted-Tweets: " + str(sum) + "\n")
