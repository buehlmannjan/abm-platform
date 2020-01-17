class Graph(object):
    def __init__(self):
        self.num_nodes = 0
        self.clear()

    def clear(self):
        self.adj_list = {}
        self.node_props = {}

    def add_node(self, nodeid):
        if nodeid in self.adj_list:
            raise ValueError('node already in graph {}'.format(nodeid))
        self.adj_list[nodeid] = []
        self.node_props[nodeid] = {}
        self.num_nodes += 1

    def add_edge(self, n0, n1):
        if n1 in self.adj_list[n0]:
            raise ValueError('edge ({},{}) already in graph'.format(n0, n1))
        self.adj_list[n0].append(n1)
        self.adj_list[n1].append(n0)

    def get_node_prop(self, nodeid, prop):
        return self.node_props[nodeid][prop]

    def update_node_props(self, nodeid, **props):
        self.node_props[nodeid].update(props)

    def get_node_neighbors(self, nodeid):
        return self.adj_list[nodeid]

    def iter_nodes(self):
        for n in self.adj_list.keys():
            yield n

    def iter_edges(self):
        for n1, x in self.adj_list.items():
            for n2 in x:
                yield n1, n2
