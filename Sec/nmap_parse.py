# nmap -T4 -A -v 192.168.1.1 -sV -oX version_scan.xml  
import xml.etree.ElementTree as ET
root = ET.parse('version_scan.xml').getroot()

for hint in root.findall('hosthint'):
    for status in hint.findall('status'):
        if status.get('state') == 'up':
            a = hint.findall('address')
            for addr in zip(a[::2], a[1::2]):
                vendor = addr[1].get('vendor')
                ip = addr[0].get('addr')
                mac = addr[1].get('addr')
                
                print(f"{vendor}\n{ip}\n{mac}\n")
