import sys,json
from pyspark import SparkConf
import pyspark_cassandra
from decimal import *

cluster_seeds = ['199.60.17.136', '199.60.17.173']
conf = SparkConf().set('spark.cassandra.connection.host', ','.join(cluster_seeds))
sc = pyspark_cassandra.CassandraSparkContext(conf=conf)
tablename = 'details'

def nullitem(line, key_val):
    if key_val in line:
        return line[key_val]
    else:
        return "N/A"

def main(inputs, keyspace):
    text = sc.textFile(inputs)

    result = text.map(lambda line: {'id':json.loads(line)["id"],
                                    'actors': nullitem(json.loads(line), "Actors"),
                                    'awards': nullitem(json.loads(line), "Awards"),
                                    'country': nullitem(json.loads(line), "Country"),
                                    'director': nullitem(json.loads(line), "Director"),
                                    'genre': nullitem(json.loads(line), "Genre"),
                                    'imdbid': nullitem(json.loads(line), "imdbID"),
                                    'imdbrating': nullitem(json.loads(line), "imdbRating"),
                                    'imdbvotes': nullitem(json.loads(line), "imdbVotes"),
                                    'language': nullitem(json.loads(line), "Language"),
                                    'metascore': nullitem(json.loads(line), "Metascore"),
                                    'plot': nullitem(json.loads(line), "Plot"),
                                    'poster': nullitem(json.loads(line), "Poster"),
                                    'rated': nullitem(json.loads(line), "Rated"),
                                    'released': nullitem(json.loads(line), "Released"),
                                    'response': nullitem(json.loads(line), "Response"),
                                    'runtime': nullitem(json.loads(line), "Runtime"),
                                    'title': json.loads(line)["Title"],
                                    'totalseasons': nullitem(json.loads(line), "totalSeasons"),
                                    'type': nullitem(json.loads(line), "Type"),
                                    'writer': nullitem(json.loads(line), "Writer"),
                                    'year':json.loads(line)["Year"]

                                    })
    # print result.collect()
    result.saveToCassandra(keyspace,tablename)

if __name__ == "__main__":
    inputs = sys.argv[1]
    keyspace = sys.argv[2]
    main(inputs,keyspace)