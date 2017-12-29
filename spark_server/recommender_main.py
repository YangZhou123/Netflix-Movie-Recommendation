from pyspark import SparkConf, SparkContext, SQLContext
from pyspark.mllib.recommendation import *
import sys


class recommender(object):

    def __init__(self,sqlContext):
        self.model =None
        self.df = None
        self.sqlContext = sqlContext


    def read_table(self,inputdir):
        self.df = self.sqlContext.read.format('parquet').load(inputdir)

    # def save_table(self, outputdir):
    #     self.df.write.mode('overwrite').format('parquet').save(outputdir)

    def train(self,rank,iter):
        rdd = self.df.rdd.map(lambda r: (r['uid'],r['mid'],r['rank']))
        self.model = ALS.train(rdd,rank,iter)

    def recommend(self,uid,num):
        return self.model.recommendProducts(uid,num)

    def receive_data(self,data):
        self.df = self.df.unionAll(data)


if __name__ == '__main__':
    conf = SparkConf().setAppName("MovieLensALS")
    sc = SparkContext(conf=conf)
    sqlContext = SQLContext(sc)
    input = sys.argv[1]
    outdir = sys.argv[2]
    r = recommender(sqlContext)
    r.read_table(input)
    r.train(6,10)
    uf = r.model.userFeatures()
    mf = r.model.productFeatures()
    sqlContext.createDataFrame(uf).write.mode('overwrite')\
            .format('parquet').save(outdir+'/uf')
    sqlContext.createDataFrame(mf).write.mode('overwrite')\
            .format('parquet').save(outdir+'/mf')
    r.df.write.mode('overwrite')\
            .format('parquet').save(outdir+'/table')