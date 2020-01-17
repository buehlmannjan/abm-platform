import graph
import model

class GraphModel(model.Model):
    """Defines a model in which each agent is a node on a graph"""
    def __init__(self, config=None):
        self.graph = graph.Graph()
        super().__init__(config)

    def clear(self):
        self.graph.clear()
        self.send('clear')

    def add_node(self, nodeid, color='black', **kwargs):
        """Adds node nodeid to the graph.

        Defaults to color black. Additionally defines attributes in kwargs.
        """
        self.graph.add_node(nodeid)
        props = { 'color': color }
        props.update(kwargs)
        self.graph.update_node_props(nodeid, **props)
        self.send('add_node', id=nodeid, props=props)

    def add_edge(self, n0, n1):
        """Adds edge (n0, n1) to the graph."""
        self.graph.add_edge(n0, n1)
        self.send('add_edge', source=n0, target=n1)

    def set_model_type(self):
        super().set_model_type(type='graph', config=self.config)

    def get_node_prop(self, nodeid, prop):
        """Returns prop property from node nodeid."""
        return self.graph.get_node_prop(nodeid, prop)

    def update_node_props(self, nodeid, **props):
        """Updates node properties dictionary for node nodeid with props"""
        self.send('update_node_props', id=nodeid, props=props)
        return self.graph.update_node_props(nodeid, **props)

    def get_node_neighbors(self, nodeid):
        """Returns a list of the neighbouring nodes of nodeid."""
        return self.graph.get_node_neighbors(nodeid)

    def node_iterator(self):
        """Returns an iterator to the nodes of the graph. """
        return self.graph.iter_nodes()

    def edge_iterator(self):
        """Returns an iterator to the edges of the graph. """
        return self.graph.iter_edges()

    def get_agent_state(self, nodeid):
        """Returns agent state of node nodeid."""
        return self.get_node_prop(nodeid, 'color')

    def set_agent_state(self, nodeid, state):
        """Sets agent state of node nodeid.
        Override this method to compose more complex states"""
        return self.update_node_props(nodeid, color=state)
