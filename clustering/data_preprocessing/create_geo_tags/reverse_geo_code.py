from __future__ import print_function
import numpy, os, time, sys
import reverse_geocode

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

    def loadIDs(self, file):
        counter = 0
        ids = numpy.loadtxt(self.input_path + file, dtype='str', delimiter="\t", usecols=[2], comments=None)

        for i in range(len(ids)):
            counter += 1
            if self.limit and counter >= self.limit:
                return ids[:self.limit]
        return ids

    def loadGeoCoordinates(self, file):
        counter = 0
        geo_data = numpy.loadtxt(self.input_path + file, dtype='str', delimiter="\t", usecols=[4], comments=None)

        for i in range(len(geo_data)):
            counter += 1
            geo_data[i] = geo_data[i].strip("[]")
            if self.limit and counter >= self.limit:
                return geo_data[:self.limit]
        return geo_data

    def getCountry(self, filename):
        print("Start: " + filename)

        ids = self.loadIDs(filename)
        geo_data = self.loadGeoCoordinates(filename)

        print("Getting country for each tweet in file " + filename)
        if len(geo_data) != len(ids):
            print("Exit!")
            exit()

        out = open(self.output_path + filename, "w")
        data = []
        c = 0

        for i in range(len(geo_data)):
            try:
                lat, lng = tuple(geo_data[i].split(","))
                result = reverse_geocode.search([(lat, lng)])[0]

                if result['country'] != "":
                    data_str = "\t".join([ids[i], geo_data[i], result['city'], result['country_code'], result['country'], "\n"])
                    data.append(data_str)

                elif result['country_code'] == "XK":
                    data_str = "\t".join([ids[i], geo_data[i], result['city'], result['country_code'], "Kosovo", "\n"])
                    data.append(data_str)

                else:
                    self.not_usable_files.write(str(ids[i]) + "\n")
                    print(result)

            except:
                c+=1
                print(sys.exc_info(), "Lola: ", geo_data[i])
                self.not_usable_files.write(str(ids[i]) + "\n")

        print("Errors in file:", c)

        for d in data:
            out.write(d)


if __name__ == "__main__":
    data_path = "data/"
    output_path = "out/"
    limit = None
    special_files = None

    geo = GeoPreprocessing(data_path, output_path, special_files, limit)
