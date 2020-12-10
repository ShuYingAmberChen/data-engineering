 # W205 Project 3 Report - Understanding User Behaviour
## Author: Shu Ying (Amber) Chen

**Spin up and check the clusters**

```
docker-compose up -d
```

**The docker-compose.yml setup**
```
---
version: '2'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 32181
      ZOOKEEPER_TICK_TIME: 2000
    expose:
      - "2181"
      - "2888"
      - "32181"
      - "3888"
    extra_hosts:
      - "moby:127.0.0.1"

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:32181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    expose:
      - "9092"
      - "29092"
    extra_hosts:
      - "moby:127.0.0.1"

  cloudera:
    image: midsw205/hadoop:0.0.2
    hostname: cloudera
    expose:
      - "8020" # nn
      - "8888" # hue
      - "9083" # hive thrift
      - "10000" # hive jdbc
      - "50070" # nn http
    ports:
      - "8888:8888"
    extra_hosts:
      - "moby:127.0.0.1"

  spark:
    image: midsw205/spark-python:0.0.6
    stdin_open: true
    tty: true
    volumes:
      - ~/w205:/w205
    expose:
      - "8888"
    #ports:
    #  - "8888:8888"
    depends_on:
      - cloudera
    environment:
      HADOOP_NAMENODE: cloudera
      HIVE_THRIFTSERVER: cloudera:9083
    extra_hosts:
      - "moby:127.0.0.1"
    command: bash

  presto:
    image: midsw205/presto:0.0.1
    hostname: presto
    volumes:
      - ~/w205:/w205
    expose:
      - "8080"
    environment:
      HIVE_THRIFTSERVER: cloudera:9083
    extra_hosts:
      - "moby:127.0.0.1"

  mids:
    image: midsw205/base:0.1.9
    stdin_open: true
    tty: true
    volumes:
      - ~/w205:/w205
    expose:
      - "5000"
    ports:
      - "5000:5000"
    extra_hosts:
      - "moby:127.0.0.1"

```

**The game-api.py setup**

```
#!/usr/bin/env python
import json
from kafka import KafkaProducer
from flask import Flask, request

app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers='kafka:29092')


def log_to_kafka(topic, event):
    event.update(request.headers)
    producer.send(topic, json.dumps(event).encode())


@app.route("/")
def default_response():
    default_event = {'event_type': 'default'}
    log_to_kafka('events', default_event)
    return "This is the default response!\n"


@app.route("/purchase_a_sword", methods = ['GET', 'POST'])
def purchase_a_sword():
    if request.method == 'POST' and request.headers['Content-Type'] == 'application/json':
        purchase_sword_event = {'event_type': 'purchase_sword', 'attributes': json.dumps(request.json)}
        log_to_kafka('events', purchase_sword_event)
        return "Sword Purchased: " + json.dumps(request.json) + "\n"
    
    else:
        purchase_sword_event = {'event_type': 'purchase_sword'}
        log_to_kafka('events', purchase_sword_event)
        return "Sword Purchased!\n"


@app.route("/purchase_a_shield", methods = ['GET', 'POST'])
def purchase_a_shield():
    if request.method == 'POST' and request.headers['Content-Type'] == 'application/json':
        purchase_shield_event = {'event_type': 'purchase_shield', 'attributes': json.dumps(request.json)}
        log_to_kafka('events', purchase_shield_event)
        return "Shield Purchased: " + json.dumps(request.json) + "\n"
    
    else:
        purchase_shield_event = {'event_type': 'purchase_shield'}
        log_to_kafka('events', purchase_shield_event)
        return "Shield Purchased!\n"

@app.route("/join_a_guild", methods = ['GET', 'POST'])
def join_guild():
    if request.method == 'POST' and request.headers['Content-Type'] == 'application/json':
        join_guild_event = {'event_type': 'join_guild', 'attributes': json.dumps(request.json)}
        log_to_kafka('events', join_guild_event)
        return "Joined guild: " + json.dumps(request.json) + "\n"
    
    else:
        join_guild_event = {'event_type': 'join_guild'}
        log_to_kafka('events', join_guild_event)
        return "Guild Joined!\n"

```

