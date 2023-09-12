# Xiaomi Mi Temperature and Humidity Monitor 2 - Domoticz

![release](https://img.shields.io/github/v/tag/erdose/xiaomi-mi-lywsd03mmc?label=release) ![Python](https://img.shields.io/badge/python-3.6-brightgreen.svg) ![license](https://img.shields.io/github/license/erdose/xiaomi-mi-lywsd03mmc) ![open_issue](https://img.shields.io/github/issues-raw/erdose/xiaomi-mi-lywsd03mmc) ![closed_issue](https://img.shields.io/github/issues-closed-raw/erdose/xiaomi-mi-lywsd03mmc)

The Xiaomi Mi sensor provides temperature and humidity over BLE.

This script also supports the ATC custom firmware!
Be sure to select [atc1441 format](https://github.com/atc1441/ATC_MiThermometer#advertising-format-of-the-custom-firmware).

![xiaomi_mi_2](Pictures/mi-temperature-and-humidity-monitor-2.jpg)

## How it works

1. ##### Preparing Domoticz

   Create a virtual sensor (Temperature & Humidity) in Domoticz (as much as you need).

   ![virtual_sensor](Pictures/temp_humid.jpg)

   Note the IDX value of virtual sensor (Setup/Devices)!

   ![virtual_sensor_idx](Pictures/temp_idx.jpg)

   If you want to get the raw voltage of battery, you also need to create the Voltage sensors too. The IDX value of the sensor is also required!

   Enable API Basic Auth

   ![basic auth api](Pictures/domoticz-allow-basic-auth.png)

3. ##### Finding the Bluetooth MAC Address of the sensor

   Turn on the Xiaomi Mi sensor (Insert the battery).

   Run the following command to find the MAC address:

   ```shell
   sudo hcitool lescan
   ```

   Example result:

   ```shell
   LE Scan ...
   46:4D:55:28:41:CA (unknown)
   A4:C1:38:DC:8F:2E LYWSD03MMC
   A4:C1:38:4D:D5:F0 ATC_4DD5F0
   ```

   Note down the MAC address!

4. ##### Prepare the required modules

   Install modules:

   ```shell
   sudo apt update
   sudo apt upgrade
   ```

   Wait a minute...

   ```shell
   sudo apt install -y python3 python3-pip git
   sudo pip3 install requests bluepy
   ```

   Check the Python version! It must be at least 3.6 or higher!

5. ##### Edit the *config.py* script

   Clone repository:

   ```shell
   git clone https://github.com/erdose/xiaomi-mi-lywsd03mmc.git
   ```

   Open the ***config.py*** and edit the parameters at the top of the script!

   ```shell
   cd xiaomi-mi-lywsd03mmc
   sudo nano config.py
   ```
   ***DOMOTICZ_CREDENTIALS*** : "username : password" encoded in base 64 https://mixedanalytics.com/tools/basic-authentication-generator/ 
   ```python
   # domoticz configuration
   DOMOTICZ_SERVER_IP = "xxx.xxx.x.xxx"
   DOMOTICZ_SERVER_PORT = "xxxx"
   # username:password base64 encoded
   DOMOTICZ_CREDENTIALS = ""
      ```

   ***MAC*** : MAC address of the Xiaomi Mi sensor.

   ***TH_IDX*** : IDX value of the Temperature & Humidity sensor(s) in Domoticz.

   ***VOLTAGE_IDX*** : IDX value of the Voltage sensor(s) in Domoticz.

   ```python
   # sensor dictionary to add own sensors
   # if you don't want to use the raw voltage option, just write -1 in the VOLTAGE_IDX value field
   sensors = {     1: {"MAC": "xx:xx:xx:xx:xx:xx", "TH_IDX": 1, "VOLTAGE_IDX": -1, "UPDATED": False},
   		2: {"MAC": "xx:xx:xx:xx:xx:xx", "TH_IDX": 2, "VOLTAGE_IDX": -1, "UPDATED": False},
   		3: {"MAC": "xx:xx:xx:xx:xx:xx", "TH_IDX": 3, "VOLTAGE_IDX": -1, "UPDATED": False}}
   ```

   ***TEMPERATURE_PREC***: Accuracy of the temperature value.

   ```python
   # other configuration
   TEMPERATURE_PREC = 2
   ```

   ***LOG_FILE_NAME***: The name of the log file.

   ***LOG_FILE_SIZE***: The size of the log file in bytes.

   ```python
   # Logfile configuration
   LOG_FILE_NAME = 'loginfo.log'
   LOG_FILE_SIZE = 1024	# file size in bytes
   ```

6. ##### Schedule the update interval

   Enable the script to run at a regular interval (5 mins):

   ```shell
   sudo crontab -e
   ```

   Add this line (if you use this path):

   ```shell
   */5 * * * * cd /home/pi/xiaomi-mi-lywsd03mmc && timeout -k 10 60 python3 xiaomiBleLywsd03mmc.py
   ```

   Done!
------
<a href="https://www.paypal.com/donate?hosted_button_id=6G4MHNDWJYKEY">
  <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" alt="Donate with PayPal" />
</a>
