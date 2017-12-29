from spark_celery import SparkCeleryApp, SparkCeleryTask, RDD_builder, main
from recommender_main0 import *
from pyspark.sql.types import *
import datetime

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


@app.task(bind=True, base=SparkCeleryTask, name='data.period_receiver')
def period_receiver(self):

    def getlist(a,b):
        return a+b

    uri = "mongodb://199.60.17.175:27017/movies_recommendations.ratings?readPreference=primaryPreferred"
    df = app.sqlContext.read.format("com.mongodb.spark.sql").options(uri=uri).load()
    data = df.filter(((datetime.datetime.now() - datetime.timedelta(seconds=100))<df.updatedAt)&(df.updatedAt<datetime.datetime.now()))\
        .select(df.uid.alias('uid'), df.movie_id.alias('mid'), df.rating.alias('rank')).cache()
    if data.count() == 0:
        print '''
        ====================================no data received=====================================
        '''
    else:
        # data.show()
        mr = recommender(app.sqlContext)
        # mr.read_table('/user/sha185/ratings')
        '===================================change relevant name here======================================'
        mr.read_table('/user/yza358/mvratings1')
        '=================================================================================================='
        mr.receive_data(data)
        mr.train(5,10)
        # saving data(new) with append-mode instead of saving the union table with overwrite mode
        # data.write.format('parquet').mode('append').save('/user/sha185/ratings')
        '===================================change relevant name here======================================'
        data.write.format('parquet').mode('append').save('/user/yza358/mvratings1')
        '=================================================================================================='
        list = data.rdd.map(lambda line: line['uid']).collect()


        for i in set(list):
            uri1 = "mongodb://199.60.17.175:27017/movies_recommendations.recs"
            res = mr.recommend(i, 10)
            res = app.sc.parallelize(res).map(lambda line: (line[0],[line[1]])).reduceByKey(getlist).map(lambda (uid,mid):(uid,mid,datetime.datetime.now()))
            output = app.sqlContext.createDataFrame(res,['uid','mid','time'])
            # output.show()
            output.write.format("com.mongodb.spark.sql").options(uri=uri1).mode('append').save()


from celery.schedules import timedelta
app.conf.beat_schedule = {
     'check-beat': {
         'task': 'data.period_receiver',
         'schedule': timedelta(seconds=100),
     },
}

if __name__ == '__main__':
    # When called as a worker, run as a worker.
    main(options={'beat': True})
