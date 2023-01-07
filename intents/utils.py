import json

import requests
from threading import Timer
from datetime import datetime, timedelta
import time

"""
Please remember to change the Event Name and Webhook key with that found in IFTT.
If DEMO = True, then it will ignore new devices.

API URL should be left default, but in any case, feel free to change it.
"""
IFTTT_EVENT_NAME = "notify"
IFTTT_WEBHOOK_KEY = "kBPlONj7vGab9fbwcDUqbRhoNdFlgOtmZCKXXUYy5w4"
IFTTT_ADDRESS = f"https://maker.ifttt.com/trigger/{IFTTT_EVENT_NAME}/with/key/{IFTTT_WEBHOOK_KEY}"
API_URL = "http://localhost:8080/" #API URL

#Dont send URL - Shortened to just command :)
"""
GetRequest - Send GET request to RYU

Attributes
----------
Command : String
    The endpoint for the RYU REST API Response
    Documentation : https://ryu.readthedocs.io/en/latest/app/ofctl_rest.html
"""
def GetRequest(command):
    return requests.get(API_URL + command).json()

"""
Post Request - Send POST request to RYU

Attributes
----------
Command : String
    The endpoint for the RYU POST Rest API

Data : Dictionary
    Converts given dictionary to JSON to be sent
    Values need to be that which follows documentation
    https://ryu.readthedocs.io/en/latest/app/ofctl_rest.html
"""
def postRequest(command, data):
    #=== Header ===
    '''
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    }
    '''
    response = requests.post(API_URL + command, data=json.dumps(data))
    print(response.text)

"""
sendPhoneNotification - Send notification via IFTTT

Attributes
----------
Message : String
    The message within the notification
"""
def sendPhoneNotifiction(message):
    requests.post(IFTT_ADDRESS, data = {"value1" : message})

"""
getUsage - Gets the byte count of the routing flow for every device
         - Used to calculate the percentage change for bandwidth
         
Return
------
Usage : List
    [MAC : Byte Count] - Used to calculate the amount of bytes a host has TX / RX
"""
def getUsage():
    time.sleep(3)
    flows = GetRequest(f"stats/flow/1")
    print(flows)
    usage = {}
    for x in flows:
        for y in flows[x]:
            mac = y.get("match").get("dl_dst")
            if mac not in usage:
                usage[y.get("match").get("dl_dst")] = y.get("byte_count")
            else:
                num = usage[mac]
                num += y.get("byte_count")
                usage[mac] = num
    print(usage)
    return usage

"""
scheduleTask - Uses threading to start a given function with args

Attributes
----------
StartTime : DateTime
    Specifies the time to start the function.
    If the time has already past, it will start tomorrow
"""
def scheduleTask(starttime, func, args):
    if datetime.combine(datetime.now().date(), starttime).time() < datetime.now().time():
        d = datetime.now().date() + timedelta(days=1)
        interval = (datetime.combine(d, time=starttime) - datetime.now()).total_seconds()
    else:
        interval = (datetime.combine(datetime.now().date(), starttime) - datetime.now()).total_seconds()
    t = Timer(interval=interval, function=func, args=args)
    t.start()








