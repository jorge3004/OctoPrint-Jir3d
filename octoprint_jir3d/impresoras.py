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
    urlJob = "http://localhost:5000/api/job"
    urlPrinter = "http://localhost:5000/api/printer"

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

    def printerStatusFlags(self):
        return requests.request(
            "GET",
            self.urlPrinter,
            headers={'Authorization': 'Bearer ' + self.apikey}
        ).json().get('state', {}).get('flags', {})

    def printerStatus(self):
        return requests.request(
            "GET",
            self.urlPrinter,
            headers={'Authorization': 'Bearer ' + self.apikey}
        ).json()

    def printerStatusTemperatureBed(self):
        return requests.request(
            "GET",
            self.urlPrinter,
            headers={'Authorization': 'Bearer ' + self.apikey}
        ).json().get('temperature', {}).get('bed', {}).get('actual', {})

    def printerStatusTemperatures(self):
        return requests.request(
            "GET",
            self.urlPrinter,
            headers={'Authorization': 'Bearer ' + self.apikey}
        ).json().get('temperature', {})

    def printerStatusTemperatureNozzle(self):
        return requests.request(
            "GET",
            self.urlPrinter,
            headers={'Authorization': 'Bearer ' + self.apikey}
        ).json().get('temperature', {}).get('tool0', {}).get('actual', {})

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

    def jobPrinter(self, option):

        if(option == "pause"):
            data = {
                "command": "pause",
                "action": "pause"
            }
        elif(option == "resume"):
            data = {
                "command": "pause",
                "action": "resume"
            }
        else:
            data = {"command": option}

        return requests.request(
            "POST",
            self.urlJob,
            headers={
                'Authorization': 'Bearer ' + self.apikey,
                'Content-Type': 'application/json'
            },

            data=json.dumps(data)
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
        if(data["status"] != "Closed"):
            state = impresoraLocal.printerStatus()
            data['tempNozzle'] = state.get(
                'temperature', {}).get(
                'tool0', {}).get('actual', {})
            data['tempBed'] = state.get(
                'temperature', {}).get('bed', {}).get('actual', {})
            data['printerStatus'] = state.get('state', {}).get(
                'flags', {})

        comando = DataJir3d().updatePrinterData(
            impresoraLocal.nombre, data)
        try:
            comando = comando.json()
        except:
            comando = comando.text

        if(comando == "on"):
            impresoraLocal.turnPsuOn()
        elif(comando == "off"):
            impresoraLocal.turnPsuOff()
        elif(comando == "pausar"):
            impresoraLocal.jobPrinter("pause")
        elif(comando == "parar"):
            impresoraLocal.jobPrinter("cancel")
        elif(comando == "reiniciar"):
            impresoraLocal.jobPrinter("restart")
        elif(comando == "continuar"):
            impresoraLocal.jobPrinter("resume")
        elif(comando != ""):
            completeName = os.path.join(
                Impresora().updatesDir, "nivelar.gcode")
            file1 = open(completeName, "w")
            file1.write(comando)
            file1.close()
            impresoraLocal.turnPsuOn()
            time.sleep(8)
            impresoraLocal.nivelar()
        time.sleep(2)


def principal(nombreImpresora, apikey):
    global impresoraLocal
    impresoraLocal = Impresora(nombreImpresora, apikey)
    if(nombreImpresora != "jir3d_nombre"):
        hilo = threading.Thread(target=paralelo)
        hilo.daemon = True
        hilo.start()


# impresoraPuebla = Impresora("Puebla", "F59852448440447FB980DD796402BD21")
# data = {
#     "status": "sta",
#     "uReporte": "ure",
# }
# impresoraLocal = Impresora("Novara", "01997B15DB0B4839B2FDDE7727DD2E0F")
# print(impresoraLocal.printerStatusFlags())
# # print(impresoraLocal.printerStatusTemperatureBed())
# # print(impresoraLocal.printerStatusTemperatureNozzle())
# print(data)
