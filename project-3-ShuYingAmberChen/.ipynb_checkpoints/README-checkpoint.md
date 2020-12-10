# Project 3: Understanding User Behavior
## Author: Shu Ying (Amber) Chen

## Objective

As a data engineer at a game development company, I have created a data pipeline to track users' `buy a sword`, `buy a shield` and `join guild` events and to allow my team to do further analysis on live data. In addition, I have conducted data analysis within Presto on the test dataset and presented a recommendation based on my data analysis.


## Details of tasks

- Instrument the API server to log events to Kafka

- Enhance the API to use additional http verbs (`POST`) to get metadata characteristics of each events

- Assemble a data pipeline to catch `buy a sword`, `buy a shield` and `join guild` events: use Spark streaming to filter
  select event types from Kafka, land them into HDFS/parquet to make them
  available for analysis using Presto
  
- The data pipeline captures metadata characteristics of all events: name and level of each guild, sword and shield

- Use Apache Bench to generate test data for the pipeline

- The final report includes a full description of the pipeline and the analysis of events in the test dataset
  [annotated Markdown file](Project-3-ShuYingAmberChen-annotations.md)

## Business Analysis

**Question 1: how many join guild events are there? How many sword purchase events? And how many shield purchase events?**
  * Answer: There are 100 join guild events, 1086 sword purchase events and 492 shield purchase events.

**Question 2: How many users are in the test data?**
  * Answer: The test data has 60 users.

**Question 3: The ranking of the guilds by popularity**

```
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
  * Answer: User ID 53 purchased the most number of swords and shields. He/she purchased 74 swords, 31 shields
  
**Question 5: How many purchase events are there in the test dataset?**
  * Answer: there are total 1578 purchase events in the dataset.
  
## Recommendations

- Based on above analysis, we discovered that there are 60 users and 100 join guild events. Clearly, some users quit current guilds and join other guilds, and there are competitions among guilds to attract users and win popularity. We can bring some occasional events into the game to create some competition events such as team battles to stimulate guilds to compete with each other, and thus to increase diversity of user playing experience and to motivate users to create new guilds. This should ultimately benefit us from increasing user stickiness to the game.

- From question 4 and 5, we can see that users purchase in total 1578 items and about 26 items on average. The highest number of purchase event for a person is 74 swords and 31 shields. We can bring more types of items and/or special holiday theme items during holidays (e.g sell limited edition outfits, swords and shields that fit Christmas theme during Christmas season). This should stimulate user to spend money to get more coins in the game to purchase more items. This, along with the first recommendation, should motivate users' purchasing desire, and hence generate higher revenues to our company.
