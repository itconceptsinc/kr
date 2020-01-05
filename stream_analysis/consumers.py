import json
import numpy as np

from data_generation.mongo_wmata_data import get_circuit_ids
from stream_analysis.rrcf_consumer import RRCFConsumer
from utils.kafka_conn import connect_kafka_consumer


def insepct(num_msgs=-1):
    agg_data = []
    for ix, msg in enumerate(train_pos_consumer):
        circuit_data = json.loads(msg.value)
        for data in circuit_data:
            circuit_id = data.get('circuit')
            if circuit_id == 1137 or 2494:
                agg_data.append(data)

        if ix > num_msgs and ix != -1:
            break

    return agg_data

def anomaly_train_pos(train_anomalies, num_msgs=-1):
    for ix, msg in enumerate(train_pos_consumer):
        circuit_data = json.loads(msg.value)
        for data in circuit_data:
            circuit_id = data.get('circuit')
            if circuit_id is None:
                break

            train_anomalies[circuit_id].anomaly_detection(data)

        if ix > num_msgs and ix != -1:
            break


def train_pos_tranform(data):
    point = np.array([
        data.get('cars', -1),
        data.get('direction', -1),
        data.get('seconds_at_location', -1)
    ])
    return point

if __name__ == "__main__":
    circuits = get_circuit_ids()
    circuit_ids = [x['CircuitId'] for x in circuits]

    topic = 'train_positions'
    train_pos_consumer = connect_kafka_consumer(topic)


    train_anomalies = {}
    for circuit_id in circuit_ids:
        train_anomalies[circuit_id] = RRCFConsumer(train_pos_tranform)

    anomaly_train_pos(train_anomalies, 200)



