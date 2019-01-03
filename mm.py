import requests, configparser,os,smtplib,json,socket
import xml.etree.ElementTree as ET
from threading import Timer
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
m=[] #массив для ewbf
ferma = [] #массив ип-адресов ригов
power=hashrate=temp_max=0
temp_min=100

f = open('ip.txt')
for line in f:
    ferma.append(line.rstrip())
f.close()

def run():
    Timer(600,run).start()
    m.clear()
    global power,hashrate,temp_max,temp_min
    power=hashrate=ttmasx=0
    temp_min=100
    claymore_table=xml_table=''

    for x in ferma: #ewbf опрашиваем api удаленных майнеров через get 
        try:
            r = requests.get('http://'+x+':42000/getstat', timeout=(1))
            add_array (x,r,len(r.json()["result"]))
        except requests.exceptions.RequestException:
            #send_mail('no connect '+x)
            #print("exception ewbf")
            exit

    for x in ferma: #claymore опрашиваем api удаленных майнеров через сокет
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((x,3333))
            s.send('{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}'.encode("utf-8"))
            j=s.recv(2048)
            s.close()
            r=json.loads(j.decode("utf-8"))
            claymore_table+=get_json_claymore(r)
        except:
            send_mail('no connect '+x)
            print("exception claymore")

    r=os.system("powershell -NoProfile -ExecutionPolicy ByPass -file mm_gg.ps1")
    if r != 0:
        send_mail('Fucking powershell ERROR')

    q='Power='+str(power) + ' Sped='+str(hashrate) + ' Tmax='+str(temp_max) + ' Tmin='+str(temp_min) + '\n'
    print (datetime.today())
    print (q)

    #сборка web страницы index.html
    html='<html><body style="background-color:#111111;color:#ffffff;font-weight:bold;">'
    html+='<p>'+str(datetime.today())+'</p><p>'+q+'</p>'

    #сборка таблицы от ewbf
    #html+='<table border=1 style="font-weight: bold;float:left;">'
    #html+='<tr><td>IPADDR</td><td>Temp</td><td>Power</td><td>Hash</td><td>Ac</td><td>Rj</td></tr>'
    #html+=get_array_json()+'</table>'

    #сборка таблицы от claymore
    html+='<table border=1 style="font-weight: bold;float:left;">'
    html+='<tr><td>HASH</td><td>Temp</td><td>Cooler</td></tr>'
    html+=claymore_table+'</table>'

    #сборка таблицы от xml file nvidi-smi
    html+='<table border=1 style="font-weight: bold;float:left"><tr><td>Name</td><td>Cooler</td><td>CPU</td><td>MEM</td><td>Temp</td><td>Watt</td><td>GPU Clock</td><td>MEM Clock</td><td>VIDEO Clock</td></tr>'
    for x in ferma: #собираем данные из файлов *.xml
        if os.path.isfile(x+'.xml'):
            xml_table+=get_ps_xml(x+'.xml')
    html+=xml_table+'</table>'
    html+='</body></html>'

    f = open('index.html', 'w')
    f.write(html)
    f.close()

    #если средине показатели отклоняются - уведомляем почтой
    #if power < 1600 or hashrate < 570 or temp_max > 73 or temp_min < 40:
    if hashrate < 390000 or temp_max > 70 or temp_min < 40:
        send_mail('Fucking mining ERROR')

def add_array(j,r,n): #ewbf наполнение массива элементами взятыми из api json майнеров
    global power,hashrate,temp_max,temp_min
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
        power+=p
        hashrate+=s
        m.append([j,t,p,s,acs,rjs])

def get_array_json(): #ewbf перебор массива с данными взятыми из api майнеров и подготовка к выводу
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

def get_json_claymore(r): #claymore перебор данных json взятыми из api майнеров и подготовка к выводу
    global hashrate,temp_max,temp_min
    rr=''
    m3 = r['result'][3].split(';')
    m6 = r['result'][6].split(';')
    for x in range(len(m3)):
        hashr=m3[::][x]
        temp=m6[::2][x]
        cooler=m6[1::2][x]
        rr+='<tr>'
        rr+='<td>'+hashr+'</td>'+'<td>'+temp+'</td>'+'<td>'+cooler+'</td>'
        rr+='</tr>'
        hashrate+=int(hashr)
        if int(temp) > temp_max:
            temp_max = int(temp)
        elif int(temp) < temp_min:
            temp_min = int(temp)
        print (hashr+' '+temp+' '+cooler)
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

def send_mail(p1): #отправка уведомлений почтой
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8-sig')
    email_login = config.get('mail', 'username')
    email_pass = config.get('mail', 'password')
    email_to = config.get('mail', 'email_to')
    msg = MIMEMultipart()
    msg['From'] = email_login
    msg['To'] = email_to
    msg['Subject'] = "Warning Mining"
    body = p1
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
    server.login(email_login, email_pass)
    text = msg.as_string()
    server.sendmail(email_login, email_to, text)
    server.quit()

run()
