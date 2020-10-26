#!/usr/bin/env python3
import binascii
import base64
import requests
from bluepy.btle import UUID, Peripheral, ADDR_TYPE_PUBLIC, DefaultDelegate, Scanner

# domoticz configuration
DOMOTICZ_SERVER_IP = "xxx.xxx.x.xxx"
DOMOTICZ_SERVER_PORT = "xxxx"
DOMOTICZ_USERNAME = ""
DOMOTICZ_PASSWORD = ""

# sensor dictionary to add own sensors
# if you don't want to use the raw voltage option, just write -1 in the VOLTAGE_IDX value field
sensors = { 	1: {"MAC": "xx:xx:xx:xx:xx:xx", "TH_IDX": 1, "VOLTAGE_IDX": -1},
		2: {"MAC": "xx:xx:xx:xx:xx:xx", "TH_IDX": 2, "VOLTAGE_IDX": -1},
		3: {"MAC": "xx:xx:xx:xx:xx:xx", "TH_IDX": 3, "VOLTAGE_IDX": -1}}

battery_level = -1
sensor_id = -1

class TempHumDelegate(DefaultDelegate):
	def __init__(self):
		DefaultDelegate.__init__(self)

	def handleNotification(self, cHandle, data):
		temperature = int.from_bytes(data[0:2],byteorder='little',signed=True)/100
		print("Temp:",temperature)
		humidity = int.from_bytes(data[2:3],byteorder='little')
		print("Hum:",humidity)
		voltage=int.from_bytes(data[3:5],byteorder='little') / 1000.
		print("Voltage:",voltage)
		batteryLevel = min(int(round((voltage - 2.1),2) * 100), 100)        #3.1 or above --> 100% 2.1 --> 0 %
		print("Battery level:",batteryLevel)
		comfort_type = get_comfort_type(humidity)
		if (sensor_id != -1 and batteryLevel > -1):
			for number, sensor in sensors.items():
				if sensor["TH_IDX"] == sensor_id:
					request_url = 'http://' + DOMOTICZ_SERVER_IP + ':' + DOMOTICZ_SERVER_PORT + '/json.htm?type=command&param=udevice&idx=' + str(sensor_id) + '&nvalue=0&svalue=' + str(temperature) + ';' + str(humidity) + ';' + comfort_type + '&battery=' + str(batteryLevel)
					send_to_domoticz(request_url)
					if sensor["VOLTAGE_IDX"] != -1:
						request_url = 'http://' + DOMOTICZ_SERVER_IP + ':' + DOMOTICZ_SERVER_PORT + '/json.htm?type=command&param=udevice&idx=' + str(sensor["VOLTAGE_IDX"]) + '&nvalue=0&svalue=' + str(voltage)
						send_to_domoticz(request_url)

def send_to_domoticz(url):
	print(url)
	requests.get(url, auth=(DOMOTICZ_USERNAME, DOMOTICZ_PASSWORD))

def get_comfort_type(humidity):
	comfort_type = "0"
	if float(humidity) < 40:
		comfort_type = "2"
	elif float(humidity) <= 70:
		comfort_type = "1"
	elif float(humidity) > 70:
		comfort_type = "3"
	return comfort_type

def handle_temp_hum_value():
	while True:
		if p.waitForNotifications(10.0):
			break

for number, sensor in sensors.items():
	try:
		sensor_id = sensor["TH_IDX"]
		print("TH_IDX:%d"%(sensor["TH_IDX"]))
		p = Peripheral(sensor["MAC"])
		p.writeCharacteristic(0x0038, b'\x01\x00', True)      #enable notifications of Temperature, Humidity and Battery voltage
		p.writeCharacteristic(0x0046, b'\xf4\x01\x00', True)
		p.withDelegate(TempHumDelegate())
		handle_temp_hum_value()
		p.disconnect()
	except Exception as e:
		print(str(e))
		pass
