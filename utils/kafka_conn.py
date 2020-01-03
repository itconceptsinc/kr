from kafka import KafkaProducer

from config import KAFKA

def connect_kafka_producer():
    # Setup connection configs
    host = KAFKA['host']
    port = KAFKA['kafka_broker_port']

    # Attempt to create connection to producer
    _producer = None
    try:
        _producer = KafkaProducer(bootstrap_servers=[f'{host}:{broker_port}'])
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    finally:
        return _producer