#!/usr/bin/env python3
import config
import binascii
import requests
import logging
from bluepy.btle import UUID, Peripheral, ADDR_TYPE_PUBLIC, DefaultDelegate, Scanner

battery_level = -1
sensor_id = -1

class TempHumDelegate(DefaultDelegate):
	def __init__(self):
		DefaultDelegate.__init__(self)

	def handleNotification(self, cHandle, data):
		temperature = round(int.from_bytes(data[0:2],byteorder='little',signed=True)/100, config.TEMPERATURE_PREC)
		logging.info(f"Temp: {temperature}")
		humidity = int.from_bytes(data[2:3],byteorder='little')
		logging.info(f"Hum: {humidity}")
		voltage=int.from_bytes(data[3:5],byteorder='little') / 1000.
		logging.info(f"Voltage: {voltage}")
		batteryLevel = min(int(round((voltage - 2.1),2) * 100), 100)        #3.1 or above --> 100% 2.1 --> 0 %
		logging.info(f"Battery level: {batteryLevel}")
		comfort_type = get_comfort_type(humidity)
		logging.info(f"Comfort type: {comfort_type}")
		if (sensor_id != -1 and batteryLevel > -1):
			for number, sensor in config.sensors.items():
				if sensor['TH_IDX'] == sensor_id:
					request_url = create_TH_request(config.DOMOTICZ_SERVER_IP,config.DOMOTICZ_SERVER_PORT,sensor_id,temperature,humidity,comfort_type,batteryLevel)
					send_to_domoticz(request_url)
					if sensor['VOLTAGE_IDX'] != -1:
						request_url = create_VOLTAGE_request(config.DOMOTICZ_SERVER_IP,config.DOMOTICZ_SERVER_PORT,sensor['VOLTAGE_IDX'],voltage)
						send_to_domoticz(request_url)

def create_TH_request(server, port, idx, temp, hum, comfort, battery):
	url = ''
	url = (
		f"http://{server}:{port}"
		f"/json.htm?type=command&param=udevice&idx={idx}"
		f"&nvalue=0&svalue={temp};{hum};{comfort}"
		f"&battery={battery}")
	logging.info(f"The request is {url}")
	return url

def create_VOLTAGE_request(server, port, idx, voltage):
	url = ''
	url = (
		f"http://{server}:{port}"
		f"/json.htm?type=command&param=udevice&idx={idx}"
		f"&nvalue=0&svalue={voltage}")
	logging.info(f"The request is {url}")
	return url

def send_to_domoticz(url):
	resp = requests.get(url, auth=(config.DOMOTICZ_USERNAME, config.DOMOTICZ_PASSWORD))
	logging.info(f"The response is {resp}")

def get_comfort_type(humidity):
	comfort_type = '0'
	if float(humidity) < 40:
		comfort_type = '2'
	elif float(humidity) <= 70:
		comfort_type = '1'
	elif float(humidity) > 70:
		comfort_type = '3'
	return comfort_type

def handle_temp_hum_value():
	while True:
		if p.waitForNotifications(10.0):
			break

logging.basicConfig(filename='loginfo.log', level=logging.INFO)
logging.info('Start script...')
logging.info(	f"Input parameters:\r\n"
				f"Domoticz Server IP: {config.DOMOTICZ_SERVER_IP}\r\n"
				f"Domoticz Server Port: {config.DOMOTICZ_SERVER_PORT}\r\n"
				f"Domoticz Server User: {config.DOMOTICZ_USERNAME}\r\n"
				f"Domoticz Server Password: {config.DOMOTICZ_PASSWORD}")

for number, sensor in config.sensors.items():
	try:
		sensor_id = sensor['TH_IDX']
		logging.info(f"TH_IDX:{sensor['TH_IDX']}")
		p = Peripheral(sensor['MAC'])
		p.writeCharacteristic(0x0038, b'\x01\x00', True)      #enable notifications of Temperature, Humidity and Battery voltage
		p.writeCharacteristic(0x0046, b'\xf4\x01\x00', True)
		p.withDelegate(TempHumDelegate())
		handle_temp_hum_value()
		p.disconnect()
	except Exception as e:
		logging.error(str(e))
		pass