**Run flask**

```
docker-compose exec mids env FLASK_APP=/w205/project-3-ShuYingAmberChen/game_api.py flask run --host 0.0.0.0
```

**Start the second terminal , where you can read streaming data from Kafka**

```
docker-compose exec mids kafkacat -C -b kafka:29092 -t events -o beginning
```

**Start the third terminal to run the write_swords_stream.py**

**The write_swords_stream.py setup**

```
#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, from_json
from pyspark.sql.types import StructType, StructField, StringType


def purchase_sword_event_schema():
    """
    root
    |-- Accept: string (nullable = true)
    |-- Host: string (nullable = true)
    |-- User-Agent: string (nullable = true)
    |-- event_type: string (nullable = true)
    |-- timestamp: string (nullable = true)
    |-- attributes: structure (nullable = true)
    """
    return StructType([
        StructField("Accept", StringType(), True),
        StructField("Host", StringType(), True),
        StructField("User-Agent", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("attributes", StructType([
            StructField('level', StringType(), True),
            StructField('colour', StringType(), True)
        ]), True),
    ])

def purchase_shield_event_schema():
    """
    root
    |-- Accept: string (nullable = true)
    |-- Host: string (nullable = true)
    |-- User-Agent: string (nullable = true)
    |-- event_type: string (nullable = true)
    |-- timestamp: string (nullable = true)
    |-- attributes: structure (nullable = true)
    """
    return StructType([
        StructField("Accept", StringType(), True),
        StructField("Host", StringType(), True),
        StructField("User-Agent", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("attributes", StructType([
            StructField('level', StringType(), True),
            StructField('colour', StringType(), True)
        ]), True),
    ])


def join_guild_event_schema():
    """
    root
    |-- Accept: string (nullable = true)
    |-- Host: string (nullable = true)
    |-- User-Agent: string (nullable = true)
    |-- event_type: string (nullable = true)
    |-- timestamp: string (nullable = true)
    |-- attributes: structure (nullable = true)
    """
    return StructType([
        StructField("Accept", StringType(), True),
        StructField("Host", StringType(), True),
        StructField("User-Agent", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("attributes", StructType([
            StructField('level', StringType(), True),
            StructField('name', StringType(), True)
        ]), True),
    ])

@udf('boolean')
def is_sword_purchase(event_as_json):
    """udf for filtering events
    """
    event = json.loads(event_as_json)
    if event['event_type'] == 'purchase_sword':
        return True
    return False

@udf('boolean')
def is_shield_purchase(event_as_json):
    """udf for filtering events
    """
    event = json.loads(event_as_json)
    if event['event_type'] == 'purchase_shield':
        return True
    return False

@udf('boolean')
def is_join_guild(event_as_json):
    """udf for filtering events
    """
    event = json.loads(event_as_json)
    if event['event_type'] == 'join_guild':
        return True
    return False


def main():
    """main
    """
    spark = SparkSession \
        .builder \
        .appName("ExtractEventsJob") \
        .getOrCreate()

    raw_events = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "events") \
        .load()

    sword_purchases = raw_events \
        .filter(is_sword_purchase(raw_events.value.cast('string'))) \
        .select(raw_events.value.cast('string').alias('raw_event'),
                raw_events.timestamp.cast('string'),
                from_json(raw_events.value.cast('string'),
                          purchase_sword_event_schema()).alias('json')) \
        .select('raw_event', 'timestamp', 'json.*')
    
    shield_purchases = raw_events \
        .filter(is_shield_purchase(raw_events.value.cast('string'))) \
        .select(raw_events.value.cast('string').alias('raw_event'),
                raw_events.timestamp.cast('string'),
                from_json(raw_events.value.cast('string'),
                          purchase_shield_event_schema()).alias('json')) \
        .select('raw_event', 'timestamp', 'json.*')
    
    join_guilds = raw_events \
        .filter(is_join_guild(raw_events.value.cast('string'))) \
        .select(raw_events.value.cast('string').alias('raw_event'),
                raw_events.timestamp.cast('string'),
                from_json(raw_events.value.cast('string'),
                          join_guild_event_schema()).alias('json')) \
        .select('raw_event', 'timestamp', 'json.*')

    sink_sword = sword_purchases \
        .writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints_for_sword_purchases") \
        .option("path", "/tmp/sword_purchases") \
        .trigger(processingTime="10 seconds") \
        .start()

    sink_shield = shield_purchases \
        .writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints_for_shield_purchases") \
        .option("path", "/tmp/shield_purchases") \
        .trigger(processingTime="10 seconds") \
        .start()

    sink_guild = join_guilds \
        .writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints_for_join_guilds") \
        .option("path", "/tmp/join_guilds") \
        .trigger(processingTime="10 seconds") \
        .start()
    
    sink_sword.awaitTermination()
    sink_shield.awaitTermination()
    sink_guild.awaitTermination()


if __name__ == "__main__":
    main()

```

