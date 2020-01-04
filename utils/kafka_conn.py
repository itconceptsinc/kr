from kafka import KafkaProducer, KafkaConsumer

from config import KAFKA

# Setup connection configs
host = KAFKA['kafka_host']
broker_port = KAFKA['kafka_broker_port']

def connect_kafka_producer():
    # Attempt to create connection to producer
    _producer = None
    try:
        _producer = KafkaProducer(bootstrap_servers=[f'{host}:{broker_port}'])
    except Exception as ex:
        print('Exception while connecting KafkaProducer')
        print(str(ex))
    finally:
        return _producer

def connect_kafka_consumer(topic_name):
    _consumer = None
    try:
        KafkaConsumer(topic_name, auto_offset_reset='earliest',
                      bootstrap_servers=[f'{host}:{broker_port}'], consumer_timeout_ms=1000)
    except Exception as ex:
        print('Exception while connecting to KafkaConsumer')
        print(str(ex))
    finally:
        return _consumer
