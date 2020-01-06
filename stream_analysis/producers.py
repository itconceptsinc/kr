import sys, json, time, os

from google.protobuf import json_format
from google.transit import gtfs_realtime_pb2

try:
    fileDir = os.path.dirname(os.path.abspath(__file__))
    parentDir = os.path.dirname(fileDir)
    sys.path.insert(0, parentDir)
except NameError:
    pass

from config import DEBUG, KAFKA
from stream_analysis.generic_producer import CustomProducer

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


if __name__ == "__main__":
    TIME_TO_WAIT = 5 * 60
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

    if DEBUG:
        train_gtfs_producer.produce(2)
        [x.produce(250) for x in producers]
        sys.exit()

    while True:
        [x.produce(1) for x in producers]
        time.sleep(TIME_TO_WAIT)