**Run it**

```
docker-compose exec spark spark-submit /w205/project-3-ShuYingAmberChen/write_swords_stream.py  
```

**Use Apache Bench to generate some test data**

**The bash shell script to generate random test data**

```
#!/bin/bash

MAX=100
count=1
num1=1
num2=1
num3=1

while [ $count -le $MAX ]
do
  userid=$((RANDOM%100+1))
  num1=$((RANDOM%20+1))
  num2=$((RANDOM%10+1))
  num3=$((RANDOM%5+1))
  num4=$((RANDOM%5+1))
  num5=$((RANDOM%5+1))
  docker-compose exec mids ab -p /w205/project-3-ShuYingAmberChen/sword$num3.json -T application/json -n $num1 -H "Host: user$userid.comcast.com" http://localhost:5000/purchase_a_sword
  docker-compose exec mids ab -p /w205/project-3-ShuYingAmberChen/shield$num4.json -T application/json -n $num2 -H "Host: user$userid.comcast.com" http://localhost:5000/purchase_a_shield
  docker-compose exec mids ab -p /w205/project-3-ShuYingAmberChen/guild$num5.json -T application/json -n 1 -H "Host: user$userid.comcast.com" http://localhost:5000/join_a_guild
  count=$(expr $count + 1)
  sleep 10
done
```

**Start the fourth terminal and run the shell script**

bash while-ab-test.sh


**Start the fifth terminal and check the streaming data is being written to HDFS**

```
docker-compose exec cloudera hadoop fs -ls /tmp/
```

Should see below

```
Found 9 items
drwxrwxrwt   - root   supergroup          0 2020-08-01 22:15 /tmp/checkpoints_for_join_guilds
drwxrwxrwt   - root   supergroup          0 2020-08-01 22:15 /tmp/checkpoints_for_shield_purchases
drwxrwxrwt   - root   supergroup          0 2020-08-01 22:15 /tmp/checkpoints_for_sword_purchases
drwxrwxrwt   - mapred mapred              0 2016-04-06 02:26 /tmp/hadoop-yarn
drwx-wx-wx   - hive   supergroup          0 2020-08-01 22:15 /tmp/hive
drwxr-xr-x   - root   supergroup          0 2020-08-01 22:16 /tmp/join_guilds
drwxrwxrwt   - mapred hadoop              0 2016-04-06 02:28 /tmp/logs
drwxr-xr-x   - root   supergroup          0 2020-08-01 22:16 /tmp/shield_purchases
drwxr-xr-x   - root   supergroup          0 2020-08-01 22:16 /tmp/sword_purchases
```

```
docker-compose exec cloudera hadoop fs -ls /tmp/sword_purchases
```

Should see something like below

