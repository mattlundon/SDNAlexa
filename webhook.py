import logging as log
from datetime import datetime
from flask import Flask, request
from flask_ask import Ask, statement, question
from intents.IntentTable import IntentTable
from intents.block import block_intent, block_for_time
from intents.enable import enable_intent
from intents.utils import sendPhoneNotifiction

# If DEMO = True, then pre-populate with users and devices
DEMO = True
app = Flask(__name__)
ask = Ask(app, "/alexa")
log.getLogger('flask_ask')

# ===== RYU INTENTS =====#
"""
/Ryu - Post request from Ryu
"""
@app.route("/ryu", methods=["POST"])
def ryu():
    req = request.get_json(force=True)
    ryu_new_device_detected(req)
    log.info("New Device Found")
    return "Received"  # <- Without this it just moans...

"""
ryu_new_device_detected 
    - Adds a new device to the device queue
    - If Demo = False, then will send Phone notification
    - If the response has "delete" then it will delete the MAC
"""
def ryu_new_device_detected(req):
    reason = req.get("reason")
    mac = req.get("mac")
    if reason == "add":
        if DEMO:
            d = demoData.pop(0)
            table.add_device(d["device"], mac, d["name"])
            return
        sendPhoneNotifiction("New device found!")
        newDeviceQueue.append(mac)
    elif reason == "delete":
        table.delete_device(mac)


# ===== ALEXA INTENTS =====#
"""
CheckNewDevices
    - Checks for any new devices
    - If none, then say no new devices
    - If there is, ask what they want to call it
"""
@ask.intent("CheckNewDevices")
def check_new_devices():
    if not newDeviceQueue:
        s = "No new devices has been recognized"
    else:
        s = "New device recognized, what do you want to call it?"
    return statement(f"{s}. Anything else?")

"""
NewDevice
    -Adds a new device to itself, or to a user
"""
@ask.intent("NewDevice", mapping={"hostname": "DeviceName", "name": "Name"})
def new_device(hostname, name):
    # If no new devices
    if not newDeviceQueue:
        return question("There are no devices to be added. Anything else?")
    # If it's just the device
    if not name:
        table.add_device(hostname, newDeviceQueue[0])
        s = question(f"{hostname} has been added. Anything else?")
        log.info(f"New Device Added\nDevice - {hostname}")
    # Add device to the name
    else:
        table.add_device(hostname, newDeviceQueue[0], name)
        s = question(f"{hostname} has been added to {name}. Anything else?")
        log.info(f"New Device Added\nUser - {name}\nDevice - {hostname}")
    del newDeviceQueue[0]
    return s

"""
Block
    - Blocks a device based on hostname and or name
"""
@ask.intent("Block", mapping={"hostname": "DeviceName", "name": "Name"})
def block(hostname, name):
    print(datetime.now())
    block_intent(table.get_mac(hostname, name))
    log.info(f"Blocked {hostname}")
    print(datetime.now())
    return question(f"Successfully blocked internet for {hostname}. Anything else?")

"""
Enable
    - Enables a device based on hostname and or name
"""
@ask.intent("Enable", mapping={"hostname": "DeviceName", "name": "Name"})
def enable(hostname, name):
    log.info("Enable Intent Received")
    enable_intent(table.get_mac(hostname, name))
    log.info(f"Enabled {hostname}")
    return question(f"Internet has been enabled for {hostname}. Anything else?")

"""
BlockTime
    - Disables and re-enables a device between 2 times
    - Does this using threads
"""
@ask.intent("BlockTime", mapping={"hostname": "DeviceName", "name": "Name"},
            convert={"start_time": "time", "end_time": "time"})
def block_time(hostname, name, start_time, end_time):
    # Make sure the hostname is valid
    if mac := table.get_mac(hostname, name) or table.get_mac(hostname):
        # We only need the mac for Ryu to process this
        block_for_time(mac, start_time, end_time)
        log.info(f"Blocked {hostname} between {start_time} and {end_time}")
        return question(f"{hostname} has been blocked between {start_time} and {end_time}. Anything else?")
    return statement(f"There is no device called {hostname}. Anything else?")

"""
Bandwidth
    - Checks the mac with the highest usage
    - Calculates based on different of bytes
"""
@ask.intent("Bandwidth")
def band():
    x = table.get_usage()
    if len(x) == 2:
        name, device_name = log
        s = f"{name} is using the most with their {device_name}"
    else:
        s = f"{x} is using the most"
    log.info(f"Bandwidth Intent - {s}")
    return question(f"{s}. Anything else?")

# === Alexa Needed Intents===#
"""
Launch
    - Used when "Open my network" is said
"""
@ask.launch
def launch():
    if not newDeviceQueue:
        return question("Welcome, what would you like to do?")
    return question("Welcome, there is a new device that needs to be added! Say Call it to add it!")

"""
Session Ended
    - Needed when the session ends
"""
@ask.session_ended
def session_ended():
    log.info("Session Ended")
    return "{}", 20

"""
Fallback Intent
    - If an utterance could not be detected
"""
@ask.intent("AMAZON.FallbackIntent")
def fallback():
    log.warning("Unknown Utterance")
    return question("Sorry, I didn't understand that, could you say it again?")


if __name__ == "__main__":
    demoData = [{"name": "John", "device": "Laptop"}, {"name": "John", "device": "Phone"},
                {"name": "John", "device": "PS4"}, {"name": "John", "device": "Xbox"},
                {"name": "Alice", "device": "Laptop"}, {"name": "Alice", "device": "Phone"},
                {"name": "Alice", "device": "Tablet"}, {"name": "Matt", "device": "Laptop"},
                {"name": "Alice", "device": "PS4"}]
    table = IntentTable()
    newDeviceQueue = []
    app.run()
