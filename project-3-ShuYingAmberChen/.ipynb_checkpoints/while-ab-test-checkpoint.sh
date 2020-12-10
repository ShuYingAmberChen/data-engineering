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
  sleep 5
done