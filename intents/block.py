from intents.enable import enable_intent
from intents.utils import postRequest
from intents.utils import scheduleTask

"""
block_intent - Blocks a MAC's intent connection

Attributes
----------
Mac - String - Host's MAC to be blocked
"""
def block_intent(mac):
    # Ryu API endpoint
    command = "stats/flowentry/add"
    # Adds a flow where if the src is the given mac, drop packet (Output on port 0)
    data = {
        "dpid": 1,
        "priority": 10000,
        "match": {
            "dl_src": mac
        },
        "actions": [
            {
                "type": "OUTPUT",
                "port": 0,

            }
        ],
    }
    # Send Flow to Ryu
    postRequest(command, data)

"""
block_for_time

Attributes
----------
mac - String - Hostname's mac to block between 2 periods
start_time   - Time when the block should start
end_time     - Time when the block show stop, so we enable it
"""
def block_for_time(mac, start_time, end_time):
    scheduleTask(start_time, block_intent, args=mac)
    scheduleTask(end_time, enable_intent, args=mac)
