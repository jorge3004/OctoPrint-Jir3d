import requests
import json
from datetime import datetime
# import pytz
import time
import threading


class Impresora:
    nombre = 'jir3d_nombre'
    apikey = 'jir3d_apikey'
    url = "http://localhost:5000/api/"

    def status(self):
        return requests.request(
            "GET", (self.url+"connection?apikey=" + self.apikey)).json().get('current', {}).get('state', {})


class DataJir3d():
    url = "https://api.jir3d.com.mx/"
    # url = "http://localhost:3010//"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }

    def updateStatus(self):
        return requests.request(
            "PUT",
            self.url+"impresoras.php" + "?nombre="+Impresora.nombre,
            headers=self.headers,
            data=json.dumps({"status": Impresora().status()})
        )

    def updateUReporte(self):
        return requests.request(
            "PUT",
            self.url+"impresoras.php" + "?nombre="+Impresora.nombre,
            headers=self.headers,
            data=json.dumps({"uReporte": int(round(time.time()))})
            # datetime.now(pytz.timezone('Mexico/General'))

        )


def paralelo():
    while (True):
        DataJir3d().updateStatus()
        DataJir3d().updateUReporte()
        time.sleep(4)


def principal(nombreImpresora, apikey):
    Impresora.nombre = nombreImpresora
    Impresora.apikey = apikey
    if(nombreImpresora != "jir3d_nombre"):
        hilo = threading.Thread(target=paralelo)
        hilo.daemon = True
        hilo.start()
