import sys, requests, json, time, os

fileDir = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.dirname(fileDir)
sys.path.insert(0, parentDir)


from utils.mongo_conn import get_mongo_db
from datetime import datetime, timedelta
from timeloop import Timeloop

from config import WMATA

headers = {'api_key': WMATA['api_key']}
sesh = requests.Session()
t1 = Timeloop()
TIME_TO_WAIT = 5 * 60


def get_line_codes():
    line_url = 'https://api.wmata.com/Rail.svc/json/jLines'
    req = sesh.get(line_url, headers=headers)
    lines = req.json().get('Lines', [])
    line_codes = [x['LineCode'] for x in lines]

    return line_codes

def save_elevator_incidents():
    url = 'https://api.wmata.com/Incidents.svc/json/ElevatorIncidents'
    req = sesh.get(url, headers=headers)
    data = {
        'epoch_time': datetime.utcnow().timestamp(),
        'data': req.json()
    }
    elevator_incidents_db.insert_one(data)


def save_train_incidents():
    url = 'https://api.wmata.com/Incidents.svc/json/Incidents'
    req = sesh.get(url, headers=headers)
    data = {
        'epoch_time': datetime.utcnow().timestamp(),
        'data': req.json()
    }
    train_incidents_db.insert_one(data)


def save_train_positions():
    url = 'https://api.wmata.com/TrainPositions/TrainPositions?contentType=json'
    req = sesh.get(url, headers=headers)
    data = {
        'epoch_time': datetime.utcnow().timestamp(),
        'data': req.json()
    }
    train_position_db.insert_one(data)


def save_train_arrivals(train_arrivals):
    data = {
        'epoch_time': datetime.utcnow().timestamp(),
        'data': {'Trains': train_arrivals}
    }
    train_arrivals_db.insert_one(data)

def get_train_arrivals(station_code):
    train_arrival_url = f'https://api.wmata.com/StationPrediction.svc/json/GetPrediction/{station_code}'
    req = sesh.get(train_arrival_url, headers=headers)
    return req.json().get('Trains', [])


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

@t1.job(interval=timedelta(seconds=TIME_TO_WAIT))
def get_train_data():
    try:
        save_train_incidents()
        save_train_positions()
        save_elevator_incidents()

        train_arrivals = []
        for ix, station in enumerate(stations):
            train_arrivals.extend(get_train_arrivals(station['Code']))
            if ix % 7 == 0:
                time.sleep(1)
        save_train_arrivals(train_arrivals)


    except Exception as err:
        with open('error.txt', 'a') as txt_file:
            txt_file.write(f'{err}\n')


if __name__ == "__main__":
    db = get_mongo_db()
    train_position_db = db.train_positions
    train_arrivals_db = db.train_arrivals
    train_incidents_db = db.train_incidents
    elevator_incidents_db = db.elevator_incidents

    stations = get_station_codes()

    t1.start(block=True)
