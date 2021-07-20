class Node:
    def __init__(self, node_of, neighbours, counter, road):
        self.road = road
        self.counter = counter
        self.node_of = node_of
        self.neighbours = neighbours

    def delete_neighbours(self):
        self.neighbours = [x for x in self.neighbours if x not in self.node_of.neighbours and x != self.node_of.road]

        parent = self.node_of
        while parent is not None:
            if parent.road in self.neighbours:
                self.neighbours.remove(parent.road)
            parent = parent.node_of