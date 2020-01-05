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
for circuit in circuits:
    forest = []
    for _ in range(num_trees):
        tree = rrcf.RCTree()
        forest.append(tree)
    forests[circuit] = forest

# Create a dict to store anomaly score of each point
avg_codisp = {x:{} for x in circuits}

def process_msg(msg):
    pass

def get_anamoly_score():
    # For each shingle...
    global ix
    curr_codisp = {x: [] for x in circuits}
    for msg in consumer:
        data = process_msg(msg)
        for circuit in circuits:
            # For each tree in the forest...
            forest = forests[circuit]
            for tree in forest:
                # If tree is above permitted size, drop the oldest point (FIFO)
                if len(tree.leaves) > tree_size:
                    tree.forget_point(ix - tree_size)
                    # try:
                    #     tree.forget_point(ix - tree_size)
                    # except:
                    #     pass

                tree.insert_point(data[circuit], index=ix)

                # Compute codisp on the new point and take the average among all trees
                if ix not in avg_codisp[circuit]:
                    avg_codisp[circuit][ix] = 0

                avg_codisp[circuit][ix] += tree.codisp(ix) / num_trees

            if avg_codisp[circuit][ix] > 10:
                print(f'At {ix} for {circuit} of {avg_codisp[circuit][ix]} stats were: {data}')
            curr_codisp[circuit].append(avg_codisp[circuit][ix])
        ix = ix + 1

    return curr_codisp