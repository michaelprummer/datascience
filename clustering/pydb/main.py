from __future__ import print_function
import MySQLdb, os, codecs, time

db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="",  # your password
                     db="datascience",
                     charset='utf8',
                     use_unicode=True)

def updateCllusterIDs():
    cur = db.cursor()
    cur.execute("""UPDATE tweets, (SELECT DISTINCT nmfID, tweetId FROM tweets WHERE nmfID > 0) b
    SET tweets.nmfID = b.nmfID
    WHERE tweets.tweetId = b.tweetId AND tweets.nmfID = -1
    """)
    db.commit()
    print("NMF DONE")

    cur.execute("""UPDATE tweets, (SELECT DISTINCT ldaID, tweetId FROM tweets WHERE ldaID > 0) b
    SET tweets.ldaID = b.ldaID
    WHERE tweets.tweetId = b.tweetId AND tweets.ldaID = -1""")
    db.commit()
    print("LDA DONE")

    cur.execute("""UPDATE tweets, (SELECT DISTINCT kmeansID, tweetId FROM tweets WHERE kmeansID > 0) b
    SET tweets.kmeansID = b.kmeansID
    WHERE tweets.tweetId = b.tweetId AND tweets.kmeansID = -1""")
    cur.execute
    db.commit()
    print("KM DONE")

def deleteDuplicates():
    cur = db.cursor()
    cur.execute("DELETE n1 FROM tweets n1, tweets n2 WHERE n1.tweetId = n2.tweetId")
    db.commit()


def importData():
    cur = db.cursor()
    input = "data/"
    files = os.listdir(input)
    # limit = 10

    for file in files:
        t1 = time.time()

        with codecs.open(input + file, encoding='utf-8') as infile:
            print("File: " + file)

            for i, line in enumerate(infile, 0):
                vals = line.split("\t")

                tweetText = vals[6].encode('ascii', 'ignore')

                try:
                    cur.execute("""INSERT INTO tweets VALUES (%s,%s,%s,%s,%s,%s,%s)""", (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], tweetText))
                except Exception as e:
                    print(e)

                if i % 100000 == 0:
                    print(str(i / 20000) + "%")
                    db.commit()


                #if i >limit:
                 #   break

        db.commit()
        print("Time: {0}s for {1}".format(time.time()-t1, file))
    db.close()


# Step 1
#importData()

# Step 2
#updateCllusterIDs()

# Step 3
#deleteDuplicates()