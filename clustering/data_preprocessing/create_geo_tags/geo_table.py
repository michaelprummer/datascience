from __future__ import print_function
import numpy, os, time, sys

class GeoPreprocessing():
    countries = {}
    country_codes = {}
    cities = {}
    counter = 0
    out_city = None
    out_country = None

    def __init__(self, input_path, output_path):
        self.input_path = input_path

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        self.output_path = output_path

        files = os.listdir(self.input_path)

        self.out_city = open(self.output_path + "cities.csv", "w")
        self.out_country = open(self.output_path + "countries.csv", "w")


        for file in files:
            t1 = time.time()
            self.loadData(file)
            print("Duration: %.1f" % ((time.time() - t1) / 60))
            print(self.counter)

    def loadData(self, file):
        out = open(self.output_path + file, "w")

        tweets = numpy.loadtxt(self.input_path + file, dtype='str', delimiter="\t", comments=None)

        for i, tweet in enumerate(tweets):
            self.counter += 1

if __name__ == "__main__":
    data_path = "data/"
    output_path = "out/"

    geo = GeoPreprocessing(data_path, output_path)
