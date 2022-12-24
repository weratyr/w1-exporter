#!/usr/bin/python
# -*- coding: utf-8 -*-

from pathlib import Path
from bottle import route, run, template, request, post, get, static_file, redirect, app, response

sensorDict = {}
sensorPath = '/sys/bus/w1/devices/w1_bus_master1/'

w1_exporter = app()

def collectSensors():
    sensors = []
    try:
        print("collect")
        for sensor in Path(sensorPath).glob("28-*"):
            print(sensor.name)
            sensorDict[sensor.name] = -99
        return sensors
    except Exception as e:
        print(f"Could not collect sensors! {e}")
        return sensors



def readData():
    data = ""
    collectSensors()
    try:
        for sensor in sensorDict:
            with open(f"{sensorPath}{sensor}/temperature", 'r') as temp:
                data = temp.read()
                sensorDict[sensor] = data
                print(sensor, data)
    except Exception as e:
        print("Cannot fetch w1 api data: %s" % e)
        data=""
    return data


@w1_exporter.route('/')
def index():
        redirect('/metrics')

@w1_exporter.route('/metrics')
def metrics():

    data = readData()
    print(data)

    #return "done"

    respdata=['\n'.join([
'# HELP w1_temperature_celsius',
'# TYPE w1_temperature_celsius gauge',
])]

    # Temperatures
    try:
        for sonsor in sensorDict:
            respdata.append(f"w1_temperature_celsius{{name=\"heater-{sonsor}\"}} {sensorDict[sonsor]}")
    except Exception as e :
        print("Temperature error %s" % e)


    response.content_type = 'text/plain'
    response.encoding = 'utf-8'

    return '\n'.join(respdata)+'\n'




try:
    run(app=w1_exporter,host='0.0.0.0', port=8055, debug=True)
except Exception as e:
        print("Can not start web server: %s" % e)
finally:
    print("bye bye")