```
Found 7 items
drwxr-xr-x   - root supergroup          0 2020-08-01 22:17 /tmp/sword_purchases/_spark_metadata
-rw-r--r--   1 root supergroup       3308 2020-08-01 22:16 /tmp/sword_purchases/part-00000-06d2c8d1-cf8b-4d1c-9d77-02c6d8aba0be-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3376 2020-08-01 22:16 /tmp/sword_purchases/part-00000-248bbdac-f396-4aba-9806-91f67fbd5835-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3302 2020-08-01 22:16 /tmp/sword_purchases/part-00000-910d57e5-7e35-4561-9567-38453ddd3011-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3412 2020-08-01 22:17 /tmp/sword_purchases/part-00000-ef5ce889-64dc-4ccd-bd95-e0224ded254c-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3300 2020-08-01 22:16 /tmp/sword_purchases/part-00000-f1fc4c2a-c931-43c6-bfb1-d01b4b851ba4-c000.snappy.parquet
-rw-r--r--   1 root supergroup       1034 2020-08-01 22:16 /tmp/sword_purchases/part-00000-f2e004fb-74ec-4090-8b2c-280285df89a9-c000.snappy.parquet
```

```
docker-compose exec cloudera hadoop fs -ls /tmp/shield_purchases
```

Should see something like below

```
Found 8 items
drwxr-xr-x   - root supergroup          0 2020-08-01 22:17 /tmp/shield_purchases/_spark_metadata
-rw-r--r--   1 root supergroup       3216 2020-08-01 22:16 /tmp/shield_purchases/part-00000-517d33e4-e0a8-4c8a-9d1d-bad377af7c21-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3275 2020-08-01 22:16 /tmp/shield_purchases/part-00000-8800467d-fb19-4afd-9a57-26aad31d0d51-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3290 2020-08-01 22:16 /tmp/shield_purchases/part-00000-8af9e1c0-20fe-4c99-8389-e4ed459a8cf7-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3222 2020-08-01 22:17 /tmp/shield_purchases/part-00000-a45fc987-a4b7-4344-9045-4dc0a0ea3b45-c000.snappy.parquet
-rw-r--r--   1 root supergroup       1034 2020-08-01 22:16 /tmp/shield_purchases/part-00000-d16930e1-5271-400b-ac8b-dca69b2a5c6e-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3229 2020-08-01 22:16 /tmp/shield_purchases/part-00000-e85d3708-6644-4250-be35-626698ea6bee-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3298 2020-08-01 22:17 /tmp/shield_purchases/part-00000-ff588add-af7d-439b-a829-e5e3f34a4b01-c000.snappy.parquet
```

```
docker-compose exec cloudera hadoop fs -ls /tmp/join_guilds
```

Should see something like below

```
Found 10 items
drwxr-xr-x   - root supergroup          0 2020-08-01 22:17 /tmp/join_guilds/_spark_metadata
-rw-r--r--   1 root supergroup       3130 2020-08-01 22:17 /tmp/join_guilds/part-00000-14a7f354-ed0d-48fd-978b-f94da3608504-c000.snappy.parquet
-rw-r--r--   1 root supergroup       1030 2020-08-01 22:16 /tmp/join_guilds/part-00000-47d5b2be-9102-47cb-bd1f-83da731733da-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3103 2020-08-01 22:16 /tmp/join_guilds/part-00000-4bb4a7a0-244b-4d55-8ef4-2628afa941b4-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3123 2020-08-01 22:16 /tmp/join_guilds/part-00000-6457bdf4-5181-49f6-8e57-c6af5833a596-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3113 2020-08-01 22:16 /tmp/join_guilds/part-00000-a116091b-df59-417f-892c-a5f2d488285c-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3160 2020-08-01 22:16 /tmp/join_guilds/part-00000-b827b637-3bb6-45c2-b911-2194d4aec7a3-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3113 2020-08-01 22:17 /tmp/join_guilds/part-00000-e5eac77a-08eb-4f21-9b44-e5cbfe7e916b-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3158 2020-08-01 22:17 /tmp/join_guilds/part-00000-e6febdef-bd3e-40a7-b384-4e2aac9778f8-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3118 2020-08-01 22:17 /tmp/join_guilds/part-00000-ed866521-a71a-40b9-a0ba-5f8879a7f294-c000.snappy.parquet
```

* Note that you can see the streaming data is growing by re-running above lines of code

**Set up the write_hive_table.py to register temp table for each event with the event schema defined in write_sword_stream.py**

