import graph_model

class SimpleGraphModel(graph_model.GraphModel):
    def handle_property_change(self, prop, value):
        if prop == 'speed':
            self.set_timer_speed(value * 1000) # speed in ms
    def create(self):
        self.add_property('speed', 'Speed', 0.1, [0,1], 'any')
        # define graph
        self.add_node('n0')
        self.add_node('n1')
        self.add_edge('n0', 'n1')
    def tick(self):
        # cycle n0 color
        if self.get_node_prop('n0', 'color') == 'black':
            self.update_node_props('n0', color='blue')
        else:
            self.update_node_props('n0', color='black')
    def reset(self):
        pass
