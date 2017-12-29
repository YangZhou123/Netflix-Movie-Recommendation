from spark_celery import SparkCeleryApp, SparkCeleryTask, RDD_builder, main
from pyspark.sql.functions import col
from pyspark.sql.types import *
# from pyspark import SparkConf, SparkContext, SQLContext
import datetime,array
import numpy as np



BROKER_URL = 'amqp://fenq:rabbitmqpassword@localhost:5672/fenqvhost'
BACKEND_URL = 'rpc://'

def sparkconfig_builder():
    from pyspark import SparkConf
    return SparkConf().setAppName('SparkCeleryTask') \
        .set('spark.dynamicAllocation.enabled', 'true') \
        .set('spark.dynamicAllocation.schedulerBacklogTimeout', 1) \
        .set('spark.dynamicAllocation.minExecutors', 1) \
        .set('spark.dynamicAllocation.executorIdleTimeout', 20) \
        .set('spark.dynamicAllocation.cachedExecutorIdleTimeout', 60)

app = SparkCeleryApp(broker=BROKER_URL, backend=BACKEND_URL, sparkconfig_builder=sparkconfig_builder)


# Setting priority for workers allows primary workers, with spillover if the primaries are busy. Used to minimize the
# number of Spark contexts (active on the cluster, or caching common data). Works only with Celery >= 4.0
# Run a lower-priority consumer like this:
#   CONSUMER_PRIORITY=5 spark-submit --master=yarn-client demo.py
import os
from kombu import Queue
priority = int(os.environ.get('CONSUMER_PRIORITY', '10'))
app.conf['CELERY_QUEUES'] = (
    Queue('celery', consumer_arguments={'x-priority': priority}),
)





