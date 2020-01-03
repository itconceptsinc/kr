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
                {"epoch_time": -1}
            )
        return doc
    
    def process_data(self, data):
        """Converts the document to a kafka message"""
        results = modifier(data)
        return results

    def advance_stream(self, doc, seconds=None):
        """Advance the datetime of the stream"""
        if seconds:
            new_datetime = np.ceil(doc['epoch_time']) + seconds
            self.curr_datetime = new_datetime
        else:
            self.curr_datetime = np.ceil(doc['epoch_time'])

    def publish_msg(self, value, key=None):
        try:
            key_bytes = bytes(key, encoding='utf-8')
            value_bytes = bytes(value, encoding='utf-8')
            producer_instance.send(topic_name, key=key_bytes, value=value_bytes)
            producer_instance.flush()
        except Exception as ex:
            print('Exception in publishing message')

    def produce(self):
        doc = self.get_record()
        self.advance_stream()
        msg = self.process_data(doc['data'])
        self.publish_msg(msg)


if __name__ == "__main__":
    producer = CustomProducer('test_topic', 1578035628, lambda x: 1, "train_incidents")
    producer.get_record()