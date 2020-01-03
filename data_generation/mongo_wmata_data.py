import requests, json, time

import numpy as np

from data_generation.mongo_conn import get_connection
from datetime import datetime
from config import WMATA
from time import sleep

headers = {'api_key': WMATA['api_key']}
sesh = requests.Session()


def get_line_codes():
    line_url = 'https://api.wmata.com/Rail.svc/json/jLines'
    req = sesh.get(line_url, headers=headers)
    lines = req.json().get('Lines', [])
    line_codes = [x['LineCode'] for x in lines]

    return line_codes

def get_elevator_incidents():
    url = 'https://api.wmata.com/Incidents.svc/json/ElevatorIncidents'
    req = sesh.get(url, headers=headers)
    data = {
        'epoch_time': datetime.utcnow().timestamp(),
        'data': req.json()
    }
    elevator_incidents_db.insert_one(data)


def get_train_incidents():
    url = 'https://api.wmata.com/Incidents.svc/json/Incidents'
    req = sesh.get(url, headers=headers)
    data = {
        'epoch_time': datetime.utcnow().timestamp(),
        'data': req.json()
    }
    train_incidents_db.insert_one(data)


def get_train_positions():
    url = 'https://api.wmata.com/TrainPositions/TrainPositions?contentType=json'
    req = sesh.get(url, headers=headers)
    data = {
        'epoch_time': datetime.utcnow().timestamp(),
        'data': req.json()
    }
    train_position_db.insert_one(data)


def get_train_arrivals(station_code):
    train_arrival_url = f'https://api.wmata.com/StationPrediction.svc/json/GetPrediction/{station_code}'
    req = sesh.get(train_arrival_url, headers=headers)
    data = {
        'epoch_time': datetime.utcnow().timestamp(),
        'data': req.json()
    }
    train_arrivals_db.insert_one(data)


def get_station_codes():
    train_station_url = 'https://api.wmata.com/Rail.svc/json/jStations'
    req = sesh.get(train_station_url, headers=headers)
    station_info = req.json()

    stations = []
    seen_stations = set()
    for station in station_info['Stations']:
        if station['Name'] not in seen_stations:
            stations.append({
                'Name': station['Name'],
                'Code': station['Code'],
                'Lat': station['Lat'],
                'Lon': station['Lon']
            })
            seen_stations.add(station['Name'])

    return stations

if __name__ == "__main__":
    client = get_connection()
    db = client['wmata']
    train_position_db = db.train_positions
    train_arrivals_db = db.train_arrivals
    train_incidents_db = db.train_incidents
    elevator_incidents_db = db.elevator_incidents

    stations = get_station_codes()

    while True:
        try:
            get_train_incidents()
            get_train_positions()
            get_elevator_incidents()

            for ix, station in enumerate(stations):
                get_train_arrivals(station['Code'])
                if ix % 7 == 0:
                    time.sleep(1)

            time.sleep(45)
        except:
            time.sleep(60)

