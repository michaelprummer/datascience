    def read_csv(self, path, special_files, limit=None):
        counter = 0
        tweets = list()
        if special_files:
            files = special_files
        else:
            files = os.listdir(path)
            
        for file in files:
            print("Loading file " + file)
            reader = self.unicode_csv_reader(open(path + file))
            for _, _, _, tweet, _, _ in reader:
                tweet = self.preprocess_tweet(tweet)
                tweets.append(tweet)
                counter += 1
                if limit and counter > limit:
                    return tweets
                
#             with codecs.open(path + file, "r") as input:
#                 for line in unicodecsv.reader(input, delimiter="\t",encoding="utf-8"):
#                     tweet = self.preprocess_tweet(line[3])
#                     tweets.append(tweet)
#                     
#                     counter += 1
#                     if limit and counter > limit:
#                         return tweets
        
        return tweets
    
    def unicode_csv_reader(self, utf8_data, delimiter="\t", **kwargs):
        csv_reader = csv.reader(utf8_data, delimiter=delimiter, **kwargs)
        for row in csv_reader:
            yield [unicode(cell, 'utf-8') for cell in row]