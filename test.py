#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask
import requests
import configparser
import os
import json
import socket
import xml.etree.ElementTree as ET
import threading
from datetime import datetime
m = []  # массив для ewbf
ferma = []  # массив ип-адресов ригов
fullpower = power = hashrate = temp_max = 0
result_html = ''
temp_min = 100
hashrate_alert = 365000
t_max_alert = 80
t_min_alert = 40
d_coin = d_unpaid = d_usd = 0
count = 0

def run2():
    global html 
    html = ''
    ip = '192.168.1.34'
    r = requests.get('http://'+ip+':4067/summary')
    get_json_trex(ip,r.json())

def get_json_trex(ip,j):
    global html
    html += '<tr><td>Name</td><td>hashrate</td><td>efficiency</td><td>power</td><td>temperature</td><td>fan_speed</td></tr>'
    for i in j['gpus']:
        name = i['name']
        hashrate = i['hashrate']
        efficiency = i['efficiency']
        power = i['power']
        temperature = i['temperature']
        fan_speed = i['fan_speed']
        html += '<tr><td>' + name + '</td><td>' + str(hashrate) + '</td><td>' + str(efficiency) + \
        '</td><td>' + str(power) + '</td><td>' + str(temperature) + '</td><td>' + str(fan_speed) + '</td><tr>'
    html += ''
    print (html)

if __name__ == '__main__':
    run2()

