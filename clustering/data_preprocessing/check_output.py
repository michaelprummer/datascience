import codecs

input_path = "C:/Users/Jennifer/Documents/semester_2/data_science/data/final_data/new_20150101.csv"
counter1 = 0
counter2 = 0
with codecs.open(input_path, "r", "utf-8") as input:
    for line in input:
        #line = line.strip()
        line = line.split("\t")
        if len(line) == 6:
            counter1 += 1
        else:
            print line
        counter2 += 1

print counter1
print counter2
"""
wenn beide Zahlen gleich und kein Tweettext ausgegeben wurde, 
dann stimmt Datei
"""
        
