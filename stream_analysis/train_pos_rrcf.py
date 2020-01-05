import json
import numpy as np

from utils.wmata_static import get_circuit_ids
from stream_analysis.rrcf_consumer import RRCFConsumer
from utils.kafka_conn import connect_kafka_consumer


class TrainPosRRCF():
    def __init__(self, topic='train_positions'):
        topic = 'train_positions'
        self.consumer = connect_kafka_consumer(topic)

        self.forests = {}
        circuits = get_circuit_ids()
        self.circuit_ids = [x['CircuitId'] for x in circuits]
        for circuit_id in self.circuit_ids:
            self.forests[circuit_id] = RRCFConsumer(self.data_tranform)


    def data_tranform(self, data):
        point = np.array([
            data.get('cars', -1),
            data.get('direction', -1),
            data.get('seconds_at_location', -1)
        ])
        return point

    def process_msgs(self, num_msgs=-1):
        for ix, msg in enumerate(self.consumer):
            circuit_data = json.loads(msg.value)
            all_circuits = set(self.circuit_ids)
            seen_circuits = set()
            for data in circuit_data:
                circuit_id = data.get('circuit')
                if circuit_id is None:
                    break

                self.forests[circuit_id].anomaly_detection(data)
                seen_circuits.add(circuit_id)

            # TODO: Should we insert empty information to maintain number of records?
            unseen_circuits = all_circuits.difference(seen_circuits)
            # for circuit_id in unseen_circuits:
            #     empty_data = {
            #         'cars': -1,
            #         'direction': -1,
            #         'circuit': circuit_id,
            #         'seconds_at_loc': -1
            #     }
            #     self.forests[circuit_id].anomaly_detection(empty_data)

            if ix > num_msgs and ix != -1:
                break

    def get_last_scores(self):
        scores = {}
        for circuit_id in self.circuit_ids:
            ix = self.forests[circuit_id].ix
            if ix > 0:
                scores[circuit_id] = self.forests[circuit_id].metrics[ix-1]

        return scores

    def get_flattened_last_scores(self):
        scores = self.get_last_scores()
        flattened_scores = []
        for score in scores.values():
            flat_score = score['info']
            flat_score['anomaly_score'] = score['avg_codisp']
            flattened_scores.append(flat_score)

        return flattened_scores


if __name__ == "__main__":
    test = TrainPosRRCF()
    test.process_msgs(200)
    scores = test.get_flattened_last_scores()

    print("finished")