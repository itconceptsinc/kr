import sys, requests, json, time, os

try:
    fileDir = os.path.dirname(os.path.abspath(__file__))
    parentDir = os.path.dirname(fileDir)
    sys.path.insert(0, parentDir)
except NameError:
    pass

from stream_analysis.generic_producer import CustomProducer

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

train_position_producer = CustomProducer(
    'train_positions',
    1578035626,
    train_pos_func,
    'train_positions',
)

while True:
    train_position_producer.produce(200)
    time.sleep(TIME_TO_WAIT)