import requests, configparser,os,smtplib
import xml.etree.ElementTree as ET
from threading import Timer
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
m=[]
gg=''
pp=ss=ttmax=0
ttmin=100
def run():
    Timer(600, run).start ()
    m.clear()
    global pp,ss,ttmax,ttmin,gg
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
    os.system("powershell -NoProfile -ExecutionPolicy ByPass -file mm_gg.ps1")
    gg='<table border=1 style="font-weight: bold;">'+get_ps_xml('192.168.1.2.xml')+get_ps_xml('192.168.1.3.xml')+get_ps_xml('192.168.1.7.xml')+'</table>'
    print (sh())
    if pp < 1600 or ss < 570 or ttmax > 73 or ttmin < 40:
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
    global gg
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
    qq+='</table>'+gg
    qq+='</body></html>'
    f = open('index.html', 'w')
    f.write(qq)
    f.close()
    print (datetime.today())
    return q

def send_mail(q):
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8-sig')
    email_login = config.get('mail', 'username')
    email_pass = config.get('mail', 'password')
    email_to = config.get('mail', 'email_to')
    msg = MIMEMultipart()
    msg['From'] = email_login
    msg['To'] = email_to
    msg['Subject'] = "Warning Mining"
    body = q
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
    server.login(email_login, email_pass)
    text = msg.as_string()
    server.sendmail(email_login, email_to, text)
    server.quit()

def get_ps_xml(q):
    tree = ET.parse(q)
    root = tree.getroot()
    driver_version = root.find('driver_version')
    r=''
    rr=''
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
        r+=product_name+' '+fan_speed+' '+gpu_util+' '+memory_util+' '+gpu_temp+' '
        r+=power_draw+' '+graphics_clock+' '
        r+=mem_clock+' '+video_clock+'\n'
        rr+='<tr><td>'+product_name+'</td><td>'+fan_speed+'</td><td>'+gpu_util+'</td><td>'
        rr+=memory_util+'</td><td>'+gpu_temp+'</td><td>'+power_draw+'</td><td>'
        rr+=graphics_clock+'</td><td>'+mem_clock+'</td><td>'+video_clock+'</td></tr>'
    print (r)
    return rr

run()
