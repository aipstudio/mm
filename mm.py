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

f = open('ip.txt')
for line in f:
    ferma.append(line.rstrip())
f.close()

def run_loop():
    threading.Timer(600, run).start()
    run()

def run():
    #threading.Timer(600, run).start()
    m.clear()
    global fullpower, power, hashrate, temp_max, temp_min, result_html
    fullpower = power = hashrate = temp_max = 0
    temp_min = 100
    claymore_table = xml_table = ''

    # for x in ferma: #ewbf опрашиваем api удаленных майнеров через get
    #    try:
    #        r = requests.get('http://'+x+':42000/getstat', timeout=(1))
    #        add_array (x,r,len(r.json()["result"]))
    #    except requests.exceptions.RequestException:
    #        send_mail('no connect '+x)
    #        print("exception ewbf")

    for x in ferma:  # claymore опрашиваем api удаленных майнеров через сокет
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((x, 3333))
            s.send(
                '{"id":0,"jsonrpc":"2.0","method":"miner_getstat2"}'.encode("utf-8"))
            j = s.recv(2048)
            s.close()
            r = json.loads(j.decode("utf-8"))
            claymore_table += get_json_claymore(x, r)
        except:
            send_discord('no connect '+x)
            print("exception claymore")

    # q='Power='+str(power) + ' Sped='+str(hashrate) + ' Tmax='+str(temp_max) + ' Tmin='+str(temp_min) + '\n'
    q = 'Sped='+str(hashrate)+' Power='+str(fullpower) + \
        ' Tmax='+str(temp_max) + ' Tmin='+str(temp_min)+'\n'
    #print(datetime.today())
    #print(q)

    # сборка web страницы index.html
    html = '<html><body style="background-color:#111111;color:#ffffff;font-weight:bold;">'
    html += '<style type="text/css">tr:nth-child(odd) { background-color: #252525; } tr:nth-child(even) { background-color: #111111; }</style>'
    html += '<p>'+str(datetime.today())+'</p><p>'+q+'</p>'

    # сборка таблицы от ewbf
    # html+='<table border=1 style="font-weight: bold;float:left;">'
    # html+='<tr><td>IPaddr</td><td>Temp</td><td>Power</td><td>Hash</td><td>Ac</td><td>Rj</td></tr>'
    # html+=get_array_json()+'</table>'

    # сборка таблицы от claymore
    html += '<table border=1 style="font-weight: bold;float:left;">'
    html += '<tr><td>IPaddr</td><td>Hash</td><td>Temp</td><td>Cooler</td></tr>'
    html += claymore_table+'</table>'

    # сборка таблицы от xml file nvidi-smi
    # html += '<table border=1 style="font-weight: bold;float:left"><tr><td>Name</td><td>Cooler</td><td>CPU</td><td>MEM</td><td>Temp</td><td>Watt</td><td>GPU Clock</td><td>MEM Clock</td><td>VIDEO Clock</td></tr>'
    # for x in ferma:  # собираем данные из файлов *.xml
    #     if os.path.isfile(x+'.xml'):
    #         xml_table += get_ps_xml(x+'.xml')
    # html += xml_table+'</table>'
    # html += '</body></html>'

    # f = open('index.html', 'w')
    # f.write(html)
    # f.close()

    result_html = html

    if hashrate < 370000 or temp_max > 75 or temp_min < 40:  # for claymore ETH
        send_discord(q)

def add_array(j, r, n):  # ewbf наполнение массива элементами взятыми из api json майнеров
    global power, hashrate, temp_max, temp_min
    for i in range(n):
        t = r.json()['result'][i]['temperature']
        p = r.json()['result'][i]['gpu_power_usage']
        s = r.json()['result'][i]['speed_sps']
        acs = r.json()['result'][i]['accepted_shares']
        rjs = r.json()['result'][i]['rejected_shares']
        if t > temp_max:
            temp_max = t
        elif t < temp_min:
            temp_min = t
        power += p
        hashrate += s
        m.append([j, t, p, s, acs, rjs])


