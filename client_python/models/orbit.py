import fixed_graph_model
import math

class OrbitModel(fixed_graph_model.FixedGraphModel):
    """Example that demonstrates fixed-size viewports

    A central node is orbited by another node, both are connected through a single link"""
    max_x = 400
    max_y = 800

    __fullname__ = "Orbit"

    def handle_property_change(self, prop, value):
        if prop == 'speed':
            self.set_timer_speed(value * 1000) # speed in ms
        elif prop == 'r':
            self.r = value
        elif prop == 'dt':
            self.dt = value / 100

    def create(self):
        self.r = 100
        self.t = 0.0
        self.center = [self.max_x / 2, self.max_y / 2]

        self.add_node(0,
                x=self.center[0],
                y=self.center[1])

        self.add_node(1,
                x=self.center[0] + self.r * math.cos(self.t),
                y=self.center[1] + self.r * math.sin(self.t))

        self.add_edge(0, 1)

        self.dt = 2*math.pi / 360

        self.add_property('speed', 'Speed', 0.1, [0,1], 'any')
        self.add_property('r', 'Radius', self.r, [0,self.r], 1)
        self.add_property('dt', 'Step', round(self.dt * 100, 2),
                [round(2*math.pi / 360 * 100, 2), round(2*math.pi / 180 * 100, 2)], 0.01)

    def tick(self):
        self.t += self.dt
        self.update_node_props(1,
                x=self.center[0] + self.r * math.cos(self.t),
                y=self.center[1] + self.r * math.sin(self.t))
        if self.t >= 2*math.pi:
            self.t -= 2*math.pi

    def reset(self):
        pass

    def viewport(self):
        return [0, 0, self.max_x, self.max_y]
