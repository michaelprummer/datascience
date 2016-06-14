import codecs, os, time
from multiprocessing import Process, Manager, Lock
from multiprocessing.sharedctypes import Value

def run(threadID, num_threads, splited, tweets, values, p_progress, start_i, end_i):
    result = []
    threshold = 0.8
    deleted_duplicates = 0
    thresholdLines = 100


    for k in range(0, len(tweets)):
        linesToGo = thresholdLines

        if k < len(splited):
            isDup = False
            for j in range(k + 1, len(splited)):
                if j < len(splited) and linesToGo > 0:
                    sim = jaccard(splited[k], splited[j])
                    #sim = computeJaccard(set(splited[k]), set(splited[j]))

                    if sim > threshold:
                        if isDup == False:
                            result.append(tweets[k])
                            isDup = True
                            #print("1: " + temp_tweets[i])
                            #print("2: " + temp_tweets[j])

                        del splited[j]
                        del tweets[j]
                        deleted_duplicates += 1
                        #print("P-{:d}: {:.0%}".format(threadID, (k / float(len(splited)))))
                else:
                    break
                linesToGo -= 1

        else:
            break

        if not isDup:
            result.append(tweets[k])

    p_progress.value += 1
    #print("PID-{0}, Tweets: {1} Duplicates: {2} ({3}/{4})".format(threadID, len(result), deleted_duplicates, p_progress.value, num_threads))

    values[1] = deleted_duplicates
    values[0] = result

def jaccard(a, b):
    intersection = float(len(set(a) & set(b)))
    if intersection == 0:
        return 0;

    union = float(len(set(a) | set(b)))

    if union == 0:
        return 0

    return intersection/union

'''
def computeJaccard(set1, set2):
    x = len(set1.intersection(set2))
    if x == 0:
        return 0

    y = len(set1.union(set2))
    if y == 0:
        return 0

    return x / float(y)
'''

if __name__ == '__main__':
    lock = Lock()
    input_path = "data/"
    output_path = "out/"
    done_path = "done/"
    num_threads = 10
    files_in_folder = os.listdir(input_path + "/")
    deleted_tweets_all = 0

    if not os.path.exists(input_path):
        os.makedirs(input_path)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    print("{0} Files found in {1}.".format(len(files_in_folder), input_path))


    for j, file in enumerate(files_in_folder, 1):
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
                    tweet = values[3].lower().split()
                    tweet.sort(reverse=True)
                    splited_tweets.append(tweet)
                    temp_tweets.append(line)


        for i in range(num_threads):
            p_shared_vals.append(
                m.list([[""], 0])
            )


        print("Starting with {0} Tweets ({1}).".format(len(temp_tweets), file))
        for i in range(num_threads):
            chunk = len(splited_tweets) / num_threads
            start_i = int(chunk * i)
            end_i = int((chunk * (i + 1)) - 1)
            tweets = temp_tweets[start_i:end_i]
            splited = splited_tweets[start_i:end_i]

            p = Process(target=run, args=(i, num_threads, splited, tweets, p_shared_vals[i], p_progress, start_i, end_i))
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
        finished = "{0:.0%}".format(j / len(files_in_folder))
        print("{0} - {1} finished, removed: {2}, time: {3}min".format(finished, file, sum, end_time))
        deleted_tweets_all += sum

    log.write("Final: {0}\n".format(deleted_tweets_all))
    print("Final: {0}\n".format(deleted_tweets_all))