import sys, json, time, os

from timeloop import Timeloop
from datetime import timedelta
from google.protobuf import json_format
from google.transit import gtfs_realtime_pb2

try:
    fileDir = os.path.dirname(os.path.abspath(__file__))
    parentDir = os.path.dirname(fileDir)
    sys.path.insert(0, parentDir)
except NameError:
    pass

from config import KAFKA
from stream_analysis.generic_producer import CustomProducer

t1 = Timeloop()
TIME_TO_WAIT = 5 * 60

def train_pos_func(data):
    msg = []

    positions = data.get('TrainPositions', [])
    for pos in positions:
        pos_data = {
            'cars': pos['CarCount'],
            'direction': pos['DirectionNum'],
            'circuit': pos['CircuitId'],
            'seconds_at_loc': pos['SecondsAtLocation']
        }
        msg.append(pos_data)
    return msg


def train_gtfs_func(data):
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(data)
    decoded_data = json.loads(json_format.MessageToJson(feed))
    return decoded_data


@t1.job(interval=timedelta(seconds=TIME_TO_WAIT))
def produce():
    [x.produce(1) for x in producers]


if __name__ == "__main__":
    train_position_producer = CustomProducer(
        'train_positions',
        KAFKA['start_utc'],
        train_pos_func,
        'train_positions'
    )

    train_gtfs_producer = CustomProducer(
        'train_gtfs',
        KAFKA['start_utc'],
        train_gtfs_func,
        'train_positions_gtfs'
    )

    producers = [train_position_producer, train_gtfs_producer]

    # TODO: Should this be run by default or in debug?
    train_gtfs_producer.produce(produce_all=True)
    train_position_producer.produce(produce_all=True)
    # [x.produce(250) for x in producers]

    t1.start(block=True)
