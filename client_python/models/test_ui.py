import graph_model

class TestUIModel(graph_model.GraphModel):
    """Test for UI Elements"""

    __fullname__ = "Test UI"

    def handle_property_change(self, prop, value):
        if prop == 'speed':
            self.set_timer_speed(value * 1000) # speed in ms
        elif prop == 'threenodes':
            if value:
                self.add_node('n2')
                self.add_edge('n0', 'n2')
            else:
                # remove
                pass
        elif prop == 'color':
            self.color = value

    def create(self):
        self.color = 'blue'

        self.add_property_slider('speed', 'Speed', 0.1, [0,1], 'any')
        self.add_property_checkbox('threenodes', '3 Nodes', False)
        self.add_property_selectbox('color', 'Cycling Color', 'blue', ['blue', 'red', 'green'])

        # define graph
        self.add_node('n0')
        self.add_node('n1')
        self.add_edge('n0', 'n1')

    def tick(self):
        # cycle n0 color
        if self.get_node_prop('n0', 'color') == 'black':
            self.update_node_props('n0', color=self.color)
        else:
            self.update_node_props('n0', color='black')

    def reset(self):
        pass
