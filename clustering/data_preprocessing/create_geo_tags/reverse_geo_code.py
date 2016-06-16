from __future__ import print_function
import numpy, os, time, sys
import reverse_geocode, datetime
from datetime import datetime

class GeoPreprocessing():
    def __init__(self, input_path, output_path, special_files=None, limit=None):
        self.input_path = input_path

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        self.output_path = output_path
        self.not_usable_files = open(self.output_path + "tweets_without_gps.txt", "a")

        self.limit = limit

        if special_files:
            files = special_files
        else:
            files = os.listdir(self.input_path)

        for file in files:
            t1 = time.time()
            self.getCountry(file)
            print("Duration: %.1f" % ((time.time() - t1) / 60))

    def loadData(self, file):
        counter = 0
        tweet = numpy.loadtxt(self.input_path + file, dtype='str', delimiter="\t", usecols=[2, 4, 0, 3], comments=None)

        for i in range(len(tweet)):
            counter += 1
            tweet[i][1] = tweet[i][1].strip("[]")

            if self.limit and counter >= self.limit:
                return tweet[:self.limit]
        return tweet


    def getCountry(self, filename):
        print("Start: " + filename)
        tweets = self.loadData(filename)
        print("Getting country for each tweet in file " + filename)

        out = open(self.output_path + filename, "w")
        data = []
        c = 0

        for i in range(len(tweets)):
            try:
                lat, lng = tuple(tweets[i][1].split(","))
                result = reverse_geocode.search([(lat, lng)])[0]

                # Timestamp
                timeFormat = '%Y-%m-%d %H:%M:%S'
                ts = time.strftime(timeFormat, time.strptime(tweets[i][2], '%a %b %d %H:%M:%S +0000 %Y'))
                timestamp = str(time.mktime(datetime.strptime(ts, timeFormat).timetuple()))[:-2]

                if result['country'] != "":
                    data_str = "\t".join([tweets[i][0], timestamp, tweets[i][1], result['city'], result['country_code'], result['country'], tweets[i][3], "\n"])
                    data.append(data_str)

                elif result['country_code'] == "XK":
                    data_str = "\t".join([tweets[i][0], timestamp, tweets[i][1], result['city'], result['country_code'], result['country'], tweets[i][3], "\n"])
                    data.append(data_str)

                else:
                    self.not_usable_files.write(str(tweets[i][0]) + "\n")
                    print(result)
            except:
                c+=1
                print(sys.exc_info(), "Lola: ", tweets[i][2])
                self.not_usable_files.write(filename + ": " +  str(tweets[i]) + "\n")

        print("Errors in file:", c)

        for d in data:
            out.write(d)


if __name__ == "__main__":
    data_path = "data/"
    output_path = "out/"
    limit = None
    special_files = None

    geo = GeoPreprocessing(data_path, output_path, special_files, limit)
