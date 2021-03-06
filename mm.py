#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask
import requests
import json
import socket
import threading
from datetime import datetime, timedelta
m = []
ferma = []  # массив ип-адресов ригов
power_full = hashrate_full = fullpower = power = hashrate = temp_max = 0
result_html = ''
temp_min = 100
hashrate_alert = 730000000
t_max_alert = 75
t_min_alert = 30
d_coin = d_unpaid = d_usd = d_validShares = d_staleShares = d_invalidShares = 0
count = 0
rig_hashrate = {}
rig_power = {}
rig_efficiency = {}
rig_uptime = {}
rig_restart = {}

f = open('ip.txt')
for line in f:
    ferma.append(line.rstrip())
f.close()


def run_eth_timer():
    threading.Timer(600, run_eth_timer).start()
    run_eth()


def run_eth():
    global d_unpaid, d_coin, d_usd, d_validShares, d_staleShares, d_invalidShares
    try:
        r = requests.get('https://api.ethermine.org/miner/fd85081868b0c380ffff66b2dd1c299ee95c09c1/currentStats')
        d_unpaid = r.json()['data']['unpaid'] / 1000000000000000000
        d_coin = r.json()['data']['coinsPerMin'] * 60 * 24
        d_usd = r.json()['data']['usdPerMin'] * 60 * 24
        d_validShares = r.json()['data']['validShares']
        d_staleShares = r.json()['data']['staleShares']
        d_invalidShares = r.json()['data']['invalidShares']
    except Exception:
        print('except api ethermine')


def run_timer():
    threading.Timer(600, run_timer).start()
    run()


def run():
    m.clear()
    global result_html, hashrate_full, power_full, temp_max, temp_min
    trex_table = rig_br_str = rig_str = ''
    power_full = hashrate_full = temp_max = 0
    temp_min = 100
    except_connect = ''
    for ip in ferma:
        rig_hashrate[ip] = rig_efficiency[ip] = rig_power[ip] = rig_power[ip] = 1
        try:
            r = requests.get('http://' + ip + ':4067/summary', timeout=2)
            if r.status_code == 200:
                trex_table += get_json_trex(ip, r.json())
        except Exception:
            except_connect += 'except: ' + ip + '\n'
            print("except: " + ip)
            continue
        rig_str += ip + '=' + str('%.1f' % (rig_hashrate[ip] / 1000000)) + '\n'
        rig_br_str += '<tr><td>' + ip + '</td><td>' + str('%.1f' % (rig_hashrate[ip] / 1000000)) + '</td><td>' + \
            str(rig_efficiency[ip]) + '</td><td>' + str(rig_power[ip] / 1000) + '</td><td>' + \
            rig_uptime[ip] + '</td><td>' + rig_restart[ip] + '</td></tr>'

    q = 'Sped=' + str('%.1f' % (hashrate_full / 1000000)) + ' Power=' + str(power_full / 1000) + \
        ' Tmax=' + str(temp_max) + ' Tmin=' + str(temp_min)  # +'\n'
    qq = 'unpaid=' + str(d_unpaid)[:5] + ' coin=' + str(d_coin)[:5] + ' usd=' + str(d_usd)[:5] + '\n'
    qqq = 'validShares=' + str(d_validShares) + ' staleShares=' + str(d_staleShares) + ' invalidShares=' + str(d_invalidShares) + '\n'
    # сборка web страницы index.html
    html = '<html><body style="background-color:#111111;color:#ffffff;font-weight:bold;">'
    html += '<style type="text/css">tr:nth-child(odd) { background-color: #252525; } tr:nth-child(even) { background-color: #111111; }</style>'
    html += '<p>' + str(datetime.today()) + '</p><p>' + q + '</p><p>' + qq + '</p><p>' + qqq + '</p>'
    html += '<p><table border=1><tr><td width=100px>IP</td><td>hashrate</td><td>kH/W</td><td>power</td><td>uptime</td><td>rst</td></tr>' + rig_br_str + '</table></p>'
    html += '<p><table border=1 style="font-weight: left;"></p>'
    html += '<tr><td width=100px>IP</td><td width=100px>Name</td><td>hashrate</td><td>kH/W</td><td>power</td><td>temp</td><td>fan</td></tr>'
    html += trex_table + '</table>'

    result_html = html

    if hashrate_full < hashrate_alert or temp_max > t_max_alert or temp_min < t_min_alert:
        send_telegram(q + '\n' + rig_str + '\n' + except_connect + '\n')


