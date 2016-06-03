import threading
import codecs, os,sys, time


class Weather():
    def __init__(self, input_path, out_path):
        self.input_path = input_path
        self.output_path = out_path

        self.threshold = 0.8
        self.tweets = []
        self.temp_tweets = []

        files_in_folder = os.listdir(self.input_path + "/")
        file_len = len(files_in_folder)
        sum = 0
        for i, file in enumerate(files_in_folder, 1):
            log = codecs.open(self.output_path + "log.txt", "a", "utf-8")
            out = codecs.open(self.output_path + file, "w", "utf-8")
            deleted_weather = 0

            #try:
            with codecs.open(self.input_path + "/" + file, encoding='utf-8') as infile:
                for line in infile:
                    values = line.split("\t")

                    if len(values) > 3:
                        tweet = values[3].lower()

                        count = 0
                        if "weather" in tweet:
                            count += 1
                        if "temperature" in tweet:
                            count += 1
                        if "wind" in tweet:
                            count += 1
                        if "barometer" in tweet:
                            count += 2
                        if "humidity" in tweet:
                            count += 2
                        if "rain" in tweet:
                            count += 1

                        if count < 2:
                            out.write(line)
                        else:
                            deleted_weather += 1
                    #else:
                        #print("Tweet error: " + tweet)

            log.write("Weather-Tweets (" + file + "): " + str(deleted_weather) + "\n")
            sum+=deleted_weather
            print("file: " + str(i) + "/"+str(file_len))
        log.write("Sum: " + str(sum) + "\n")

if __name__ == '__main__':
    input_path = "E:/data/"
    output_path = "E:/out/"
    weather = Weather(input_path, output_path)