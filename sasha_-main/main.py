import uvicorn
from fastapi import FastAPI, Request, Depends, BackgroundTasks, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles #für css
import jinja2 as JJ2
from fastapi_mqtt import FastMQTT, MQTTConfig
from pydantic import BaseModel
from datetime import datetime
import statemachine
import asyncio
import httpx as httpx
import scrape_gigacube
import random
import json
import os

dir_path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(dir_path, 'ini.json')) as f:
    ini = json.load(f)

Wetter_KEY = ini["Wetter_KEY"]
Tank_KEY = ini["Tank_KEY"]
Server_IP = ini["Server_IP"]

with open(os.path.join(dir_path, 'komplimente.txt')) as f:
    komplimente = f.readlines()

templates = Jinja2Templates(directory="templates") #html Seiten

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static") #für CSS und so



iot_state = statemachine.iot_json()

scrape_state = statemachine.scrape_json()

class Item(BaseModel):
    cmd: str
    number: float

mqtt_config = MQTTConfig(host = Server_IP,
    port= 1883,
    keepalive = 60,
    username="",
    password="")

mqtt = FastMQTT(
    config=mqtt_config
)

mqtt.init_app(app)

class BackgroundRunner:
    def __init__(self):
        self.value = 0
        self.client0 = "cmnd/Lampe/POWER"
        self.cmdOFF = "OFF"
        self.minute = 0

    # async def switch(self, client, command):
    #     await mqtt.publish(client, command)

    async def switch_by_time(self):
        while True:
            is_minute = datetime.now().minute
            #print(self.client0)
            if is_minute < 67:
                #print("nichts passiert")
                await asyncio.sleep(60)
            else:
                await mqtt.publish(self.client0, self.cmdOFF)
                await asyncio.sleep(600) #60 war

    async def giga_scrape(self):
        while True:
            scrape_gigacube.scrape_giga()
            await asyncio.sleep(60*60*6) #21600

runner = BackgroundRunner() # für Zeitsteuerungen und so

@app.on_event('startup')
async def app_startup():
    asyncio.create_task(runner.switch_by_time())
    asyncio.create_task(runner.giga_scrape())


@mqtt.on_connect()
def connect(client, flags, rc, properties):
    mqtt.client.subscribe("stat/Lampe/POWER") #stat/Lampe/POWER
    print("Connected: ", client, flags, rc, properties)
#    mqtt.client.subscribe("stat/Küche/POWER") #stat/Lampe/POWER
 #   print("Connected: ", client, flags, rc, properties)
#    mqtt.client.subscribe("sensor/co2") #stat/Lampe/POWER
#    print("Connected: ", client, flags, rc, properties)

@mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    print(client, topic, payload.decode())
    if payload.decode() == "ON":
        an = True
    else:
        an = False
    iot_state.switch(topic = "cmnd/Lampe/POWER", Zustand = an)

@mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    print("Disconnected")

@mqtt.on_subscribe()
def subscribe(client, mid, qos, properties):
    print("subscribed", client, mid, qos, properties)

@app.get('/')
def read_form():
    return "moin chef"

fuu = JJ2.Template("My favorite numbers: {% for n in range(1,10) %}{{n}} " "{% endfor %}")
fuu.render()

@app.get("/baum")
async def root2(request: Request): #das Request hier musste sein, noch kA warum
    hallo = "es funktioniert über jinja"
    liste = [0, 1, 2, 3, 4, 5]
    return templates.TemplateResponse('baum.html',{'request': request, 'message': hallo, 'my_list': liste }) #hier auch request, {{message}} steht in der HTML

@app.get("/index")
def form_post(request: Request):
    pferd = "Type a number"
    wetter_api = httpx.get(f"http://api.openweathermap.org/data/2.5/forecast?q=Bakum&units=metric&appid={Wetter_KEY}")
    das_Wetter = wetter_api.json()
    temp = das_Wetter["list"][0]["main"]["temp"]

    tanken_api = httpx.get(f"https://creativecommons.tankerkoenig.de/json/list.php?lat=52.7412&lng=8.1955&rad=15&sort=price&type=diesel&apikey={Tank_KEY}")
    Tankstellen = tanken_api.json()
    diesel = Tankstellen["stations"][0]["price"]

    giga_sate = scrape_state.check("vodafone")
    volume = giga_sate[0]
    verbraucht = giga_sate[1]
    zeit = giga_sate[2]
    z_zeit = float(zeit)
    z_volume = float(volume)
#    z_volume = format(z_volume, '.2f')
    z_diff = 340*(z_zeit/100)-(340-z_volume)
    diff = format(z_diff,format('.2f'))
    print(diff)
    kom_i= random.randint(0,len(komplimente))
    kompl_py = komplimente[kom_i]
    return templates.TemplateResponse('index.html', context={'request': request, 'result': pferd, 'volume': volume,'verbraucht': verbraucht,'zeit': zeit,'diff': diff,'diesel': diesel,'temp': temp, 'kompl_web': kompl_py })