```
#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""
import json
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import udf
from pyspark.sql.types import StructType, StructField, StringType


@udf('boolean')
def is_sword_purchase(event_as_json):
    event = json.loads(event_as_json)
    if event['event_type'] == 'purchase_sword':
        return True
    return False

@udf('boolean')
def is_shield_purchase(event_as_json):
    event = json.loads(event_as_json)
    if event['event_type'] == 'purchase_shield':
        return True
    return False

@udf('boolean')
def is_join_guild(event_as_json):
    event = json.loads(event_as_json)
    if event['event_type'] == 'join_guild':
        return True
    return False

def main():
    """main
    """
    spark = SparkSession \
        .builder \
        .appName("ExtractEventsJob") \
        .enableHiveSupport() \
        .getOrCreate()

    raw_events = spark \
        .read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "events") \
        .option("startingOffsets", "earliest") \
        .option("endingOffsets", "latest") \
        .load()
    
    raw_events.cache()
    sword_purchase_events = raw_events \
        .select(raw_events.value.cast('string').alias('raw'),
                raw_events.timestamp.cast('string')) \
        .filter(is_sword_purchase('raw'))

    extracted_sword_purchase_events = sword_purchase_events \
        .rdd \
        .map(lambda r: Row(timestamp=r.timestamp, **json.loads(r.raw))) \
        .toDF()
    extracted_sword_purchase_events.printSchema()
    extracted_sword_purchase_events.show()

    extracted_sword_purchase_events.registerTempTable("extracted_sword_purchase_events")

    spark.sql("""
        create external table if not exists sword_purchases
        stored as parquet
        location '/tmp/sword_purchases'
        as
        select * from extracted_sword_purchase_events
    """)
   
    shield_purchase_events = raw_events \
        .select(raw_events.value.cast('string').alias('raw'),
                raw_events.timestamp.cast('string')) \
        .filter(is_shield_purchase('raw'))

    extracted_shield_purchase_events = shield_purchase_events \
        .rdd \
        .map(lambda r: Row(timestamp=r.timestamp, **json.loads(r.raw))) \
        .toDF()
    extracted_shield_purchase_events.printSchema()
    extracted_shield_purchase_events.show()
    
    raw_events.printSchema()
    raw_events.show()
    
    extracted_shield_purchase_events.registerTempTable("extracted_shield_purchase_events")

    spark.sql("""
        create external table if not exists shield_purchases
        stored as parquet
        location '/tmp/shield_purchases'
        as
        select * from extracted_shield_purchase_events
    """)
    
    join_guild_events = raw_events \
        .select(raw_events.value.cast('string').alias('raw'),
                raw_events.timestamp.cast('string')) \
        .filter(is_join_guild('raw'))

    extracted_join_guild_events = join_guild_events \
        .rdd \
        .map(lambda r: Row(timestamp=r.timestamp, **json.loads(r.raw))) \
        .toDF()
    extracted_join_guild_events.printSchema()
    extracted_join_guild_events.show()

    extracted_join_guild_events.registerTempTable("extracted_join_guild_events")

    spark.sql("""
        create external table if not exists join_guilds
        stored as parquet
        location '/tmp/join_guilds'
        as
        select * from extracted_join_guild_events
    """)

if __name__ == "__main__":
    main()

```

**Run it**

```
docker-compose exec spark spark-submit /w205/project-3-ShuYingAmberChen/write_hive_table.py
```

**Check the tables have been written to HDFS**

```
docker-compose exec cloudera hadoop fs -ls /tmp/
```

**Start Presto to query data to answer business questions**

```
docker-compose exec presto presto --server presto:8080 --catalog hive --schema default
```