class recommender(SparkCeleryTask):
    name = 'recommender'
    @RDD_builder
    def readTable(self,inputdir):
        df = app.sqlContext.read.format('parquet').load(inputdir+'/table').cache()
        return df
    @RDD_builder
    def loadUF(self,inputdir):
        uf = app.sqlContext.read.format('parquet') \
            .load(inputdir+'/uf') \
            .rdd.map(lambda r: (r[0], array.array('d', r[1]))).cache()
        return uf
    @RDD_builder
    def loadMF(self,inputdir):
        mf = app.sqlContext.read.format('parquet') \
            .load(inputdir + '/mf') \
            .rdd.map(lambda r: (r[0], array.array('d', r[1]))).cache()
        return mf
    def loadModel(self,inputpath):
        model = MatrixFactorizationModel.load(app.sc, inputpath)
        return model
    def prediction(self,P, Q):
        return np.dot(P, Q.T)
    def newUser(self,inputdir, iter, Rating):
        def getlist(a, b):
            return a + b
        Rating.show()
        newUsers = Rating.select('uid').distinct().map(lambda l: l[0]).collect()
        if len(newUsers) == 0:
            return None
        else:
            lmbda = 0.01  # Regularisation weight
            gamma = 0.05  # Learning rate
            (ufKey,uf) = self.loadUF(inputdir)
            (mfKey,mf) = self.loadMF(inputdir)
            (dfKey,df) = self.readTable(inputdir)
            users = uf.keys().collect()
            movies = mf.keys().collect()
            rank = len(mf.collect()[1][1])
            newUsers = Rating.select('uid').distinct().map(lambda l: l[0]).collect()
            pl = []
            predl = []
            for u in set(newUsers):
                ur = Rating.where(Rating.uid == u).cache()
                newRatedm = ur.select('mid').distinct().rdd.map(lambda l: l[0]).collect()
                if u not in users:
                    P = 3 * np.random.rand(rank)
                    newMovies = Rating.where(Rating.uid == u)\
                        .select('mid', 'rank').distinct()\
                        .rdd.map(lambda l: (l[0], l[1])).collect()
                    md = dict((mid, r) for mid, r in newMovies)
                    newmf = mf.filter(lambda l: l[0] in md.keys())\
                        .map(lambda (key, arr): (key, np.array(arr))).collect()
                    mfd = dict((mid, arr) for mid, arr in newmf)
                    users.append(u)
                    self._cache[dfKey] = df.unionAll(ur)
                else:
                    # ratedm = ur.select('mid').distinct().rdd.map(lambda l:l[0]).collect()
                    # P = np.array(self.uf.filter(lambda l: l[0] == u).collect()[0][1])
                    # oldm = self.df.where(self.df.uid == u).where(self.df.mid.isin(ratedm))
                    # newRating = ur.unionAll(oldm).cache()
                    P = np.array(uf.filter(lambda l: l[0] == u).collect()[0][1])
                    um = df.where(df.uid == u).cache()
                    notUpdatedm = um.where(um.mid.isin(set(i for i in movies if i not in newRatedm))).cache()
                    newRatedm = newRatedm + notUpdatedm.select('mid').distinct().rdd.map(lambda l:l[0]).collect()
                    newRating = ur.unionAll(notUpdatedm).cache()
                    self._cache[dfKey] = df.where(df.uid != u).unionAll(newRating)
                    newMovies = newRating.select('mid', 'rank').rdd\
                        .map(lambda l: (l[0], l[1])).collect()
                    md = dict((mid, r) for mid, r in newMovies)
                    newmf = mf.filter(lambda l: l[0] in md.keys())\
                        .map(lambda (key, arr): (key, np.array(arr))).collect()
                    mfd = dict((mid, arr) for mid, arr in newmf)
                for epoch in range(iter):
                    for (m, r) in newMovies:
                        print '.\n.\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n'
                        print P
                        print mfd[m]
                        e = r - np.dot(P, mfd[m])
                        P += gamma * (e * mfd[m] - lmbda * P)
                pl.append((u,array.array('d',P)))
                self._cache[ufKey] = uf.filter(lambda l:l[0] not in set(newUsers)).union(app.sc.parallelize(pl))
                for (u,v) in pl:
                    l = self.pred(v,mf)
                    ll = [(u,m,float(r)) for (m,r) in l if m not in newRatedm]
                    ll.sort(key=lambda x:-x[2])
                    predl = predl + ll[:10]

                res = app.sc.parallelize(predl).map(lambda line: (line[0], [line[1]])).reduceByKey(getlist).map(
                    lambda (uid, mid): (uid, mid, datetime.datetime.now()))
                output = app.sqlContext.createDataFrame(res, ['uid', 'mid', 'time'])
            return output
    def pred(self, P,mf):
        l = []
        for (mid, arr) in mf.collect():
            l.append((mid, np.dot(P, np.array(arr).T)))
        return l
    def run(self):
        uri = "mongodb://199.60.17.175:27017/movies_recommendations.ratings?readPreference=primaryPreferred"
        df = app.sqlContext.read.format("com.mongodb.spark.sql").options(uri=uri).load()
        data = df.filter(((datetime.datetime.now() - datetime.timedelta(seconds=100)) < df.updatedAt) & (df.updatedAt < datetime.datetime.now())) \
            .select(df.uid.alias('uid'), df.movie_id.alias('mid'), df.rating.alias('rank')).cache()

        # data = data.select('uid', col('movie_id').alias('mid'), col('rating').alias('rank')).cache()
        # mr = recommender(app.sqlContext)
        # # mr.read_table('/user/sha185/ratings')
        # mr.read_table('/user/yza358/mvratings1')
        # mr.receive_data(data)
        # mr.train(5, 10)
        # saving data(new) with append-mode instead of saving the union table with overwrite mode
        output = self.newUser('snapshoot',10,data)
        if output:
            output.show()
            # data.write.format('parquet').mode('append').save('/user/yza358/mvratings1')
            # list = data.rdd.map(lambda line: line['uid']).collect()
            # schema = StructType([
            #     StructField('uid', IntegerType(), False),
            #     StructField('mid', IntegerType(), False)
            # ])
            uri1 = "mongodb://199.60.17.175:27017/movies_recommendations.recs"
            # uri2 = "mongodb://199.60.17.175:27017/movies_recommendations.rec"
            # res = mr.recommend(i, 10)
            # res = app.sc.parallelize(res).map(lambda line: (line[0], line[1]))
            # output = app.sqlContext.createDataFrame(res, schema)
            output.write.format("com.mongodb.spark.sql").options(uri=uri1).mode('append').save()

app.tasks.register(recommender())

from celery.schedules import timedelta
app.conf.beat_schedule = {
     'check-beat': {
         'task': 'recommender',
         'schedule': timedelta(seconds=100),
     },
}


if __name__ == '__main__':
    # When called as a worker, run as a worker.
    main(options={'beat': True})
