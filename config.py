# domoticz configuration
DOMOTICZ_SERVER_IP = "xxx.xxx.x.xxx"
DOMOTICZ_SERVER_PORT = "xxxx"
DOMOTICZ_USERNAME = ""
DOMOTICZ_PASSWORD = ""

# sensor dictionary to add own sensors
# if you don't want to use the raw voltage option, just write -1 in the VOLTAGE_IDX value field
sensors = { 1: {"MAC": "xx:xx:xx:xx:xx:xx", "TH_IDX": 1, "VOLTAGE_IDX": -1, "UPDATED": False},
			2: {"MAC": "xx:xx:xx:xx:xx:xx", "TH_IDX": 2, "VOLTAGE_IDX": -1, "UPDATED": False},
			3: {"MAC": "xx:xx:xx:xx:xx:xx", "TH_IDX": 3, "VOLTAGE_IDX": -1, "UPDATED": False}}

# other configuration
TEMPERATURE_PREC = 2

# Logfile configuration
LOG_FILE_NAME = "loginfo.log"
LOG_FILE_SIZE = 16384		# file size in bytes
