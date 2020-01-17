import grid_model
import random

class VoterModel(grid_model.GridModel):
    __fullname__ = 'Voter Model'

    def __init__(self):
        super().__init__()
        self.size = 0
        self.set_timer_speed(500)

    def handle_property_change(self, prop, value):
        if prop == 'size':
            self._grid(value)
        elif prop == 'probability':
            self._grid(self.size, prob=value)

    def _grid(self, size, prob=None):
        if size <= 0:
            raise ValueError('invalid forest size')
        self.size = size

        if prob is not None:
            self.prob = prob
        self.create_grid(size, size, initial_state= lambda row, col: {
            'color': 'black' if random.random() < self.prob else 'white'
        })

    def create(self):
        size = 50
        speed = 0.1
        prob = 0.5

        self.add_property('size', 'Grid Size', size, [1, 100], 1)
        self.add_property('probability', 'Probability', prob, [0, 1], 'any')
        self.add_property('speed', 'Speed', speed, [0, 1], 'any')

        self._grid(size, prob=prob)
        self.set_speed(speed)

    def set_speed(self, speed):
        self.speed = speed
        self.set_timer_speed(1000 - speed * 1000)

    def reset(self):
        self._grid(self.size, prob=self.prob)

    def tick(self):
        # choose random agent
        row = random.randrange(0, self.size)
        col = random.randrange(0, self.size)

        # choose random neighbor
        all_neighs = self.get_cell_neighbors(row, col)
        neigh = random.sample(all_neighs, 1)[0]

        # copy state
        self.set_agent_state(row, col, self.get_agent_state(*neigh))

    def get_agent_state(self, row, col):
        return 1 if self.get_cell_attribute(row, col, 'color') == 'black' else 0

    def set_agent_state(self, row, col, state):
        color = None
        if state == 1:
            color = 'white'
        elif state == 0:
            color = 'black'
        if color is None:
            raise ValueError('invalid state: {0}'.format(color))
        self.notify_cell_state(row, col, color=color)

    def reset(self):
        self._grid(self.size, prob=self.prob)
