import requests, configparser,os,smtplib,json
import xml.etree.ElementTree as ET
from threading import Timer
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
m=[]
ferma = ['192.168.1.2','192.168.1.3','192.168.1.7']
pp=ss=ttmax=0
ttmin=100

def run():
    Timer(600,run).start()
    m.clear()
    global pp,ss,ttmax,ttmin
    pp=ss=ttmasx=0
    ttmin=100
    qqq=''
    for x in ferma: #опрашиваем api удаленных машин
        try:
            r = requests.get('http://'+x+':42000/getstat', timeout=(3))
            add_array (x,r,len(r.json()["result"]))
        except requests.exceptions.RequestException:
            send_mail('no connect '+x)

    r=os.system("powershell -NoProfile -ExecutionPolicy ByPass -file mm_gg.ps1")
    if r != 0:
        send_mail('Fucking powershell ERROR')


    q='Power='+str(pp) + ' Sped='+str(ss) + ' Tmax='+str(ttmax) + ' Tmin='+str(ttmin) + '\n'

    print (datetime.today())
    print (q)

    #сборка web страницы index.html
    qq='<html><body style="background-color:#111111;color:#ffffff;font-weight:bold;">'
    qq+='<p>'+str(datetime.today())+'</p><p>'+q+'</p>'
    qq+='<table border=1 style="font-weight: bold;float:left;">'
    qq+='<tr><td>IPADDR</td><td>Temp</td><td>Power</td><td>Hash</td><td>Ac</td><td>Rj</td></tr>'
    qq+=get_array_json()+'</table>'
    qq+='<table border=1 style="font-weight: bold;float:left"><tr><td>Name</td><td>Cooler</td><td>CPU</td><td>MEM</td><td>Temp</td><td>Watt</td><td>GPU Clock</td><td>MEM Clock</td><td>VIDEO Clock</td></tr>'

    for x in ferma: #собираем данные из файлов *.xml
        if os.path.isfile(x+'.xml'):
            qqq+=get_ps_xml(x+'.xml')

    qq+=qqq+'</table>'
    qq+='</body></html>'

    f = open('index.html', 'w')
    f.write(qq)
    f.close()

    #если средине показатели отклоняются - уведомляем почтой
    if pp < 1600 or ss < 570 or ttmax > 73 or ttmin < 40:
        send_mail('Fucking mining ERROR')

def add_array(j,r,n): #наполнение массива элементами взятыми из api json майнеров
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

def get_array_json(): #перебор массива с данными взятыми из api майнеров и подготовка к выводу
    rr=r=''
    for row in m:
        rr+='<tr>'
        for elem in row:
            r += str(elem) + ' '
            rr+='<td>'+str(elem)+'</td>'
        r+='\n'
        rr+='</tr>'
    print(r)
    return rr

def get_ps_xml(p1): #перебор элементов в xml файлах(файлы получены через powershell 5.1 через сесиию) и подготовка к выводу
    tree = ET.parse(p1)
    root = tree.getroot()
    driver_version = root.find('driver_version')
    rr=r=''
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

def send_mail(q): #отправка уведомлений почтой
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

run()
