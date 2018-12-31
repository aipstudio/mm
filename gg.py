import xml.etree.ElementTree as ET
import os
os.system("powershell -NoProfile -ExecutionPolicy ByPass -file mm_gg.ps1")

tree = ET.parse('192.168.1.7.xml')
root = tree.getroot()

driver_version = root.find('driver_version')
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
    r=product_name+' '+fan_speed+' '+gpu_util+' '+memory_util+' '+gpu_temp+' '
    r+=power_draw+' '+graphics_clock+' '
    r+=mem_clock+' '+video_clock
    print(r)
