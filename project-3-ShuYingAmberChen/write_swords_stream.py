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
