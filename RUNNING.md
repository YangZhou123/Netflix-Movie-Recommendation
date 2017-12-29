## frontend
### login in cloud server with ssh connection:
```
ssh cloud@199.60.17.175
password: sfucmpt732
```
### access web application folder
```
cd netflix_recommender/website/
```
### start web application
```
node app.js
```
wait for the message
```
Express server listening on port 8000 in development mode
```

### access the frontend at
http://199.60.17.175:8000/

## backend
### copy rating data:
```
hdfs dfs -cp /user/sha185/ratings /user/yourname/rating
```

### change relevant name in data_reciever_main.py
```
'/user/yza358/mvratings1' =====>'//user/yourname/rating'
```

### copy the folder spark_server to your space
```
scp -r spark_server yourname@gateway.sfucloud.ca:
```

### login your cluster space , cd to spark_server
```
ssh yourname@gateway.sfucloud.ca
cd spark_server 
```

### run the origin rec-sys code (spark celery , period tasks)
```
spark-submit --master yarn-client --packages org.mongodb.spark:mongo-spark-connector_2.10:1.1.0 data_receiver_main.py
```

### run the improved rec-sys code (spark celery , period tasks)
first run
```
spark-submit --master yarn-client recommender_main.py rating snapshoot
```
then
```
spark-submit --master yarn-client --packages org.mongodb.spark:mongo-spark-connector_2.10:1.1.0 new_data_receiver.py
```