import sys, requests, json, time, os

try:
    fileDir = os.path.dirname(os.path.abspath(__file__))
    parentDir = os.path.dirname(fileDir)
    sys.path.insert(0, parentDir)
except:
    pass

from config import WMATA
headers = {'api_key': WMATA['api_key']}
sesh = requests.Session()


def get_line_codes():
    line_url = 'https://api.wmata.com/Rail.svc/json/jLines'
    req = sesh.get(line_url, headers=headers)
    lines = req.json().get('Lines', [])
    line_codes = [x['LineCode'] for x in lines]

    return line_codes

def get_circuit_ids():
    url = 'https://api.wmata.com/TrainPositions/TrackCircuits?contentType=json'
    req = sesh.get(url, headers=headers)

    return req.json().get('TrackCircuits', [])