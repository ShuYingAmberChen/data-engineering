# Project 2: Tracking User Activity
## Author: Shu Ying (Amber) Chen

## Objective

As a data engineer in the ed tech firm, I have created a service that deliver assessments. Now lots of different customers (e.g., Pearson) want
to publish their assessments on it. I completed this project to build an infrastructure to land the assessment data in a structured form and have it ready for data scientists to run queries on the data.


## Data

```
curl -L -o assessment-attempts-20180128-121051-nested.json https://goo.gl/ME6hjp`
```


## Structure of the Task

I have completed the project in three steps:

    1. Publish and consume messages with Kafka
    2. Use Spark to transform the messages, and
    3. Use Spark to transform the messages so that you can land them in HDFS

[An example of the docker-compose.yml files](w205/project-2-ShuYingAmberChen/Part3/docker-compose.yml)

Final Report: [Annotated Markdown file](w205/project-2-ShuYingAmberChen/Part3/ShuYingAmberChen-Part3-annotations.md)

Step 1 [annotated Markdown file](w205/project-2-ShuYingAmberChen/Part1/ShuYingAmberChen-Part1-annotations.md)

Part 2 [annotated Markdown file](w205/project-2-ShuYingAmberChen/Part2/ShuYingAmberChen-Part2-annotations.md)

Part 3 (Also the final report) [annotated Markdown file](w205/project-2-ShuYingAmberChen/Part3/ShuYingAmberChen-Part3-annotations.md)


## Further Analysis

Finally, I have conducted a preliminary analysis of the assessment data by querying the data using SparkSQL and answering three business questions which I believe data scientists might be interested to know.

The questions are:

    1. How many assessments are in the dataset?
    2. What are the 10 most popular courses and the 10 least popular courses? And how many times they have been taken?
    3. How many users are loyal customers and have taken more than 1 assessment?
    
The analysis is saved in the final report.

