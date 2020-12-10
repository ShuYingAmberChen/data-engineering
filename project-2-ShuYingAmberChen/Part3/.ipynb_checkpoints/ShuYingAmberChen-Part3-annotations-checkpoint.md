 # W205 Project 2 Tracking User Activities - Part3
## Author: Shu Ying (Amber) Chen

**First of all, create a sub directory within my workspace for part 3**

  426  mkdir Part3
  
  569  cd Part3

**Use the same docker-compose.yml from Part 2**

  570  cp ~/w205/project-2-ShuYingAmberChen/Part2/docker-compose.yml .

**Spin up and check the cluster**

  571  docker-compose up -d
  572  docker-compose ps
  
**Check the kafka broker**

  573  docker-compose logs -f kafka

  **Create a topic called eduAssessment, and check the topic**

  574  docker-compose exec kafka kafka-topics --create --topic eduAssessment --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181
  
  575  docker-compose exec kafka kafka-topics --describe --topic eduAssessment --zookeeper zookeeper:32181

**Check out the messages**

  576  docker-compose exec mids bash -c "cat /w205/project-2-ShuYingAmberChen/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c"

**Get the length of the messages. Total 3280 messages.**

  577  docker-compose exec mids bash -c "cat /w205/project-2-ShuYingAmberChen/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c | wc -l"

**Publish the messages to that topic with kafkacat**

  578  docker-compose exec mids bash -c "cat /w205/project-2-ShuYingAmberChen/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c | kafkacat -P -b kafka:29092 -t eduAssessment && echo 'Produced 3280 messages.'"

**Open a PySpark Notebook**

  579  docker-compose exec spark env PYSPARK_DRIVER_PYTHON=jupyter PYSPARK_DRIVER_PYTHON_OPTS='notebook --no-browser --port 8888 --ip 0.0.0.0 --allow-root' pyspark

**Transform the data, land it in HDFS and answer business questions in [PySpark Notebook](w205/project-2-ShuYingAmberChen/Part3/Part3-PySpark.ipynb)

**After writing the messages in PySpark Notebook in hdfs, check out the results in the second terminal**

  567  cd w205/project-2-ShuYingAmberChen/Part3

  568  docker-compose exec cloudera hadoop fs -ls /tmp/
  
  ```
  Found 3 items
drwxrwxrwt   - mapred mapred              0 2018-02-06 18:27 /tmp/hadoop-yarn
drwx-wx-wx   - root   supergroup          0 2020-07-05 16:55 /tmp/hive
drwxr-xr-x   - root   supergroup          0 2020-07-05 17:09 /tmp/messages
  ```
  
  569  docker-compose exec cloudera hadoop fs -ls /tmp/messages
  ```
  Found 2 items
-rw-r--r--   1 root supergroup          0 2020-07-05 17:09 /tmp/messages/_SUCCESS
-rw-r--r--   1 root supergroup    2513397 2020-07-05 17:09 /tmp/messages/part-00000-201c589b-3700-44e6-967d-49a9ffca4e11-c000.snappy.parquet
 ```
 **Confirm the raw data have been saved in hdfs**
 
**After writing the extracted messages in PySpark Notebook in hdfs, check out the results in the second terminal**

  570  docker-compose exec cloudera hadoop fs -ls /tmp/
  
  572  docker-compose exec cloudera hadoop fs -ls /tmp/extracted_message

 **Confirm extracted version of the data have been saved in hdfs**

**Copy the Notebook from the container to the host (history from the second terminal)**

  563  docker ps
  
  564  docker cp 4102e3d9e5d1:/spark-2.2.0-bin-hadoop2.6/Part3-PySpark.ipynb ~/w205/project-2-ShuYingAmberChen/Part3/.
  
**Shut down the cluster and save the terminal history**

  565  docker-compose down

  566  history > ShuYingAmberChen-history.txt
  
  573  history > ShuYingAmberChen-terminal2-history.txt