def get_json_trex(ip, j):
    global hashrate_full, power_full, temp_max, temp_min
    html = ''
    for i in j['gpus']:
        name = i['name']
        hashrate = i['hashrate']
        efficiency = i['efficiency']
        power = i['power']
        temperature = i['temperature']
        fan_speed = i['fan_speed']
        html += '<tr><td>' + ip + '</td><td>' + name + '</td><td>' + str('%.1f' % (hashrate / 1000000)) + \
            '</td><td>' + str(efficiency.replace('kH/W', '')) + '</td><td>' + str(power) + \
            '</td><td>' + str(temperature) + '</td><td>' + str(fan_speed) + '</td></tr>'
        if temperature > temp_max:
            temp_max = temperature
        elif temperature < temp_min:
            temp_min = temperature
        power_full += power
        hashrate_full += hashrate
        rig_hashrate[ip] += hashrate
        rig_efficiency[ip] += int(efficiency.replace('kH/W', ''))
        rig_power[ip] += power
    try:
        rig_uptime[ip] = str(timedelta(seconds=j['watchdog_stat']['uptime']))
        rig_restart[ip] = str(j['watchdog_stat']['total_restarts'])
    except Exception:
        rig_uptime[ip] = 1
        rig_restart[ip] = 0
    return html


def run_claymore():
    m.clear()
    global fullpower, power, hashrate, temp_max, temp_min, result_html, count
    fullpower = power = hashrate = temp_max = 0
    temp_min = 100
    claymore_table = ''
    rig_str = rig_br_str = ''

    for x in ferma:  # claymore опрашиваем api удаленных майнеров через сокет
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s = socket.socket()
        rig_hashrate[x] = 0
        try:
            s.connect((x, 3333))
            s.send(
                '{"id":0,"jsonrpc":"2.0","method":"miner_getstat2"}'.encode("utf-8"))
            data = s.recv(2048)
            if not data:
                send_telegram('no data ' + x)
                print("nodata " + x)
                break
            s.close()
            r = json.loads(data.decode("utf-8"))
            claymore_table += get_json_claymore(x, r)
            rig_str += x + '=' + str(rig_hashrate[x]) + '\n'
            rig_br_str += '<tr><td>' + x + '</td><td>' + str(rig_hashrate[x]) + '</td></tr>'
        except TimeoutError:
            send_telegram('connection timeout ' + x)
            print("connection timeout " + x)
        except ConnectionRefusedError:
            send_telegram('connection refused ' + x)
            print("connection refused " + x)
        except Exception:
            send_telegram('except ' + x)
            print("exception claymore " + x)

    q = 'Sped=' + str(hashrate) + ' Power=' + str(fullpower) + \
        ' Tmax=' + str(temp_max) + ' Tmin=' + str(temp_min)  # +'\n'
    qq = 'unpaid=' + str(d_unpaid)[:5] + ' coin=' + str(d_coin)[:5] + ' usd=' + str(d_usd)[:5] + '\n'
    # сборка web страницы index.html
    html = '<html><body style="background-color:#111111;color:#ffffff;font-weight:bold;">'
    html += '<style type="text/css">tr:nth-child(odd) { background-color: #252525; } tr:nth-child(even) { background-color: #111111; }</style>'
    html += '<p>' + str(datetime.today()) + '</p><p>' + q + '</p><p>' + qq + '</p>'
    html += '<p><table border=1>' + rig_br_str + '</table></p>'

    # сборка таблицы от claymore
    html += '<table border=1 style="font-weight: left;">'
    html += '<tr><td>IPaddr</td><td>Hash</td><td>Temp</td><td>Cooler</td></tr>'
    html += claymore_table + '</table>'

    result_html = html

    if hashrate < hashrate_alert or temp_max > t_max_alert or temp_min < t_min_alert:  # for claymore ETH
        send_telegram(q + '\n' + rig_str)


# claymore перебор данных json взятыми из api майнеров и подготовка к выводу
def get_json_claymore(xx, r):
    global hashrate, fullpower, temp_max, temp_min
    hashr = temp = cooler = 0
    rr = ''
    m3 = r['result'][3].split(';')
    m6 = r['result'][6].split(';')
    fullpower += int(r['result'][17])
    # print(xx+' '+str(datetime.today()))
    for x in range(len(m3)):
        hashr = m3[::][x]
        temp = m6[::2][x]
        cooler = m6[1::2][x]
        rr += '<tr>'
        rr += '<td>' + xx + '</td><td>' + hashr + '</td><td>' + temp + '</td><td>' + cooler + '</td>'
        rr += '</tr>'
        hashrate += int(hashr)
        rig_hashrate[xx] += int(hashr)
        if int(temp) > temp_max:
            temp_max = int(temp)
        elif int(temp) < temp_min:
            temp_min = int(temp)
        # print(str(x)+' '+hashr+' '+temp+' '+cooler)
    return rr


def send_telegram(p1):
    bot_token = '1449777708:AAHV6KJaAXq0qEw1X6X01aHGFAlBwrxSlAo'  # aipstd_bot
    bot_chatID = '345075073'
    send_text = 'https://api.telegram.org/bot' + bot_token + \
        '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + p1
    response = requests.get(send_text)
    return response.json()


app = Flask(__name__)


@app.route("/")
def hello():
    run()
    return result_html


if __name__ == '__main__':
    run_eth_timer()
    run_timer()
    app.run(host='0.0.0.0', port=8008)