@app.post("/index")
def form_post(request: Request, num: int = Form(...)):
    result = num
    return templates.TemplateResponse('index.html', context={'request': request, 'result': result})

@app.get("/control")
def form_get(request: Request):
    saft = "moin"
    wasser =123
    return templates.TemplateResponse('control.html', context={'request': request, 'bier': saft, "sekt": wasser})

@app.post('/control')
def form_post(request: Request, num: int = Form(...), action: str = Form(...)):
    if action == 'convert':
        transf = num * 2
        result = "moin"
        return templates.TemplateResponse('control.html', context={'request': request, 'bier': result, 'sekt': transf})
    elif action == 'download':
        result = "Alster"
        transf = num * 3
        return templates.TemplateResponse('control.html', context={'request': request, 'bier': result, 'sekt': transf})

@app.get("/wetter")
async def form_get(request: Request):
    wetter_api = httpx.get(f"http://api.openweathermap.org/data/2.5/forecast?q=Bakum&units=metric&appid={Wetter_KEY}")
    das_Wetter = wetter_api.json()
    liste_wetter = []
    for k in range(len(das_Wetter["list"])):
        txt = das_Wetter["list"][k]["dt_txt"]
        look = das_Wetter["list"][k]["weather"][0]["main"]
        temp = das_Wetter["list"][k]["main"]["temp"]
        f_l = das_Wetter["list"][k]["main"]["feels_like"]
        druck = das_Wetter["list"][k]["main"]["pressure"]
        wind = das_Wetter["list"][k]["wind"]["speed"]
        w_deg = das_Wetter["list"][k]["wind"]["deg"]
        reihe = txt+ "\t\r\t|\r\t|\r\t------  "+look+" Temp: "+str(temp)+" feels like: "+str(f_l)+" Druck: "+str(druck)+" Wind: "+str(wind)+" Windrichtung: "+str(w_deg)
        liste_wetter.append(reihe)

    liste_wetter.pop(0)

    return templates.TemplateResponse('wetter.html', context={'request': request, "wetter": liste_wetter})

@app.get("/knoepfe")
def form_get(request: Request):
    Lampe_state = iot_state.check("Lampe")
    if Lampe_state == True:
        Lampe_status_str = "an"
        str_bg_an = "background-color:#827597"
        str_bg_aus = ""
    else:
        Lampe_status_str = "aus"
        str_bg_an = ""
        str_bg_aus = "background-color:#827597"
    return templates.TemplateResponse('knoepfe.html', context={'request': request,'Lampe_status': Lampe_status_str, 'bg_an': str_bg_an, 'bg_aus': str_bg_aus})

@app.get('/off')
async def mqtt_test():
    await mqtt.publish("cmnd/Lampe/POWER","OFF")

@app.get('/on')
async def mqtt_test():
    await mqtt.publish("cmnd/Lampe/POWER","ON")
    return "testi"

@app.post('/knoepfe')
async def form_post(request: Request, action: str = Form(...)):
    if action == 'Lampe aus':
        await mqtt.publish("cmnd/Lampe/POWER","OFF")
        Lampe_status_str = "aus"
        check ="huhu"
        str_bg_an = ""
        str_bg_aus = "background-color:#827597"
    elif action == 'Lampe an':
        await mqtt.publish("cmnd/Lampe/POWER","ON")
        check = "moin"
        Lampe_status_str = "an"
        str_bg_an = "background-color:#827597"
        str_bg_aus = ""
    return templates.TemplateResponse('knoepfe.html', context={'request': request,"check": check, 'Lampe_status': Lampe_status_str, 'bg_an': str_bg_an, 'bg_aus': str_bg_aus})

@app.get("/tanken")
async def form_get(request: Request):
    tanken_api = httpx.get(f"https://creativecommons.tankerkoenig.de/json/list.php?lat=52.7412&lng=8.1955&rad=15&sort=price&type=diesel&apikey={Tank_KEY}")
    Tankstellen = tanken_api.json()
    liste_Tankstellen = []
    for k in range(len(Tankstellen["stations"])):
        marke = Tankstellen["stations"][k]["brand"]
        ort = Tankstellen["stations"][k]["place"]
        preis = Tankstellen["stations"][k]["price"]
        entfernung = Tankstellen["stations"][k]["dist"]
        reihe = "Preis Diesel: " + str(
            preis) + "\t\r\t|\r\t|\r\t------  " + " Tanke: " + marke + "| Ort: " + ort + "| Entfernung im km: " + str(
            entfernung)
        liste_Tankstellen.append(reihe)
    liste_Tankstellen.pop(0)
    return templates.TemplateResponse('tanken.html', context={'request': request, "Tanken": liste_Tankstellen})
