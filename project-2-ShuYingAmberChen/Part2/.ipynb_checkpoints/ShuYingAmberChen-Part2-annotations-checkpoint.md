# W205 Project 2 Tracking User Activities - Part 2
## Author: Shu Ying (Amber) Chen

**First of all, create a sub directory within my workspace for part 2**

  490  cd w205/project-2-ShuYingAmberChen/Part2

**Copy docker-compose.yml from week 8 lecture**

  520  cp ~/w205/course-content/08-Querying-Data/docker-compose.yml .

**Update the part of code for PySpark within docker-compose.yml**

  523  vim docker-compose.yml
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

  cloudera:
    image: midsw205/cdh-minimal:latest
    expose:
      - "8020" # nn
      - "50070" # nn http
      - "8888" # hue
    #ports:
    #- "8888:8888"
    
  spark:
    image: midsw205/spark-python:0.0.5
    stdin_open: true
    tty: true
    volumes:
      - ~/w205:/w205
    command: bash
    depends_on:
      - cloudera
    environment:
      HADOOP_NAMENODE: cloudera
    ports: 
      - "8888:8888"

  mids:
    image: midsw205/base:latest
    stdin_open: true
    tty: true
    volumes:
      - ~/w205:/w205
 ```


**Spin up the cluster**

  524  docker-compose up -d

**Check the kafka broker**
  
  525  docker-compose logs -f kafka

  **Create a topic called eduAssessment, and check the topic**
  
  527  docker-compose exec kafka kafka-topics --create --topic eduAssessment --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181
 
  528  docker-compose exec kafka kafka-topics --describe --topic eduAssessment --zookeeper zookeeper:32181

**Check out the messages**

  529  docker-compose exec mids bash -c "cat /w205/project-2-ShuYingAmberChen/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c"

**Get the length of the messages. Total 3280 messages.**

  530  docker-compose exec mids bash -c "cat /w205/project-2-ShuYingAmberChen/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c | wc -l"

**Publish the messages to that topic with kafkacat**

  531  docker-compose exec mids bash -c "cat /w205/project-2-ShuYingAmberChen/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c | kafkacat -P -b kafka:29092 -t eduAssessment && echo 'Produced 3280 messages.'"

**Open a PySpark Notebook**

  532  docker-compose exec spark env PYSPARK_DRIVER_PYTHON=jupyter PYSPARK_DRIVER_PYTHON_OPTS='notebook --no-browser --port 8888 --ip 0.0.0.0 --allow-root' pyspark

**Transform the data in [PySpark Notebook](w205/project-2-ShuYingAmberChen/Part2/Part2-PySpark.ipynb)

**Copy the Notebook from the container to the host**

  533  docker ps

  535  docker cp e71cfcc69a85:/spark-2.2.0-bin-hadoop2.6/Part2-PySpark.ipynb ~/w205/project-2-ShuYingAmberChen/Part2/.

**Shut down the cluster and save the terminal history**

  536  docker-compose down
  
  537  history > ShuYingAmberChen-history.txt