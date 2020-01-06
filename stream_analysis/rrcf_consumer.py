import rrcf
import numpy as np

class RRCFConsumer():
    def __init__(self, point_transform):
        self.point_transform = point_transform
        self.metrics = {}

        # Setup forest params
        self.forest = None
        self.num_trees = 20
        self.tree_size = 128
        self.ix = 0

        self.generate_forest()

    def generate_forest(self):
        # Create a forest of empty trees
        forest = []
        for _ in range(self.num_trees):
            tree = rrcf.RCTree()
            forest.append(tree)
        self.forest = forest

    def anomaly_detection(self, data):
        for tree in self.forest:
            # If tree is above permitted size, drop the oldest point (FIFO)
            if len(tree.leaves) > self.tree_size:
                tree.forget_point(self.ix - self.tree_size)
                # try:
                #     tree.forget_point(ix - tree_size)
                # except:
                #     pass

            point = self.point_transform(data)
            tree.insert_point(point, index=self.ix)

            # Compute codisp on the new point and take the average among all trees
            if self.ix not in self.metrics:
                self.metrics[self.ix] = {}
                self.metrics[self.ix]['avg_codisp'] = 0

            self.metrics[self.ix]['avg_codisp'] += tree.codisp(self.ix) / self.num_trees
            self.metrics[self.ix]['info'] = data

        self.ix += 1



