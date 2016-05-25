import json,codecs, re, os
import gzip
from timeit import timeit

class Fileprocessing():
    def __init__(self,input_path,out_path):
        self.input_path = input_path
        self.output_path = out_path
        self.nr = 1
        self.out = 0
        self.processed_folders = 0
        self.read_tweets = 0
        self.saved_tweets = 0
        self.whole_saved_tweets = 0
        folders = os.listdir(self.input_path)
        for folder in folders:
            duration = timeit(lambda: self.process_folder_per_folder(folder), number=1),
             
            showDuration(duration, folder)
            
        print "Saved: " + str(self.whole_saved_tweets)
        print "Read: " + str(self.read_tweets)
        
    def open_json_file(self,filename):
        data = []
        with codecs.open(filename,'rU','utf-8') as f:
            for line in f:
                data.append(json.loads(line))
        
        return data
    
    def process_folder_per_folder(self, folder):
        files_in_folder = os.listdir(self.input_path + folder + "/")
        if self.out:
            self.out.close()
        
        self.out = codecs.open(self.output_path + folder + ".csv", "w", "utf-8")
 
        for file in files_in_folder:
            try:
                with gzip.open(self.input_path + folder + "/" + file, "rb", "utf-8") as infile:
                    for line in infile:
                          
                        self.read_tweets += 1
                        self.extract_data_from_json_element(json.loads(line))
            except:
                continue

        self.processed_folders +=1
                
    def extract_data_from_json_element(self,element):
                    
        output = []
        if element["lang"] == "en":
            
            tweet_text = self.check_tweet_text(element["text"])
            
            if tweet_text:
                
                if element["geo"] and element["place"]:
                    if len(element["geo"]["coordinates"]) == 2:
                        output.append(element["created_at"])
                        #output.append(element["lang"])
                        output.append(self.preprocess_text(element["user"]["screen_name"]))
                        output.append(str(element["id"]))
                        output.append(tweet_text)
                        output.append(str(element["geo"]["coordinates"]))
                        output.append(element["place"]["full_name"] + " (" + element["place"]["country"] + ")")
                        #print output
                        self.out.write("\t".join(output) + "\n")
                        self.saved_tweets += 1
                        self.whole_saved_tweets += 1
                elif element["geo"] and not element["place"]:
                    if len(element["geo"]["coordinates"]) == 2:
                        output.append(element["created_at"])
                        #output.append(element["lang"])
                        output.append(self.preprocess_text(element["user"]["screen_name"]))
                        output.append(str(element["id"]))
                        output.append(tweet_text)
                        output.append(str(element["geo"]["coordinates"]))
                        output.append("")
                        #print output
                        self.out.write("\t".join(output) + "\n")
                        self.saved_tweets += 1
                        self.whole_saved_tweets += 1
#                 elif not element["geo"] and element["place"]:
#                     output.append(element["created_at"])
#                     output.append(element["lang"])
#                     output.append(self.preprocess_text(element["user"]["screen_name"]))
#                     output.append(str(element["id"]))
#                     output.append(tweet_text)
#                     output.append("")
#                     output.append(element["place"]["full_name"] + " (" + element["place"]["country"] + ")")
#                     #print output
#                     self.out.write("\t".join(output) + "\n")
#                     self.saved_tweets += 1
    
    def check_tweet_text(self, text):
        length = 0
        words = text.split()
        for word in words:
            if not word.startswith("@") and not re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', word):
                length += 1
        
        if length < 5 or text.startswith("RT"):
            return 0
        else:
            return self.preprocess_text(text)        
    
    def preprocess_text(self, text):
        if "\t" in text:
            text = re.sub("\t"," ", text)
        if "\r" in text:
            text = re.sub("\r"," ", text)
        if "\n" in text:
            text = re.sub("\n", " ", text)
        
        return text

def showDuration(duration, folder):
    print "Elapsed time for {folder}: {duration}s".format(folder=folder,duration=duration[0])

if __name__ == '__main__':
    input_path = "C:/Users/Jennifer/Documents/semester_2/data_science/data/test2/"
    output_path = "C:/Users/Jennifer/Documents/semester_2/data_science/data/"
    fp = Fileprocessing(input_path,output_path)
    #duration = timeit(lambda: Fileprocessing(path), number=1), 
    #showDuration(duration)
