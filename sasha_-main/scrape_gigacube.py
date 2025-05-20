import httpx as httpx
import requests
from bs4 import BeautifulSoup
import json
from datetime import time,date

def scrape_giga():
    site = "https://center.vodafone.de/vfcenter/index.html"

    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    }
    # Get HTML Content
    r = requests.get(site, headers=header)
    soup = BeautifulSoup(r.content, "html.parser")

    volume_scr = str(soup.find_all("div", class_="volume"))
    verbraucht_scr = str(soup.find_all("div", class_="col w-35"))
    restzeit_scr = soup.find_all("div", class_="fr")

    volume_start = volume_scr.find("<strong>",0)
    volume_end = volume_scr.find("</strong>",0)
    volume = volume_scr[volume_start+8:volume_end-3]
    volume = volume.replace(",",".")
    volume = format(volume, '.2f')

    verbraucht_start = verbraucht_scr.find("Sie haben ",0)
    verbraucht_end = verbraucht_scr.find(" Ihrer",0)
    verbraucht = verbraucht_scr[verbraucht_start+10:verbraucht_end]
    verbraucht = verbraucht.replace('%', '')

    restzeit_str = str(restzeit_scr[2])
    restzeit_start_d = restzeit_str[17:19]
    restzeit_start_m = restzeit_str[19:22]
    restzeit_ende_d = restzeit_str[23:26]
    restzeit_ende_m = restzeit_str[26:28]

    restzeit_start_d = restzeit_start_d.strip(".")
    restzeit_start_m = restzeit_start_m.strip(".")
    restzeit_ende_d = restzeit_ende_d.strip(".")
    restzeit_ende_m = restzeit_ende_m.strip(".")

    heute = date.today()

    print(heute.year)

    startzeitpunkt = date(year=heute.year, month=int(restzeit_start_m),day=int(restzeit_start_d))
    endzeitpunkt = date(year=heute.year, month=int(restzeit_ende_m),day=int(restzeit_ende_d))

    rest_delta = heute-startzeitpunkt
    rest_delta = int(rest_delta.days)
    rest_prozent = (1-((30-rest_delta)/30))*100
    rest_prozent = format(rest_prozent, '.2f')
#    rest_prozent = str(rest_prozent)


    file = "data.json"

    with open(file) as f:
        data = json.load(f)
    data["scraper"]["name" == "vodafone"]["value_1"] = volume
    data["scraper"]["name" == "vodafone"]["value_2"] = verbraucht
    data["scraper"]["name" == "vodafone"]["value_3"] = rest_prozent
    with open(file, "w") as f:
        json.dump(data, f)
    return

#g = scrape_giga()