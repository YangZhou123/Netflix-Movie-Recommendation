from cassandra.cluster import Cluster
import sys, re, os, datetime
from cassandra.query import BatchStatement, SimpleStatement
from cassandra import ConsistencyLevel, Timeout, InvalidRequest
input = sys.argv[1]
keyspace = sys.argv[2]
table = sys.argv[3]

cluster = Cluster(['199.60.17.136', '199.60.17.173'])
session = cluster.connect()
session.set_keyspace(keyspace=keyspace)
insert_user = session.prepare("INSERT INTO %s (mid,uid,rank,date) VALUES (?,?,?,?)"%(table))
batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)

fcount = 0
n_file = str(len(os.listdir(input)))
for f in os.listdir(input):
    fcount = fcount+1
    records = []
    file = open(os.path.join(input, f))
    mid = int(f[3:10])
    for line in file:
        if line[-2:] == ':\n':
            pass
        else:
            l = line.split(',')
            records.append((mid, int(l[0]), int(l[1]),datetime.datetime.strptime(l[2], '%Y-%m-%d\n')))
    file.close()

    lenth = len(records)
    count = 0
    for (mid,uid,rank,date) in records:
        count+=1
        batch.add(insert_user, (mid,uid,rank,date))
        if count%200 == 0 or count == lenth:
            # print count
            # print 'batch %i'%(count/200)
            try:
                session.execute(batch)
            except Timeout as error:
                print error
                session.execute(batch)
            batch.clear()

    print(f + ' is readed.'+str(fcount)+'/'+n_file)