import rrcf
import numpy as np
import pandas as pd

from kafka import KafkaConsumer
from utils.kafka_conn import connect_kafka_consumer
from data_generation.mongo_wmata_data import get_circuit_ids

consumer = connect_kafka_consumer('train_positions')
circuits = get_circuit_ids()

# Set tree parameters
num_trees = 20
shingle_size = 4
tree_size = 25
ix = 0

# Create a forest of empty trees
forests = {}
for line in line_codes:
    forest = []
    for _ in range(num_trees):
        tree = rrcf.RCTree()
        forest.append(tree)
    forests[line] = forest