import csv
import datetime
import json
import socket
import sys
import time
import serial

import RPi.GPIO as GPIO
import pyowm
from DHT11_Python import dht11

#need_to_synchronize = False

def read_from_sensors():
    print("Start!")
    temp_results = []
    # initialize GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()
<<<<<<< HEAD
    instance = dht11.DHT11(pin=4)  # read data from DHT11 sensor using pin 4
    schar = 0x4d42
    port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=5.0)  # serial port for dust sensor

=======
    # read data from DHT11 sensor using pin 4
    instance = dht11.DHT11(pin=4)
    temp_results = []
    results = []

    print("Start!")
    
>>>>>>> 7cdd1690b8cd3559ae232ec3718778997c414732
    while True:
        result = instance.read()
        pm25 = ''
        pm10 = ''

        """try:
            rcv = port.read(32)
            rlen = len(rcv)
            if rlen == 32:
                schar, flen, pm10, pm25, pm100, td1, td2, td3, ab3, ab5, ab10, ab25, ab50, ab100, td4, csum = \
                    unpack('>HHHHHHHHHHHHHHHH', rcv)
            # Check Bit for Data Sum, 16-byte 	Check Bit = Start Character 1 + Start Character 2 + ...all data
            cSum = 0
            for i in range(0, len(rcv) - 3):
                cSum = cSum + ord(rcv[i])
            # print('4=',hex(schar),hex(flen), hex(pm10), hex(pm25), hex(pm100), hex(td1), hex(td2), hex(td3), hex(ab3),
            # hex(ab5), hex(ab10), hex(ab25), hex(ab50), hex(ab100), hex(td4), hex(csum), hex(cSum))

            if (schar == 0x424d) and (cSum == csum):
                print("OK!", pm10, pm25)
            else:
                print('Byte order NOT OK')
                try:
                    port.read(31)
                except:
                    port.flushInput()
                    print("Read 1 error")
        except (KeyboardInterrupt, SystemExit):
            port.close() """

        if result.is_valid():
            temp_results.append([result.temperature, result.humidity, pm25, pm10])
            print("Last valid input: " + str(datetime.datetime.now()))

        # every minute average results from sensors and send data in separate thread
        if datetime.datetime.now().second == 0:
            #try:
             #   w_s = os.pipe()
              #  thread.start_new_thread(write_and_send, ("Thread-1", w_s,))
               # threading.Thread(target=write_and_send, args=(temp_results,)).start()
            #except:
             #   print("Error: unable to start thread")
            write_and_send(temp_results)
            temp_results = []
        time.sleep(1)


def average(temp_results):
    avg_datetime = datetime.datetime.now().replace(second=0, microsecond=0,
                                                   minute=(datetime.datetime.now().minute - 1) % 60)
    if len(temp_results) == 0:
        print("No results!")
        return avg_datetime, '', '', '', ''
    else:
        avg_temperature = sum(row[0] for row in temp_results) / len(temp_results)
        avg_humidity = sum(row[1] for row in temp_results) / len(temp_results)
        avg_pm25 = ''  # sum(row[2] for row in temp_results) / len(temp_results)
        avg_pm10 = ''  # sum(row[3] for row in temp_results) / len(temp_results)
    return avg_datetime, avg_temperature, avg_humidity, avg_pm25, avg_pm10


def get_weather_data():
    try:
        owm = pyowm.OWM('e4fde90e6d809209411d7c680e9e52d7')
        observation = owm.weather_at_place('Cracov, pl')
        w = observation.get_weather()
        wind = w.get_wind()
        pressure = w.get_pressure()
    except socket.error:
        wind = {'deg': '', 'speed': ''}
        pressure = {'press': ''}
<<<<<<< HEAD
    return wind, pressure
=======
    return wind, pressure   
>>>>>>> 7cdd1690b8cd3559ae232ec3718778997c414732


def write_and_send(temp_results):
    global need_to_synchronize
    print(len(temp_results))
    avg_datetime, avg_temperature, avg_humidity, avg_pm25, avg_pm10 = average(temp_results)
    wind, pressure = get_weather_data()
    data = {'sensor_id': 1, 'date': str(avg_datetime), 'temperature': avg_temperature, 'humidity': avg_humidity,
            'pm2.5': avg_pm25, 'pm10': avg_pm10, 'wind_direction': wind['deg'], 'wind_speed': wind['speed'],
            'pressure': pressure['press'], 'send': ''}

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
<<<<<<< HEAD
        data['send'] = 'YES'

        # if sending was successful and there is unsend data, then try to synchronize databases
        if need_to_synchronize:
           # try:
            #    synch = os.pipe()
             #   thread.start_new_thread(synchronize, ("Thread-1", synch,))
              #  threading.Thread(target=synchronize).start()
            #except:
             #   print("Error: unable to start thread")
            synchronize()
=======
        data['send'] = 'NO'
        # if sending was successful and there is unsend data, then try to synchronize databases
        #if need_to_synchronize:
            #synchronize()
>>>>>>> 7cdd1690b8cd3559ae232ec3718778997c414732
    except socket.error:
        print("Unable to connect to " + host)
        data['send'] = 'NO'
<<<<<<< HEAD
        need_to_synchronize = True

=======
        #need_to_synchronize = True
>>>>>>> 7cdd1690b8cd3559ae232ec3718778997c414732
    # write data to csv backup copy with correct flag (data send or not send)
    with open('results.csv', 'a') as csvfile:
        fieldnames = ['sensor_id', 'date', 'temperature', 'humidity', 'pm2.5', 'pm10', 'wind_direction', 'wind_speed',
                      'pressure', 'send']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(data)
    print("Data: ")
    print(data)
<<<<<<< HEAD
    print("Need to synchronize: ")
    print(need_to_synchronize)
=======
    #print(need_to_synchronize)
>>>>>>> 7cdd1690b8cd3559ae232ec3718778997c414732


def synchronize():
    global need_to_synchronize
    host = "192.168.137.1"
    port = 8888
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with open('results.csv', 'rw') as csvfile:
<<<<<<< HEAD
        fieldnames = ['sensor_id', 'date', 'temperature', 'humidity', 'pm2.5', 'pm10', 'wind_direction', 'wind_speed',
                      'pressure', 'send']
=======
        fieldnames = ['sensor_id', 'date', 'temperature', 'humidity', 'pm2.5', 'pm10', 'wind_direction', 'wind_speed', 'pressure', 'send']
>>>>>>> 7cdd1690b8cd3559ae232ec3718778997c414732
        reader = csv.DictReader(csvfile, fieldnames=fieldnames)
        try:
            s.connect((host, port))
            for row in reader:
                if row['send'] == 'NO':
                    try:
                        s.send(json.dumps(row))
                        print("Done sending")
                        row['send'] = 'YES'
                        print(row)
                        time.sleep(10)
                    except socket.error:
                        print("Unable to send data")
                        return
<<<<<<< HEAD
            need_to_synchronize = False
        except socket.error:
            print("Unable to connect to", host)
            return

=======
        except socket.error:
                print("Unable to connect to", host)
                return
    #need_to_synchronize = False
    
>>>>>>> 7cdd1690b8cd3559ae232ec3718778997c414732

if __name__ == "__main__":
    #try:
     #   r_s = os.pipe()
      #  thread.start_new_thread(read_from_sensors)
        #threading.Thread(target=read_from_sensors).start()
   # except:
       # print("Error: unable to start read_from_sensors thread")
    read_from_sensors()
