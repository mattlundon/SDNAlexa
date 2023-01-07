from intents.utils import postRequest
def enable_intent(mac):
    """
    In order to enable internet, we just need to find
    the flow that disabled it, and delete it
    """
    command = "stats/flowentry/delete"
    data = {
        "dpid": 1,
        "match": {
            "dl_src": mac
        },
        "instructions": [
            {
                "type": "OUTPUT",
                "port": 0
            }
        ]
    }
    # Send flow to Ryu
    postRequest(command, data)
