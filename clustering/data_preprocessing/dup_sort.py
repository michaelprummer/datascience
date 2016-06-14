from operator import itemgetter
import codecs, os,sys, time


class RemoveTweets():
    def __init__(self, input_path, out_path):
        self.input_path = input_path
        self.output_path = out_path
        files_in_folder = os.listdir(self.input_path + "/")

        for i, file in enumerate(files_in_folder, 1):
            self.tweets = []
            out = codecs.open(self.output_path + file, "w", "utf-8")

            with codecs.open(self.input_path + "/" + file, encoding='utf-8') as infile:
                for line in infile:
                    self.tweets.append(line.split("\t"))

                self.tweets.sort(key=itemgetter(3))

                for t in self.tweets:
                    out.write("\t".join(t))

            print("{0:.0%}".format(i/float(len(files_in_folder))))


if __name__ == '__main__':
    input_path = "data/"
    output_path = "out/"
    removeTweets = RemoveTweets(input_path, output_path)