**Check all tables**
```
presto:default> show tables;
      Table       
 ------------------ 
 join_guilds      
 shield_purchases 
 sword_purchases  
(3 rows)

presto:default> describe join_guilds;
     Column     |  Type   | Comment 
----------------+---------+---------
 accept         | varchar |         
 content-length | varchar |         
 content-type   | varchar |         
 host           | varchar |         
 user-agent     | varchar |         
 attributes     | varchar |         
 event_type     | varchar |         
 timestamp      | varchar |         
(8 rows)

presto:default> describe sword_purchases;
     Column     |  Type   | Comment 
----------------+---------+---------
 accept         | varchar |         
 content-length | varchar |         
 content-type   | varchar |         
 host           | varchar |         
 user-agent     | varchar |         
 attributes     | varchar |         
 event_type     | varchar |         
 timestamp      | varchar |         
(8 rows)

presto:default> describe shield_purchases;
     Column     |  Type   | Comment 
----------------+---------+---------
 accept         | varchar |         
 content-length | varchar |         
 content-type   | varchar |         
 host           | varchar |         
 user-agent     | varchar |         
 attributes     | varchar |         
 event_type     | varchar |         
 timestamp      | varchar |         
(8 rows)
```

###Business Questions
**Question 1: How many join guild events are there? How many sword purchase events? And how many shield purchase events?**

```
presto:default> select count(*) from join_guilds;
 _col0 
-------
   100 
(1 row)

presto:default> select count(*) from sword_purchases;
 _col0 
-------
  1086 
(1 row)

presto:default> select count(*) from shield_purchases;
 _col0 
-------
   492 
(1 row)
```

**Question 2: How many users are in the test data?**
*Note that because of the algorithm of generating test data, every users performed all events, but different times. Therefore, all tables have same number of distinct hosts.

```
presto:default> select count(distinct host) from join_guilds;
 _col0 
-------
    60 
(1 row)
```

**Question 3: The ranking of the guilds by popularity**
```
presto:default> select attributes, count(host) as num_host from join_guilds group by attributes order by num_host desc
             -> ;
               attributes                | num_host 
-----------------------------------------+----------
 {"name": "Jaguar", "level": "3"}        |       27 
 {"name": "Tiger", "level": "4"}         |       21 
 {"name": "Pika", "level": "1"}          |       20 
 {"name": "Cheetah", "level": "2"}       |       16 
 {"name": "InvisibleLion", "level": "5"} |       16 
(5 rows)
```
* Answer: the most popular guild in the test data is Jaguar, which has almost 50% of players. Then, it's Tiger, Pika, Cheetah and InvisibleLion.

**Question 4: Which user purchased the most number of swords and shield in aggregate?**
```
presto:default> select distinct join_guilds.host, sword_table.num_swords, shield_table.num_shields, (sword_table.num_swords + shield_table.num_shields) as total_buy
             -> from join_guilds 
             -> left join (select host, count(event_type) as num_swords from sword_purchases group by host) as sword_table 
             -> on join_guilds.host = sword_table.host 
             -> left join (select host, count(event_type) as num_shields from shield_purchases group by host) as shield_table 
             -> on join_guilds.host = shield_table.host 
             -> group by join_guilds.host, sword_table.num_swords, shield_table.num_shields, sword_table.num_swords + shield_table.num_shields
             -> order by total_buy desc
             -> limit 1;
        host        | num_swords | num_shields | total_buy 
--------------------+------------+-------------+-----------
 user53.comcast.com |         74 |          31 |       105 
(1 row)
```

* Answer: User ID 53 purchased the most number of swords and shields. He/she purchased 74 swords, 31 shields

**Question 5: How many purchase events are there in the test dataset?**
```
presto:default> select sum(total_buy) from (
             -> select distinct join_guilds.host, sword_table.num_swords, shield_table.num_shields, (sword_table.num_swords + shield_table.num_shields) as total_buy
             -> from join_guilds 
             -> left join (select host, count(event_type) as num_swords from sword_purchases group by host) as sword_table 
             -> on join_guilds.host = sword_table.host 
             -> left join (select host, count(event_type) as num_shields from shield_purchases group by host) as shield_table 
             -> on join_guilds.host = shield_table.host 
             -> group by join_guilds.host, sword_table.num_swords, shield_table.num_shields, sword_table.num_swords + shield_table.num_shields
             -> order by total_buy);
 _col0 
-------
  1578 
(1 row)
```

* Answer: there are total 1578 purchase events in the dataset.


**Tear down the cluster**

```
  docker-compose down
```
