import codecs, os, time
from multiprocessing import Process, Manager, Lock
from multiprocessing.sharedctypes import Value

def run(threadID, num_threads, splited_tweets, temp_tweets, values, p_progress):
    i = threadID
    result = []
    threshold = 0.8
    deleted_duplicates = 0

    chunk = len(splited_tweets) / num_threads
    start_i = int(chunk * i)
    end_i = int((chunk * (i + 1)) - 1)

    thresholdLines = 1200

    #print(str(start_i) + " / " + str(end_i))

    for i in range(start_i, end_i):
        linesToGo = thresholdLines
        if i < len(splited_tweets):
            isDup = False
            for j in range(i + 1, len(splited_tweets)):
                if j < len(splited_tweets) and linesToGo > 0:
                    sim = computeJaccard(set(splited_tweets[i]), set(splited_tweets[j]))

                    if sim > threshold:
                        if isDup == False:
                            result.append(temp_tweets[i])
                            isDup = True
                            #print("1: " + temp_tweets[i])
                            #print("2: " + temp_tweets[j])

                        del splited_tweets[j]
                        del temp_tweets[j]
                        deleted_duplicates += 1
                        #print("P-{:d}: {:.2%}".format(threadID, (i - start_i) / float(end_i - start_i)))
                else:
                    break
                linesToGo -= 1

        else:
            break

        if not isDup:
            result.append(temp_tweets[i])

    p_progress.value += 1
    print("PID-{0}, Tweets: {1} Duplicates: {2} ({3}/{4})".format(threadID, len(result), deleted_duplicates, p_progress.value, num_threads))

    values[1] = deleted_duplicates
    values[0] = result


def computeJaccard(set1, set2):
    return len(set1.intersection(set2)) / float(len(set1.union(set2)))

if __name__ == '__main__':
    lock = Lock()
    input_path = "data/"
    output_path = "out/"
    num_threads = 10
    files_in_folder = os.listdir(input_path + "/")
    deleted_tweets_all = 0

    for file in files_in_folder:
        log = codecs.open(output_path + "log.txt", "a", "utf-8")
        out = codecs.open(output_path + file, "w", "utf-8")

        p_shared_vals = []
        p_progress = Value('i', 0)
        temp_tweets = []
        splited_tweets = []
        t1 = time.time()
        processes = []
        m = Manager()



        with codecs.open(input_path + "/" + file, encoding='utf-8') as infile:
            for line in infile:
                values = line.split("\t")

                if len(values) > 3:
                    tweet = values[3]
                    splited_tweets.append(tweet.split())
                    temp_tweets.append(line)


        for i in range(num_threads):
            p_shared_vals.append(
                m.list([[""], 0])
           )

        #shared_data = m.list(temp_tweets)
        print("Starting with {0} Tweets.".format(len(temp_tweets)))
        for i in range(num_threads):
            #p = Process(target=run, args=(i, num_threads, splited_tweets, shared_data, p_shared_vals[i], p_progress))
            p = Process(target=run, args=(i, num_threads, splited_tweets, temp_tweets, p_shared_vals[i], p_progress))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        t2 = time.time()

        sum = 0
        for val in p_shared_vals:
            sum += val[1]
            for line in val[0]:
                out.write(line)

        end_time = "%.1f" % ((t2-t1)/60)

        log.write("Deleted-Tweets: {0}\n".format(sum))
        log.write("time: {0}\n".format(end_time))
        print("file finished: {0}, removed: {1}, time: {2}min".format(file, sum, end_time))
        deleted_tweets_all += sum

    log.write("Final: {0}\n".format(deleted_tweets_all))