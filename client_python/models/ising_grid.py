import grid_model
import random
import math

class IsingModel(grid_model.GridModel):
    __fullname__ = 'Voter Model'
 
    update_chart_steps = 1
    update_steps = 1

    def __init__(self):
        super().__init__()
        self.size = 0
        self.set_timer_speed(500)
        self.active_links_chart = None
        self.magnetiz_chart = None
        self.chart_steps = 0

    def handle_property_change(self, prop, value):
        if prop == 'size':
            self._grid(size = value, extfield=self.extfield, temperature=self.temperature, pbc=self.pbc)
        elif prop == 'extfield':
            self._grid(self.size, extfield=value, temperature=self.temperature, pbc = self.pbc)
        elif prop == 'speed':
            self.set_speed(value)
        elif prop == 'temperature':
            self._grid(self.size, self.extfield, temperature=value, pbc = self.pbc)
        elif prop == 'update_steps':
            self.update_steps = value
        elif prop == 'pbc':
            self._grid(self.size, self.extfield, self.temperature, pbc = value)


    def _grid(self, size, extfield, temperature, pbc):
        self.time = 0
        if size <= 0:
            raise ValueError('invalid forest size')
        self.size = size
        self.pbc = pbc
        self.create_grid(size, size, initial_state= lambda row, col: {
            'color': 'black' if random.random() < 0.5 else 'white'
        })
        
        self.active_links_count = 0
        self.magnetization = 0
        for row in range(self.size):
            for col in range(self.size):
                if self.pbc:
                    all_neighs = self.get_cell_neighbors_pbc(row, col)
                else:
                    all_neighs = self.get_cell_neighbors(row,col)
                self.magnetization += self.get_agent_state(row,col)/self.size**2
                for neig in all_neighs:
                    if self.get_agent_state(*neig) != self.get_agent_state(row,col):
                        self.active_links_count += 1/(2*self.size**2)
        self.reset_charts()
        self.extfield = extfield
        self.temperature = temperature

    def create(self):
        size = 10
        speed = 0.8
        extfield = 0
        temperature = 0.5
        update_steps = 1
        pbc = False

        self.add_property('size', 'Grid Size', size, [1, 100], 1)
        self.add_property('extfield', 'External field', extfield, [-1, 1], 'any')
        self.add_property('temperature', 'Temperature', temperature, [0.01, 3], 'any')
        self.add_property('speed', 'Speed', speed, [0, 0.99], 'any')
        self.add_property('update_steps', '# steps per update', update_steps, [1, 300], 10)
        self.add_property_checkbox('pbc', 'PBC', pbc)

        self.magnetiz_chart = self.add_chart('line',
                title='Magnetization',
                xLabel='t',
                yLim = [-1,1],
                size=8)
        self.active_links_chart = self.add_chart('line',
                title='Active links fraction',
                xLabel='t',
                yLim = [0, 1],
                size=8)

        
        self._grid(size, extfield, temperature, pbc)
        self.set_speed(speed)

    def set_speed(self, speed):
        self.speed = speed
        self.set_timer_speed(1000 - speed * 1000)

    def reset(self):
        self._grid(self.size, self.extfield, self.temperature, self.pbc)

    def tick(self):
        
        self.disable_updates()
        
        # Metropolis step - select a random node and flip it
        row = random.randrange(0, self.size)
        col = random.randrange(0, self.size)
        currstate = self.get_agent_state(row,col)
        
        interact = 0
        neigh = self.get_cell_neighbors_pbc(row,col)
        for i,j in neigh:
            interact += self.get_agent_state(i, j)
        moveprob = math.exp(- (2 / self.temperature) * currstate * (self.extfield + interact))
        if(random.random() < moveprob):
            self.set_agent_state(row, col, -currstate)

        self.time += 1

        self.active_links_count = 0
        self.magnetization = 0
        for row in range(self.size):
            for col in range(self.size):
                if self.pbc:
                    all_neighs = self.get_cell_neighbors_pbc(row, col)
                else:
                    all_neighs = self.get_cell_neighbors(row,col)
                self.magnetization += self.get_agent_state(row,col)/self.size**2
                for neig in all_neighs:
                    if self.get_agent_state(*neig) != self.get_agent_state(row,col):
                        self.active_links_count += 1/(2*self.size**2)
        #print(self.active_links_count)
        if self.time % self.update_steps == 0:
            self.enable_updates()
            self.update_charts()
            self.disable_updates()

    def get_agent_state(self, row, col):
        return 1 if self.get_cell_attribute(row, col, 'color') == 'black' else -1

    def set_agent_state(self, row, col, state):
        color = None
        if state == 1:
            color = 'black'
        elif state == -1:
            color = 'white'
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
