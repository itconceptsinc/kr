import json

import numpy as np
from datetime import timedelta
from timeloop import Timeloop

from utils.kafka_conn import connect_kafka_producer
from utils.mongo_conn import get_mongo_db

class CustomProducer():

    def __init__(self, topic, init_datetime, func, mongo_coll,
                    producer=connect_kafka_producer(),
                    mongo_db=get_mongo_db()):
        self.topic = topic
        self.init_datetime = init_datetime
        self.curr_datetime = init_datetime
        self.modifier = func
        self.producer = producer
        self.mongo_coll = mongo_db[mongo_coll]

        self.timer = Timeloop()


    def get_record(self):
        """Gets the next mongo document for the stream"""
        doc = self.mongo_coll.find_one(
            {"epoch_time": {"$gt": self.curr_datetime}},
            sort=[('epoch_time', 1)]
        )
        return doc
    
    def process_data(self, data):
        """Converts the document to a kafka message"""
        results = self.modifier(data)
        return results

    def advance_stream(self, doc=None, seconds=None):
        """Advance the datetime of the stream"""
        if seconds:
            self.curr_datetime += seconds
        elif doc:
            self.curr_datetime = np.ceil(doc['epoch_time'])

    def publish_msg(self, value, key=''):
        try:
            key_bytes = bytes(key, encoding='utf-8')
            value_bytes = bytes(json.dumps(value), encoding='utf-8')
            self.producer.send(self.topic, key=key_bytes, value=value_bytes)
            self.producer.flush()
        except Exception as ex:
            print('Exception in publishing message')

    def produce(self, itr=1, produce_all=False):
        ix = 0
        while ix < itr or produce_all:
            doc = self.get_record()
            self.advance_stream(doc)
            if doc and doc.get('data'):
                msg = self.process_data(doc['data'])
                self.publish_msg(msg)
            else:
                break

            ix += 1


if __name__ == "__main__":
    producer = CustomProducer('test_topic', 1578035628, lambda x: 1, "train_incidents")
    producer.get_record()