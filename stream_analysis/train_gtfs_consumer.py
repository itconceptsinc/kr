import sys, os, json
import numpy as np

import json
import pandas as pd
from pandas.io.json import json_normalize
import datetime

try:
    fileDir = os.path.dirname(os.path.abspath(__file__))
    parentDir = os.path.dirname(fileDir)
    sys.path.insert(0, parentDir)
except:
    pass

from utils.kafka_conn import connect_kafka_consumer


class TrainGTFS():
    def __init__(self, topic='train_positions'):
        topic = 'train_gtfs'
        self.consumer = connect_kafka_consumer(topic)
        self.stop_times = pd.read_csv('../static/stop_times.txt')
        self.data_lst = []

    def process_msgs(self, num_msgs=-1):
        for ix, msg in enumerate(self.consumer):
            a = json_normalize(json.loads(msg.value))
            if 'entity' in a:
                b = json_normalize(a.entity[0])

                # Filtering data to only keep the relevant ones for delta calculation
                if 'vehicle.stopId' in b:
                    c = b[~b['vehicle.stopId'].isnull()].copy()
                    c = c[c['vehicle.currentStatus'].str.contains('INCOMING_AT|STOPPED_AT')]
                    c = c[c['vehicle.trip.scheduleRelationship'] == 'SCHEDULED'].reset_index()
                    c['vehicle.stopId'] = c['vehicle.stopId'].astype('int')
                    c['vehicle.trip.tripId'] = c['vehicle.trip.tripId'].astype('int64')
                    c['vehicle.timestamp'] = pd.to_datetime(c['vehicle.timestamp'], unit='s')

                    # for every b, calculate delta
                    c['ExpectedArrival'] = 0
                    # Note that Expected Arrival includes day and is set to UTC given 5 hour addition (hack)

                    for i in range(len(c)):
                        tmp = self.stop_times[
                            (self.stop_times['trip_id'] == c['vehicle.trip.tripId'][i]) &
                            (self.stop_times['stop_id'] == c['vehicle.stopId'][i])
                        ]
                        # print(tmp)
                        if len(tmp) > 0:
                            time = tmp.arrival_time.values[0]
                            hr_e = float(time.split(':')[0])
                            day = datetime.datetime.strptime(c.loc[[i], ['vehicle.trip.startDate']].values[0][0],
                                                             '%Y%m%d')

                            if hr_e >= 24:
                                time = '0' + str(int(hr_e - 24)) + time[2:]
                                day = day + datetime.timedelta(days=1)

                            time = datetime.datetime.strptime(time, '%H:%M:%S')
                            c.loc[[i], ['ExpectedArrival']] = datetime.datetime.combine(day,
                                                                                        time.time()) + datetime.timedelta(
                                hours=5)

                    c['delta'] = c['vehicle.timestamp'] - pd.to_datetime(c['ExpectedArrival'])
                    c.delta = c.delta.dt.total_seconds()

                    c2 = b.join(c.set_index('index')[['ExpectedArrival', 'delta']])
                    # TODO: Should we still concat these in the stream?
                    # data = pd.concat([data, c2])
                    self.data_lst.append(c2)

            if ix > num_msgs and ix > 0:
                break


    def get_past_data(self, num=1):
        return self.data_lst[-num:]


if __name__ == "__main__":
    test = TrainGTFS()
    test.process_msgs(5)
    scores = test.get_past_data()

    print("finished")