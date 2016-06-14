import threading
import codecs, os,sys, time


class RemoveTweets():
    def __init__(self, input_path, out_path):
        self.input_path = input_path
        self.output_path = out_path

        self.threshold = 0.8
        self.tweets = []
        self.temp_tweets = []

        files_in_folder = os.listdir(self.input_path + "/")
        file_len = len(files_in_folder)
        sum_job = 0
        sum_love = 0
        sum_n = 0

        #log = codecs.open(self.output_path + "log.txt", "a", "utf-8")

        for i, file in enumerate(files_in_folder, 1):
            out = codecs.open(self.output_path + file, "w", "utf-8")

            count_job= 0
            count_love = 0
            count_n = 0
            num_lines = 0

            with codecs.open(self.input_path + "/" + file, encoding='utf-8') as infile:
                for line in infile:
                    num_lines += 1
                    values = line.split("\t")

                    if len(values) > 3:
                        tweet = values[3].lower()

                        if "#job" in tweet or "#hiring" in tweet:
                            count_job += 1
                        elif "lov" in tweet and "baby" in tweet:
                            count_love += 1
                        elif "birthday" in tweet or "bday" in tweet or "b-day" in tweet:
                            count_n += 1
                        else:
                            out.write(line)

            sum_job += count_job
            sum_love += count_love
            sum_n += count_n

            print("{0}: {1}, ({2})".format(file, "{:.2%}".format((count_job + count_love + count_n) / num_lines), (str(i) + "/" + str(file_len))))

if __name__ == '__main__':
    input_path = "data/"
    output_path = "out/"
    removeTweets = RemoveTweets(input_path, output_path)