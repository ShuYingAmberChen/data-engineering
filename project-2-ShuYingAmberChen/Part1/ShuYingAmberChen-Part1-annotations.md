# W205 Project 2 Tracking User Activities - Part 1
## Author: Shu Ying (Amber) Chen

**First of all, create a working directory.**

223  git clone https://github.com/mids-w205-schioberg/project-2-ShuYingAmberChen.git

224  mv project-2-ShuYingAmberChen w205/

225  git branch assignment

226  cd w205/project-2-ShuYingAmberChen/

227  git branch assignment

228  git checkout branch

229  git checkout assignment

230  git branch


**Get the data**

233  curl -L -o assessment-attempts-20180128-121051-nested.json https://goo.gl/ME6hjp

**Copy docker-compose.yml from week 6 lecture**

236  cp ../course-content/06-Transforming-Data/docker-compose.yml docker-compose.yml

**Spin up and check the cluster**

237  docker-compose up -d

238  docker-compose ps

**Check zookeeper**

240  docker-compose logs zookeeper | grep -i binding

**Check the kafka broker**

241  docker-compose logs kafka | grep -i started

**Check out the messages**

247  docker-compose exec mids bash -c "cat /w205/project-2-ShuYingAmberChen/assessment-attempts-20180128-121051-nested.json"

248  docker-compose exec mids bash -c "cat /w205/project-2-ShuYingAmberChen/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c"

**Get the length of the messages. Total 3280 messages.**

251  docker-compose exec mids bash -c "cat /w205/project-2-ShuYingAmberChen/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c | wc -l"

**Create a topic called EdTechAssessment2, and check the topic**

289  docker-compose exec kafka kafka-topics --create --topic EdTechAssessment2 --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181

290  docker-compose exec kafka kafka-topics --describe --topic EdTechAssessment2 --zookeeper zookeeper:32181

**Publish the messages**

292  docker-compose exec mids bash -c "cat /w205/project-2-ShuYingAmberChen/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c | kafkacat -P -b kafka:29092 -t EdTechAssessment2 && echo 'Produced all messages.'"

**Consume the messages**

294  docker-compose exec mids bash -c "kafkacat -C -b kafka:29092 -t EdTechAssessment2 -o beginning -e"

295  docker-compose exec mids bash -c "kafkacat -C -b kafka:29092 -t EdTechAssessment2 -o beginning -e" | wc -l

**Shut down the cluster and save the terminal history**

296  docker-compose down

297  history > ShuYingAmberChen-history.txt 