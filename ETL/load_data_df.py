from pyspark import SparkContext, SQLContext, SparkConf
import sys
import pyspark_cassandra


keyspace = 'sha185'
table = 'movie_rank'
outdir = sys.argv[1]

cluster_seeds = ['199.60.17.136', '199.60.17.173']
conf = SparkConf().set('spark.cassandra.connection.host', ','.join(cluster_seeds)).set('spark.dynamicAllocation.maxExecutors', 20)
sc = pyspark_cassandra.CassandraSparkContext(conf=conf)
sqlContext = SQLContext(sc)

df = sqlContext.read\
    .format("org.apache.spark.sql.cassandra")\
    .options(table=table, keyspace=keyspace)\
    .load()

df.write.format('parquet').save(outdir)