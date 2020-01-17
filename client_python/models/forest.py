import grid_model
import random

class TreeState(object):
    ALIVE = 'green'
    BURNING = 'red'
    DEAD = 'black'
    EMPTY = 'white'

class ForestFireModel(grid_model.GridModel):
    __fullname__ = 'Forest Fire'

    burn_steps = 20
    update_chart_steps = 1

    def __init__(self):
        super().__init__()
        self.size = 0
        self.set_timer_speed(500)
        self.burning_count_chart = None
        self.chart_steps = 0
        self.alive_orig_count = 0

    def handle_property_change(self, prop, value):
        if prop == 'size':
            #self.clear()
            self.forest(value)
        elif prop == 'probability':
            self.forest(self.size, prob=value)
        elif prop == 'speed':
            self.set_speed(value)

    def handle_agent_clicked(self, data):
        row = data['row']; col = data['col']
        if self.get_agent_state(row, col) == TreeState.ALIVE:
            self.set_on_fire(row, col)

    def set_on_fire(self, row, col):
        self.burning_count += 1
        self.alive_count -= 1
        self.set_agent_state(row, col, TreeState.BURNING)
        self.update_charts()

    def stop_condition(self):
        return self.alive_count == 0 and self.burning_count == 0

    def start_fire(self):
        if self.get_agent_state(0, 0) == TreeState.ALIVE:
            self.set_on_fire(0, 0)
        elif self.get_agent_state(0, self.cols-1) == TreeState.ALIVE:
            self.set_on_fire(0, self.cols-1)
        elif self.get_agent_state(self.rows-1, 0) == TreeState.ALIVE:
            self.set_on_fire(self.rows-1, 0)
        elif self.get_agent_state(self.rows-1, self.cols-1) == TreeState.ALIVE:
            self.set_on_fire(self.rows-1, self.cols-1)

    def forest(self, size, prob=None, rebuild=True):
        if size <= 0:
            raise ValueError('invalid forest size')
        self.burning_count = 0
        old_size = self.size
        self.size = size

        if prob is not None:
            self.prob = prob
        if rebuild:
            self.create_grid(
                    size,
                    size,
                    initial_state=
                        lambda row, col: {'color': TreeState.ALIVE if random.random() < self.prob else TreeState.EMPTY}
            )
            self.alive_orig_count = 0
            for i in range(size):
                for j in range(size):
                    if self.get_agent_state(i, j) == TreeState.ALIVE:
                        self.alive_orig_count += 1
        else:
            if old_size != size:
                raise ValueError('forest size change with rebuild=False')
            self.disable_updates()
            for i in range(size):
                for j in range(size):
                    cur_state = self.get_agent_state(i, j)
                    if cur_state != TreeState.EMPTY:
                        self.set_agent_state(i, j, TreeState.ALIVE)
            self.enable_updates()

        self.reset_charts()

        # reset initial number of steps
        for i in range(size):
            for j in range(size):
                self.update_cell_state(i, j, steps=0)

        #self.start_fire()

    def create(self):
        size = 50
        speed = 0.1
        prob = 0.5

        self.add_property('size', 'Grid Size', size, [1, 100], 1)
        self.add_property('probability', 'Probability', prob, [0, 1], 'any')
        self.add_property('speed', 'Speed', speed, [0, 1], 'any')

        self.burning_count_chart = self.add_chart('ts',
                title='Burning Count',
                xLabel='t')
        self.cell_stats_chart = self.add_chart('bar',
                title='Cell Stats',
                yLabel='Count',
                xLabel='State',
                )

        self.forest(size, prob=prob)
        self.set_speed(speed)

    def reset(self):
        self.forest(self.size, prob=self.prob, rebuild=False)

    def set_speed(self, speed):
        self.speed = speed
        self.set_timer_speed(1000 - speed * 1000)

    def burn(self):
        burning = set()
        to_burn = set()

        self.disable_updates()

        for i in range(self.size):
            for j in range(self.size):
                if self.get_agent_state(i, j) == TreeState.BURNING:
                    burning.add((i, j))
                    for neig_i, neig_j in self.iterate_cell_neighbors(i, j):
                        if self.get_agent_state(neig_i, neig_j) == TreeState.ALIVE:
                            to_burn.add((neig_i, neig_j))

        for i, j in burning:
            steps = self.get_cell_attribute(i, j, 'steps')
            if steps < self.burn_steps:
                self.update_cell_state(i, j, steps=steps+1)
            else:
                self.set_agent_state(i, j, TreeState.DEAD)
                self.dead_count += 1
                self.burning_count -= 1

        for i, j in to_burn:
            self.set_agent_state(i, j, TreeState.BURNING)
            self.burning_count += 1
            self.alive_count -= 1

        self.update_charts()

        self.enable_updates()

    def reset_charts(self):
        self.alive_count = self.alive_orig_count
        self.burning_count = 0
        self.dead_count = 0

        self.burning_count_chart.clear_datapoints()
        self.chart_steps = 0

        self.cell_stats_chart.clear_datapoints()
        self.cell_stats_chart.update_config(yLim=[0, self.alive_count])
        self.cell_stats_chart.add_datapoint('Alive', self.alive_count)
        self.cell_stats_chart.add_datapoint('Burning', self.burning_count)
        self.cell_stats_chart.add_datapoint('Dead', self.dead_count)

    def update_charts(self):
        self.chart_steps += 1
        if self.chart_steps >= self.update_chart_steps:
            self.burning_count_chart.add_datapoint((self.burning_count + self.dead_count) / self.alive_orig_count)
            self.chart_steps = 0

        self.cell_stats_chart.update_datapoints([
            ('Alive', self.alive_count),
            ('Burning', self.burning_count),
            ('Dead', self.dead_count)
        ])

    def tick(self):
        print('calling tick')
        self.burn()
