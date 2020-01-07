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

def get_lines():
    url = 'https://api.wmata.com/Rail.svc/json/jLines'
    req = sesh.get(url, headers=headers)
    lines = req.json().get('Lines', [])

    return lines

def get_line_paths():
    lines = get_lines()

    paths = {}
    for line in lines:
        from_station = line['StartStationCode']
        to_station = line['EndStationCode']
        path_url = f'https://api.wmata.com/Rail.svc/json/jPath?FromStationCode={from_station}&ToStationCode={to_station}'
        req = sesh.get(path_url, headers=headers)
        path = req.json().get('Path', [])

        paths[line] = path

    return paths

def get_station_codes():
    url = 'https://api.wmata.com/Rail.svc/json/jStations'
    req = sesh.get(url, headers=headers)
    stations = req.json().get('Stations', [])

    norm_stations = []
    for station in stations:
        norm_stations.append({
            station['Code'],
            station['name'],
        })
    return norm_stations

def get_station_circuit_ids(line):
    url = 'https://api.wmata.com/TrainPositions/StandardRoutes?contentType=json'
    req = sesh.get(url, headers=headers)
    routes = req.json().get('StandardRoutes', [])

    station_circuits = []
    for route in routes:
        if route.get('LineCode', '') == line:
            for circuit in route.get('TrackCircuits', []):
                if circuit.get('StationCode') is not None:
                    station_circuits.append(circuit)

    return station_circuits

def get_circuit_ids():
    url = 'https://api.wmata.com/TrainPositions/TrackCircuits?contentType=json'
    req = sesh.get(url, headers=headers)

    return req.json().get('TrackCircuits', [])