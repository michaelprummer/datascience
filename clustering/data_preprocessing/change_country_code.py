import threading
import codecs, os,sys, time, numpy


class RemoveTweets():
    def __init__(self, input_path, out_path):
        self.input_path = input_path
        self.output_path = out_path
        files_in_folder = os.listdir(self.input_path + "/")
        file_len = len(files_in_folder)

        # Python 3 numpy bug
        dat = numpy.loadtxt("codes.csv", dtype='str', delimiter=";", usecols=[0, 2], comments=None)
        for i in range(0, numpy.size(dat[:, 0])):
            for j in range(0, numpy.size(dat[0, :])):
                mystring = dat[i, j]
                tick = len(mystring) - 1
                dat[i, j] = mystring[2:tick]

        codes = {}
        for d2 in dat:
            codes[d2[0]] = d2[1]


        for i, file in enumerate(files_in_folder, 1):
            out = codecs.open(self.output_path + file, "w", "utf-8")

            with codecs.open(self.input_path + "/" + file, encoding='utf-8') as infile:
                for line in infile:
                    values = line.split("\t")
                    values[5] = codes[values[5]]
                    out.write("\t".join(values))


if __name__ == '__main__':
    input_path = "data/"
    output_path = "out/"
    removeTweets = RemoveTweets(input_path, output_path)