import requests
import configparser
from threading import Timer
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
m = []
pp=ss=ttmax=0
ttmin=100
def run():
    Timer(600, run).start ()
    m.clear()
    global pp,ss,ttmax,ttmin
    pp=ss=ttmax=0
    ttmin=100
    try:
        r = requests.get('http://192.168.1.2:42000/getstat', timeout=(3))
        add_array ('s1',r,2)
    except requests.exceptions.ReadTimeout:
        exit
    except requests.exceptions.ConnectTimeout:
        exit
    try:
        r = requests.get('http://192.168.1.3:42000/getstat', timeout=(3))
        add_array ('s2',r,5)
    except requests.exceptions.ReadTimeout:
        exit
    except requests.exceptions.ConnectTimeout:
        exit
    try:
        r = requests.get('http://192.168.1.7:42000/getstat', timeout=(3))
        add_array ('s3',r,6)
    except requests.exceptions.ReadTimeout:
        exit
    except requests.exceptions.ConnectTimeout:
        exit
    print (sh())
    if (pp < 1500 or ss < 475 or ttmax > 73 or ttmin < 40):
        send_mail(sh())

def add_array(j,r,n):
    global pp,ss,ttmax,ttmin
    for i in range(n):
        t = r.json()['result'][i]['temperature']
        p = r.json()['result'][i]['gpu_power_usage']
        s = r.json()['result'][i]['speed_sps']
        acs = r.json()['result'][i]['accepted_shares']
        rjs = r.json()['result'][i]['rejected_shares']
        if t > ttmax:
            ttmax = t
        elif t < ttmin:
            ttmin = t
        pp+=p
        ss+=s
        m.append([j,t,p,s,acs,rjs])

def sh():
    q='Power='+str(pp) + ' Sped='+str(ss) + ' Tmax='+str(ttmax) + ' Tmin='+str(ttmin) + '\n'
    qq='<html><body style="background-color:#111111;color:#ffffff;font-weight:bold;"><p>'+str(datetime.today())+'</p><p>'+q+'</p><table border=1 style="font-weight: bold;">'
    qq+='<tr><td>Farm</td><td>Temp</td><td>Power</td><td>Hash</td><td>Ac</td><td>Rj</td></tr>'
    for row in m:
        qq+='<tr>'
        for elem in row:
            q += str(elem) + ' '
            qq+='<td>'+str(elem)+'</td>'
        q+='\n'
        qq+='</tr>'
    qq+='</table></body></html>'
    f = open('index.html', 'w')
    f.write(qq)
    f.close()
    print (datetime.today())
    return q

def send_mail(q):
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8-sig')
    msg = MIMEMultipart()
    msg['From'] = "aipstudio@mail.ru"
    msg['To'] = "aipstudion@mail.ru"
    msg['Subject'] = "Warning Mining"
    body = q
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
    server.login(username, password)
    text = msg.as_string()
    server.sendmail("aipstudio@mail.ru", "aipstudio@mail.ru", text)
    server.quit()

run()
