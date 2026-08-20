import paho.mqtt.client as mqtt
import json
import time
import requests
from threading import Thread
from random import randint

BROKER='localhost'
PORT=1883
MACHINES=[f'ST{i:03d}' for i in range(1,9)]
INTERVALO=2
DURATION=30*60

sent=0
errors=0
lat=[]

def on_c(client,u,f,r):pass
def gen(m):return{"id":f"{m}-{int(time.time()*1000)}","maquina_id":m,"temperatura":round(random.uniform(65,75),1),"vibracao":round(random.uniform(0.1,0.3),2),"rpm":randint(1700,1900),"timestamp":time.time()}
def mon():
    global errors,lat
    while True:
        try:
            s=time.time()
            requests.get('http://127.0.0.1:8000/api/status-maquinas/',headers={'X-API-Key':'fieldnode-demo-2024'},timeout=3)
            lat.append((time.time()-s)*1000)
        except:errors+=1
        time.sleep(30)
def main():
    c=mqtt.Client()
    c.on_connect=on_c
    c.connect(BROKER,PORT)
    c.loop_start()
    Thread(target=mon,daemon=True).start()
    e=time.time()+DURATION
    while time.time()<e:
        for m in MACHINES:
            c.publish(f"fieldnode/{m}/leitura",json.dumps(gen(m)))
            sent+=1
        time.sleep(INTERVALO/len(MACHINES))
    c.loop_stop()
    print(f"SENT={sent}")
    if lat:print(f"LAT_MS={int(sum(lat)/len(lat))}")
    print(f"ERR={errors}")
if __name__=="__main__":main()