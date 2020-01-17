import grid_model
import random
import math

class VoterModel(grid_model.GridModel):
    __fullname__ = 'Voter Model'
 
    update_chart_steps = 1

    def __init__(self):
        super().__init__()
        self.size = 0
        self.set_timer_speed(500)
        self.active_links_chart = None
        self.magnetiz_chart = None
        self.chart_steps = 0

    def handle_property_change(self, prop, value):
        if prop == 'size':
            self._grid(size = value, prob=self.prob, steptype=self.steptype, startconf=self.startconf)
        elif prop == 'probability':
            self._grid(self.size, prob=value, steptype=self.steptype, startconf=self.startconf)
        elif prop == 'steptype':
            self._grid(self.size, self.prob, steptype=value, startconf=self.startconf)
        elif prop == 'speed':
            self.set_speed(value)
        elif prop == 'startconf':
            self._grid(self.size, self.prob, self.steptype, startconf=value)

    def _grid(self, size, prob, steptype, startconf):
        self.time = 0
        if size <= 0:
            raise ValueError('invalid forest size')
        self.size = size

        if prob is not None:
            self.prob = prob
        if startconf == 'Random':
            self.create_grid(size, size, initial_state= lambda row, col: {
                'color': 'red' if random.random() < self.prob else 'blue'
            })
        elif startconf == 'Circle':
            circle_radius = math.sqrt(size**2 * prob / math.pi)
            self.create_grid(size, size, initial_state = lambda row, col: {
                'color': 'red' if (row - size/2)**2 + (col - size/2)**2 <= circle_radius**2 else 'blue'
            })
        elif startconf == 'Strip':
            strip_size = size*prob
            self.create_grid(size, size, initial_state = lambda row, col: {
                'color': 'red' if abs(row - size/2) <= strip_size/2 else 'blue'
            })
        self.active_links_count = 0
        self.magnetization = 0
        for row in range(self.size):
            for col in range(self.size):
                all_neighs = self.get_cell_neighbors(row, col)
                if self.get_agent_state(row,col) == 1:
                    self.magnetization += 1/self.size**2
                for neig in all_neighs:
                    if self.get_agent_state(*neig) != self.get_agent_state(row,col):
                        self.active_links_count += 1/(2*self.size**2)
        self.reset_charts()
        self.steptype = steptype
        self.startconf = startconf

    def create(self):
        size = 50
        speed = 0.1
        prob = 0.5
        steptype = 'Node'
        startconf = 'Random'

        self.add_property('size', 'Grid Size', size, [1, 100], 1)
        self.add_property('probability', 'Initial red fraction', prob, [0, 1], 'any')
        self.add_property('speed', 'Speed', speed, [0, 0.99], 'any')
        self.add_property_selectbox('steptype', 'Dynamics Rule', 'Node', ['Node', 'Link'])
        self.add_property_selectbox('startconf', 'Starting Configuration', 'Random', ['Random', 'Circle', 'Strip'])

        self.magnetiz_chart = self.add_chart('line',
                title='Red fraction',
                xLabel='t',
                yLim = [0,1],
                size=8)
        self.active_links_chart = self.add_chart('line',
                title='Active links fraction',
                xLabel='t',
                yLim = [0, 1],
                size=8)

        
        self._grid(size, prob, steptype, startconf)
        self.set_speed(speed)

    def set_speed(self, speed):
        self.speed = speed
        self.set_timer_speed(1000 - speed * 1000)

    def reset(self):
        self._grid(self.size, self.prob, self.steptype, self.startconf)

    def tick(self):
        self.disable_updates()
        if self.steptype == 'Node':
            # choose random agent
            row = random.randrange(0, self.size)
            col = random.randrange(0, self.size)

            # choose random neighbor
            all_neighs = self.get_cell_neighbors(row, col)
            neigh = random.sample(all_neighs, 1)[0]
            # copy state
            self.set_agent_state(row, col, self.get_agent_state(*neigh))
            self.time += 1/self.size**2

        else:
            # link dynamics: select a random interface
            row = random.randrange(0, self.size)
            col = random.randrange(0, self.size)
            neigh = random.sample(self.get_cell_neighbors(row, col), 1)[0]
            # do nothing if they agree
            if self.get_agent_state(*neigh) == self.get_agent_state(row,col):
                return
            # select one at random if they disagree
            else:
                randstate = random.sample([0, 1], 1)[0]
                self.set_agent_state(neigh[0], neigh[1], randstate)
                self.set_agent_state(row, col, randstate)
                    
                
            self.time += 1/self.size**2

        self.active_links_count = 0
        self.magnetization = 0
        for row in range(self.size):
            for col in range(self.size):
                all_neighs = self.get_cell_neighbors(row, col)
                if self.get_agent_state(row,col) == 1:
                    self.magnetization += 1/self.size**2
                for neig in all_neighs:
                    if self.get_agent_state(*neig) != self.get_agent_state(row,col):
                        self.active_links_count += 1/(2*self.size**2)
        #print(self.active_links_count)
        self.enable_updates()
        self.update_charts()

    def get_agent_state(self, row, col):
        return 1 if self.get_cell_attribute(row, col, 'color') == 'red' else 0

    def set_agent_state(self, row, col, state):
        color = None
        if state == 1:
            color = 'red'
        elif state == 0:
            color = 'blue'
        if color is None:
            raise ValueError('invalid state: {0}'.format(color))
        self.notify_cell_state(row, col, color=color)

    def reset_charts(self):
        self.magnetization = 0
        self.active_links_count = 0

        self.magnetiz_chart.clear_datapoints()
        self.active_links_chart.clear_datapoints()
        self.chart_steps = 0

    def update_charts(self):
         self.chart_steps += 1
         if self.chart_steps >= self.update_chart_steps:
             self.magnetiz_chart.add_datapoint(x=self.time, y=self.magnetization)
             self.active_links_chart.add_datapoint(x=self.time, y=self.active_links_count)
             self.chart_steps = 0
