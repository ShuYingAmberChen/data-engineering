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
        Read parquets from what were written into HDFS
        Register temp tables
        Create external tables for all events and store as parquets
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