def get_array_json():  # ewbf перебор массива с данными взятыми из api майнеров и подготовка к выводу
    rr = r = ''
    for row in m:
        rr += '<tr>'
        for elem in row:
            r += str(elem) + ' '
            rr += '<td>'+str(elem)+'</td>'
        r += '\n'
        rr += '</tr>'
    #print(r)
    return rr


# claymore перебор данных json взятыми из api майнеров и подготовка к выводу
def get_json_claymore(xx, r):
    global hashrate, fullpower, temp_max, temp_min, hashr, temp, cooler
    rr = ''
    m3 = r['result'][3].split(';')
    m6 = r['result'][6].split(';')
    fullpower += int(r['result'][17])
    for x in range(len(m3)):
        hashr = m3[::][x]
        temp = m6[::2][x]
        cooler = m6[1::2][x]
        rr += '<tr>'
        rr += '<td>'+xx+'</td><td>'+hashr+'</td><td>'+temp+'</td><td>'+cooler+'</td>'
        rr += '</tr>'
        hashrate += int(hashr)
        if int(temp) > temp_max:
            temp_max = int(temp)
        elif int(temp) < temp_min:
            temp_min = int(temp)
        #print(hashr+' '+temp+' '+cooler)
    return rr


def get_ps_xml_file():
    threading.Timer(600, get_ps_xml_file).start()
    r = os.system(
        "powershell -NoProfile -ExecutionPolicy ByPass -file mm_gg.ps1")
    if r != 0:
        send_discord('Fucking powershell ERROR')

def get_ps_xml(p1):  # перебор элементов в xml файлах(файлы получены через powershell 5.1 через сесиию) и подготовка к выводу
    tree = ET.parse(p1)
    root = tree.getroot()
    driver_version = root.find('driver_version')
    rr = r = ''
    for gpu in root.findall('gpu'):
        product_name = gpu.find('product_name').text
        fan_speed = gpu.find('fan_speed').text
        for util in gpu.findall('utilization'):
            gpu_util = util.find('gpu_util').text
            memory_util = util.find('memory_util').text
        for temp in gpu.findall('temperature'):
            gpu_temp = temp.find('gpu_temp').text
        for power in gpu.findall('power_readings'):
            power_draw = power.find('power_draw').text
        for clocks in gpu.findall('clocks'):
            graphics_clock = clocks.find('graphics_clock').text
            mem_clock = clocks.find('mem_clock').text
            video_clock = clocks.find('video_clock').text
        r += product_name+' '+fan_speed+' '+gpu_util+' '+memory_util+' '+gpu_temp+' '
        r += power_draw+' '+graphics_clock+' '
        r += mem_clock+' '+video_clock+'\n'
        rr += '<tr><td>'+product_name+'</td><td>' + \
            fan_speed+'</td><td>'+gpu_util+'</td><td>'
        rr += memory_util+'</td><td>'+gpu_temp+'</td><td>'+power_draw+'</td><td>'
        rr += graphics_clock+'</td><td>'+mem_clock+'</td><td>'+video_clock+'</td></tr>'
    #print(r)
    return rr


def send_discord(p1):
    HOOK = 'https://discord.com/api/webhooks/713946771360841840/j_nyVu1KBYZdP5RiYaTfXuAy66mIh9UDeW4gajpaTCmPkNjLLle5JHSuBRonW7kk7lmR'
    MESSAGE = {
        'embeds': [
            {
                'color': 11500000,
                'title': 'Warning Mining',
                'fields': [
                    {
                        'name': 'Miner monitor',
                        'value': p1,
                        'inline': True
                    }
                ]
            }
        ]
    }

    requests.post(HOOK, json=MESSAGE).text


app = Flask(__name__)
@app.route("/")
def hello():
    run()
    return result_html


if __name__ == '__main__':
    #get_ps_xml_file()
    run_loop()
    app.run(host='0.0.0.0', port=8008)
