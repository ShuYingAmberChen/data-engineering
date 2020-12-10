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

