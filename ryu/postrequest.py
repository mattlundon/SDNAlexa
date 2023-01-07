import time

import requests
API_URL = "http://localhost:5000/ryu"

def post_request(data):
    try:
        requests.post(API_URL, json=data, verify=False)
    except:
        time.sleep(2)
        post_request(data)
