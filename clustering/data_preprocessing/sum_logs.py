import codecs, os, time

'''
Removed Duplicated (Range: 1200)
Jan: 1825657

'''

if __name__ == '__main__':
    input_path = "logs/in/"

    if not os.path.exists(input_path):
        os.makedirs(input_path)

    files_in_folder = os.listdir(input_path + "/")
    sums_tweets = []
    sums_time = []
    out = codecs.open("result.log", "w", "utf-8")

    for file in files_in_folder:

        with codecs.open(input_path + "/" + file, encoding='utf-8') as infile:
            for i, line in enumerate(infile, 1):
                if i % 2 == 1:
                    values = line.split("Deleted-Tweets: ")
                    if len(values) > 1:
                        sums_tweets.append(int(values[1].rstrip('\n')))
                else:
                    time_values = line.split("time: ")
                    if len(time_values) > 1:
                        tmp_time = time_values[1].rstrip('\n')
                        sums_time.append(float(time_values[1].rstrip('\r')))

    final_time = sum(sums_time)
    final_tweets = sum(sums_tweets)
    final_str = "Tweets removed: {:d} time: {:10.2f}h".format(final_tweets, final_time/60)
    out.write(final_str)
    print(final_str)
