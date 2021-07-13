#!/usr/bin/env python3
import config
import binascii
import requests
import logging
from logging.handlers import RotatingFileHandler
from bluepy.btle import UUID, Peripheral, ADDR_TYPE_PUBLIC, DefaultDelegate, Scanner, BTLEInternalError

battery_level = -1
sensor_id = -1

class TempHumDelegate(DefaultDelegate):
	def __init__(self):
		DefaultDelegate.__init__(self)

	def handleNotification(self, cHandle, data):
		temperature = round(int.from_bytes(data[0:2],byteorder='little',signed=True)/100, config.TEMPERATURE_PREC)
		logger.info(f"Temp: {temperature}")
		humidity = int.from_bytes(data[2:3],byteorder='little')
		logger.info(f"Hum: {humidity}")
		voltage=int.from_bytes(data[3:5],byteorder='little') / 1000.
		logger.info(f"Voltage: {voltage}")
		batteryLevel = min(int(round((voltage - 2.1),2) * 100), 100)		#3.1 or above --> 100% 2.1 --> 0 %
		logger.info(f"Battery level: {batteryLevel}")
		comfort_type = get_comfort_type(humidity)
		logger.info(f"Comfort type: {comfort_type}")
		if (sensor_id != -1 and batteryLevel > -1):
			for number, sensor in config.sensors.items():
				if sensor['TH_IDX'] == sensor_id:
					request_url = create_TH_request(config.DOMOTICZ_SERVER_IP,config.DOMOTICZ_SERVER_PORT,sensor_id,temperature,humidity,comfort_type,batteryLevel)
					send_to_domoticz(request_url)
					sensor['UPDATED'] = True
					if sensor['VOLTAGE_IDX'] != -1:
						request_url = create_VOLTAGE_request(config.DOMOTICZ_SERVER_IP,config.DOMOTICZ_SERVER_PORT,sensor['VOLTAGE_IDX'],voltage)
						send_to_domoticz(request_url)

	def handleDiscovery(self, dev, isNewDev, isNewData):
		for (sdid, desc, val) in dev.getScanData():
			if self.isTemperature(dev.addr, sdid, val):
				bytes = [int(val[i:i+2], 16) for i in range(0, len(val), 2)]
				temperature = (bytes[8] * 256 + bytes[9]) / 10
				logger.info(f"Temp: {temperature}")
				humidity = bytes[10]
				logger.info(f"Hum: {humidity}")
				comfort_type = get_comfort_type(humidity)
				logger.info(f"Comfort type: {comfort_type}")
				batteryLevel = bytes[11]
				logger.info(f"Battery level: {batteryLevel}")
				voltage = (bytes[12] * 256 + bytes[13]) / 1000
				logger.info(f"Voltage: {voltage}")
				for number, sensor in config.sensors.items():
					if (sensor['MAC'] == dev.addr) and (sensor['UPDATED'] == False):
						request_url = create_TH_request(config.DOMOTICZ_SERVER_IP,config.DOMOTICZ_SERVER_PORT,sensor['TH_IDX'],temperature,humidity,comfort_type,batteryLevel)
						send_to_domoticz(request_url)
						sensor['UPDATED'] = True
						if sensor['VOLTAGE_IDX'] != -1:
							request_url = create_VOLTAGE_request(config.DOMOTICZ_SERVER_IP,config.DOMOTICZ_SERVER_PORT,sensor['VOLTAGE_IDX'],voltage)
							send_to_domoticz(request_url)
				#break

	def isTemperature(self, addr, sdid, val):
		if sdid != 22:
			return False
		if len(val) != 30:
			return False
		return True

	def parseData(self, val):
		bytes = [int(val[i:i+2], 16) for i in range(0, len(val), 2)]
		return {
			'timestamp': datetime.now().astimezone().replace(microsecond=0).isoformat(),
			'mac': ":".join(["{:02X}".format(bytes[i]) for i in range(2,8)]),
			'temperature': (bytes[8] * 256 + bytes[9]) / 10,
			'humidity': bytes[10],
			'battery_percent': bytes[11],
			'battery_volt': (bytes[12] * 256 + bytes[13]) / 1000,
			'count': bytes[14],
		}

def create_TH_request(server, port, idx, temp, hum, comfort, battery):
	url = ''
	url = (
		f"http://{server}:{port}"
		f"/json.htm?type=command&param=udevice&idx={idx}"
		f"&nvalue=0&svalue={temp};{hum};{comfort}"
		f"&battery={battery}")
	logger.info(f"The request is {url}")
	return url

def create_VOLTAGE_request(server, port, idx, voltage):
	url = ''
	url = (
		f"http://{server}:{port}"
		f"/json.htm?type=command&param=udevice&idx={idx}"
		f"&nvalue=0&svalue={voltage}")
	logger.info(f"The request is {url}")
	return url

def send_to_domoticz(url):
	resp = requests.get(url, auth=(config.DOMOTICZ_USERNAME, config.DOMOTICZ_PASSWORD))
	logger.info(f"The response is {resp}")

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

"""
Creates a rotating log
"""
logger = logging.getLogger("Rotating Log")
formatter = logging.Formatter(fmt="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger.setLevel(logging.INFO)

# add a rotating handler
handler = RotatingFileHandler(config.LOG_FILE_NAME, maxBytes=config.LOG_FILE_SIZE, backupCount=1)
handler.setFormatter(formatter)
logger.addHandler(handler)


logger.info("***************************************")
logger.info("Start script...")
logger.info(	f"Input parameters:\r\n"
				f"Domoticz Server IP: {config.DOMOTICZ_SERVER_IP}\r\n"
				f"Domoticz Server Port: {config.DOMOTICZ_SERVER_PORT}\r\n"
				f"Domoticz Server User: {config.DOMOTICZ_USERNAME}\r\n"
				f"Domoticz Server Password: {config.DOMOTICZ_PASSWORD}")

try:
	scanner = Scanner().withDelegate(TempHumDelegate())
	scanner.scan(10.0, passive=True)
except Exception as e:
	logger.error(str(e))
	pass

for number, sensor in config.sensors.items():
	try:
		if sensor['UPDATED'] == False:
			sensor_id = sensor['TH_IDX']
			logger.info(f"TH_IDX:{sensor['TH_IDX']}")
			p = Peripheral(sensor['MAC'])
			p.writeCharacteristic(0x0038, b'\x01\x00', True)	  #enable notifications of Temperature, Humidity and Battery voltage
			p.writeCharacteristic(0x0046, b'\xf4\x01\x00', True)
			p.withDelegate(TempHumDelegate())
			handle_temp_hum_value()
			p.disconnect()
	except Exception as e:
		logger.error(str(e))
		pass
