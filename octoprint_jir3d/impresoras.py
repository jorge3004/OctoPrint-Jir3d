from ast import If
import requests
import json
from datetime import datetime
# import pytz
import time
import threading
import os
import platform


class Impresora:
    urlConnection = "http://localhost:5000/api/connection"
    urlPSU = "http://localhost:5000/api/plugin/psucontrol"
    urlImprimir = "http://localhost:5000/api/files/local/nivelar.gcode"
    if (platform.system() == "Windows"):
        updatesDir = (os.getenv('APPDATA')+"/Octoprint/uploads")
    else:
        updatesDir = "/home/pi/.octoprint/uploads"

    def __init__(self, nombre="jir3d_nombre", apikey="jir3d_apikey"):
        self.nombre = nombre
        self.apikey = apikey

    def status(self):
        return requests.request(
            "GET",
            self.urlConnection,
            headers={'Authorization': 'Bearer ' + self.apikey}
        ).json().get('current', {}).get('state', {})

    def turnPsuOn(self):
        return requests.request(
            "POST",
            self.urlPSU,
            headers={
                'Authorization': 'Bearer ' + self.apikey,
                'Content-Type': 'application/json'
            },
            data=json.dumps({"command": "turnPSUOn"})
        )

    def turnPsuOff(self):
        return requests.request(
            "POST",
            self.urlPSU,
            headers={
                'Authorization': 'Bearer ' + self.apikey,
                'Content-Type': 'application/json'
            },
            data=json.dumps({"command": "turnPSUOff"})
        )

    def nivelar(self):
        return requests.request(
            "POST",
            self.urlImprimir,
            headers={
                'Authorization': 'Bearer ' + self.apikey,
                'Content-Type': 'application/json'
            },
            data=json.dumps({"command": "select", "print": "true"})
        )


class DataJir3d():
    urlImpresoras = "https://api.jir3d.com.mx/impresoras.php?nombre="
    # urlImpresoras = "http://localhost:3010/impresoras.php?nombre="

    def updatePrinterData(self, nombre, data):
        return requests.request(
            "PUT",
            self.urlImpresoras+nombre,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
            },
            data=json.dumps(data)
        )


def paralelo():
    while (True):
        data = {
            "status": impresoraLocal.status(),
            "uReporte": int(round(time.time())),
        }
        comando = DataJir3d().updatePrinterData(
            impresoraLocal.nombre, data).json()
        if(comando == "on"):
            impresoraLocal.turnPsuOn()
        elif(comando == "off"):
            impresoraLocal.turnPsuOff()
        elif(comando != ""):
            completeName = os.path.join(
                Impresora().updatesDir, "nivelar.gcode")
            # comando = comando.replace('\n', '')
            file1 = open(completeName, "w")
            file1.write(comando)
            file1.close()
            impresoraLocal.turnPsuOn()
            impresoraLocal.nivelar()

        time.sleep(3)


def principal(nombreImpresora, apikey):
    global impresoraLocal
    impresoraLocal = Impresora(nombreImpresora, apikey)
    if(nombreImpresora != "jir3d_nombre"):
        hilo = threading.Thread(target=paralelo)
        hilo.daemon = True
        hilo.start()


# impresoraPuebla = Impresora("Puebla", "F59852448440447FB980DD796402BD21")
# impresoraLocal = Impresora("Novara", "01997B15DB0B4839B2FDDE7727DD2E0F")
# data = {
#     "status": "sksk",
#     "uReporte": "ksksksks",
#     "comando": "sss"
# }
# print(DataJir3d().updatePrinterData(
#     impresoraLocal.nombre, data).json())
# impresoraPuebla.url = "http://octopi.local/api/"

# print(int(round(time.time())))
