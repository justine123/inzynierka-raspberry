import RPi.GPIO as GPIO
from DHT11_Python import dht11
import time
import datetime
import pyowm
import csv
import socket
import sys
import json


def read_from_sensors():
    # initialize GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()

    # read data using pin 4
    instance = dht11.DHT11(pin=4)
    temp_results = []
    results = []
    
    print("Start!")
    while True:
        result = instance.read()
        # TODO: rowniez odczyt z czujnika pylow co 1s
        if result.is_valid():
            temp_results.append([result.temperature, result.humidity]) # TODO: dokladac rowniez tu z pylow analigicznie gdy jest valid...
            print("Last valid input: " + str(datetime.datetime.now()))
        # every minute average and send data
        if datetime.datetime.now().second == 0:
            write_and_send(temp_results)
            temp_results = []
            # every minute try to synchronize database (send those "not send" records)
            if datetime.datetime.now().minute == 0:
                synchronize()
        time.sleep(1)


def average(temp_results):
    avg_datetime = datetime.datetime.now().replace(second = 0, microsecond = 0, minute = datetime.datetime.now().minute-1)  # results from previous minute
    if len(temp_results) == 0:
        print("No results!")
        return avg_datetime, '', ''
    else:
        avg_temperature = sum(row[0] for row in temp_results)/len(temp_results)
        avg_humidity = sum(row[1] for row in temp_results)/len(temp_results)
    return avg_datetime, avg_temperature, avg_humidity


def get_weather_data():
    owm = pyowm.OWM('e4fde90e6d809209411d7c680e9e52d7')
    observation = owm.weather_at_place('Cracov, pl')
    w = observation.get_weather()
    wind = w.get_wind()
    pressure = w.get_pressure()
    return wind, pressure


def write_and_send(temp_results):
    print(len(temp_results))
    avg_datetime, avg_temperature, avg_humidity = average(temp_results) # TODO: usredniac rowniez pyly
    wind, pressure = get_weather_data()
    data = {'sensor_id': 1, 'date': str(avg_datetime), 'temperature': avg_temperature, 'humidity': avg_humidity, 'pm2.5': '', 'pm10': '',
            'wind_direction': wind['deg'], 'wind_speed': wind['speed'], 'pressure': pressure['press'], 'send': ''}
    # send data via socket
    host = "192.168.137.1"
    port = 8888
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created")
    try:
        s.connect((host, port))
        print("Connected, about to send")
        s.send(json.dumps(data))
        print("Done sending")
        data['send'] = 'YES'
    except socket.error:
        print("Unable to connect to", host)
        data['send'] = 'NO'
    # write data to csv backup copy with correct flag (data send or not send)
    with open('results.csv', 'a') as csvfile:
        fieldnames = ['sensor_id', 'date', 'temperature', 'humidity', 'pm2.5', 'pm10', 'wind_direction', 'wind_speed', 'pressure', 'send']
        writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
        writer.writeheader()
        writer.writerow(data)
    print(data)


def synchronize():
    host = "192.168.137.1"
    port = 8888
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with open('results.csv', 'a') as csvfile:
        reader = csv.DictWriter(csvfile)
        for row in reader:
            if row['send'] == 'NO':
                try:
                    s.connect((host, port))
                    print("Connected, about to send")
                    s.send(json.dumps(row))
                    print("Done sending")
                    row['send'] = 'YES'
                except socket.error:
                    print("Unable to connect to", host)
    

if __name__ == "__main__":
    read_from_sensors()
