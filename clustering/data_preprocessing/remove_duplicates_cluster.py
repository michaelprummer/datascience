import codecs, os


if __name__ == '__main__':
    input_path = "data/"
    output_path = "out/"
    files_in_folder = os.listdir(input_path + "/")

    if not os.path.exists(input_path):
        os.makedirs(input_path)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    print("{0} Files found in {1}.".format(len(files_in_folder), input_path))

    for file in files_in_folder:
        out = codecs.open(output_path + file, "w", "utf-8")

        file = codecs.open(input_path + file, encoding='utf-8')
        fileList = []

        fileNDF = []
        fileLDA = []
        fileKM = []

        # out
        outFile = []

        for i, line in enumerate(file, 0):
            fileList.append(line)
            values = line.split("\t")

            if values[1] != "-1":
                fileNDF.append(values)
            elif values[2] != "-1":
                fileLDA.append(values)
            elif values[3] != "-1":
                fileKM.append(values)
            else:
                print("fail")

        fileList = sorted(fileList, key=lambda x: x[0])
        fileNDF = sorted(fileNDF, key=lambda x: x[0])
        fileLDA = sorted(fileLDA, key=lambda x: x[0])
        fileKM = sorted(fileKM, key=lambda x: x[0])

        for k, lineA in enumerate(fileNDF, 0):
            lineA[2] = fileLDA[k][2]
            lineA[3] = fileKM[k][3]
            out.write("\t".join(lineA))


        exit("EZ")


