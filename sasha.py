import uvicorn
import json
import os

dir_path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(dir_path, 'ini.json')) as f:
    ini = json.load(f)

Server_IP = str(ini["Server_IP"])
Entwicklung_IP = str(ini["Entwicklung_IP"])


# templates = Jinja2Templates(directory="templates")
#
# app = FastAPI()
#
# app.mount("/static", StaticFiles(directory="static"), name="static")

Umgebung = ini["Umgebung"]

if Umgebung == 'Entwicklung':
    uvicorn.run("main:app", host=Entwicklung_IP, port=5000, reload=False)
elif Umgebung == 'sasha':
    uvicorn.run("main:app", host=Server_IP, port=5000, reload=False)
