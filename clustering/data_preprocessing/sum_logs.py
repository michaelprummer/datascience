import codecs, os, time

'''
Removed Duplicated (Range: 1200)
Jan: 1825657

'''

if __name__ == '__main__':
    input_path = "logs/in/"
    output_path = "logs/out/"

    if not os.path.exists(input_path):
        os.makedirs(input_path)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    files_in_folder = os.listdir(input_path + "/")
    log_sums = []

    for file in files_in_folder:
        out = codecs.open(output_path + file, "w", "utf-8")

        with codecs.open(input_path + "/" + file, encoding='utf-8') as infile:
            for i, line in enumerate(infile, 1):
                if i % 2 == 1:
                    values = line.split("Deleted-Tweets: ")
                    if len(values) > 1:
                        log_sums.append(int(values[1].rstrip('\n')))

    final = sum(log_sums)
    final_str = "Sum: {0}".format(final)
    out.write(final_str)
    print(final_str)
