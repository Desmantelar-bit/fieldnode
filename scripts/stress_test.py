import random
import paho.mqtt.client as mqtt
import json
import time
import requests
import os
import getpass
from threading import Thread
from random import randint

BROKER='localhost'
PORT=1883
MQTT_DEVICE_ID=os.getenv('MQTT_DEVICE_ID', '').strip()
MQTT_MACHINE_ID=os.getenv('MQTT_MACHINE_ID', '').strip()
HEALTH_URL=os.getenv('FIELDNODE_HEALTH_URL', 'http://127.0.0.1:8000/api/health/')
API_KEY=os.getenv('FIELDNODE_API_KEY', '')
INTERVALO=2
DURATION=30*60

sent=0
errors=0
lat=[]

def on_c(client,u,f,r):pass
def gen(m, device_id):return{"id":f"{m}-{int(time.time()*1000)}","device_id":device_id,"maquina_id":m,"temperatura":round(random.uniform(65,75),1),"vibracao":round(random.uniform(0.1,0.3),2),"rpm":randint(1700,1900),"timestamp":time.time()}
def mon():
    global errors,lat
    while True:
        try:
            s=time.time()
            headers={'X-API-Key': API_KEY} if API_KEY else {}
            requests.get(HEALTH_URL,headers=headers,timeout=3)
            lat.append((time.time()-s)*1000)
        except requests.RequestException:
            errors+=1
        time.sleep(30)
def main():
    global sent
    if not MQTT_DEVICE_ID or not MQTT_MACHINE_ID:
        raise RuntimeError('Defina MQTT_DEVICE_ID e MQTT_MACHINE_ID para uma identidade provisionada.')
    mqtt_password=getpass.getpass(f'Senha MQTT de {MQTT_DEVICE_ID}: ')
    if not mqtt_password: raise RuntimeError('Senha MQTT vazia; conexão cancelada.')
    c=mqtt.Client()
    c.username_pw_set(MQTT_DEVICE_ID, mqtt_password)
    c.on_connect=on_c
    c.connect(BROKER,PORT)
    c.loop_start()
    Thread(target=mon,daemon=True).start()
    e=time.time()+DURATION
    while time.time()<e:
        c.publish(f"fieldnode/{MQTT_DEVICE_ID}/telemetria",json.dumps(gen(MQTT_MACHINE_ID, MQTT_DEVICE_ID)))
        sent+=1
        time.sleep(INTERVALO)
    c.loop_stop()
    print(f"SENT={sent}")
    if lat:print(f"LAT_MS={int(sum(lat)/len(lat))}")
    print(f"ERR={errors}")
if __name__=="__main__":main()
