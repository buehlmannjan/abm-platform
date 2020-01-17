import grid_model
import random

class HouseState(object):
    RACE1 = 'yellow'
    RACE2 = 'red'
    EMPTY = 'white'

class ShellingModel(grid_model.GridModel):

    update_chart_steps = 1

    def __init__(self):
        super().__init__()
        self.set_timer_speed(500)
        self.chart_steps = 0
        self.frustration_chart = None

    def handle_property_change(self, prop, value):
        if (prop == 'size'):
            #self.clear()
            self.shelling(size=value)
        elif prop == 'probability':
            self.shelling(self.size, prob=value)
        elif prop == 'similarity':
            self.shelling(self.size, self.prob, simil=value)
        elif prop == 'imbalance':
            self.shelling(self.size, self.prob, self.simil, imb=value)
        elif prop == 'speed':
            self.set_speed(value)


    def shelling(self, size, prob=None, simil=None, imb=None):
        self.size = size
        if prob is not None:
            self.prob = prob
        if simil is not None:
            self.simil = simil
        if imb is not None:
            self.imb = imb
        self.create_grid(
                size,
                size,
                initial_state=
                    lambda row, col: {'color': random.choices(population = [HouseState.RACE1, HouseState.RACE2], weights = [self.imb, 1 - self.imb], k = 1)[0] if random.random() < self.prob else HouseState.EMPTY}
        )
        self.reset_charts()

    def create(self):
        size = 50
        speed = 0.1
        prob = 0.5
        imb = 0.5
        simil = 0.5

        self.add_property('size', 'Grid Size', size, [1, 100], 1)
        self.add_property('probability', 'Occupancy', prob, [0, 1], 'any')
        self.add_property('similarity', 'Similarity Threshold', simil, [0, 1], 'any')
        self.add_property('speed', 'Speed', speed, [0, 1], 'any')
        self.add_property('imbalance', 'Color Imbalance', imb, [0,1], 'any')

        self.frustration_chart = self.add_chart('ts',
            title='Conflicting neighborhoods',
            xLabel='t',
            size=8)

        self.shelling(size, prob=prob, simil=simil, imb=imb)
        self.set_speed(speed)

    def set_speed(self, speed):
        self.speed = speed
        self.set_timer_speed(1000 - speed * 1000)

    def move(self):
        empty_houses = set()
        to_move = set()
        nonempty = set()

        self.disable_updates()

    #    for i in range(self.size):
    #        for j in range(self.size):
    #            if self.get_cell_attribute(i, j, 'color') == HouseState.EMPTY:
    #                empty_houses.add((i, j))
    #            else:  # check satisfaction of cell (i,j)
    #                similarity_count = 0
    #                different_count = 0
    #                for neig_i, neig_j in self.iterate_cell_neighbors(i, j):  # compute satisfaction
    #                    if self.get_cell_attribute(neig_i, neig_j, 'color') == self.get_cell_attribute(i, j, 'color'):
    #                        similarity_count += 1
    #                    elif self.get_cell_attribute(neig_i, neig_j, 'color') != HouseState.EMPTY:
    #                        different_count += 1
    #                if similarity_count + different_count > 0:
    #                    satisfaction = similarity_count/(similarity_count + different_count)
    #                    if satisfaction < self.simil:
    #                        to_move.add((i, j))

        for i in range(self.size):
            for j in range(self.size):
                if self.get_cell_attribute(i, j, 'color') == HouseState.EMPTY:
                    empty_houses.add((i, j))
                else:
                    nonempty.add((i,j))

        self.frustrated_count = 0
        for n in range(int(self.size * self.size * self.prob)):
            i, j = random.sample(nonempty, 1)[0]
            similarity_count = 0
            different_count = 0
            for neig_i, neig_j in self.iterate_cell_neighbors(i, j):  # compute satisfaction
                if self.get_cell_attribute(neig_i, neig_j, 'color') == self.get_cell_attribute(i, j, 'color'):
                    similarity_count += 1
                elif self.get_cell_attribute(neig_i, neig_j, 'color') != HouseState.EMPTY:
                    different_count += 1
                    self.frustrated_count += 0.5
            if similarity_count + different_count > 0:
                satisfaction = similarity_count/(similarity_count + different_count)
                if satisfaction < self.simil:
                    race = self.get_cell_attribute(i, j, 'color')
                    self.notify_cell_state(i, j, color=HouseState.EMPTY)  # move out
                    h, l = random.sample(empty_houses, 1)[0]  # new house in (h,l)
                    self.notify_cell_state(h, l, color=race)
                    empty_houses.remove((h,l)) # new house removed from market
                    empty_houses.add((i,j))  # old house now on the market
                    nonempty.remove((i,j))
                    nonempty.add((h,l))
     #   for i, j in to_move:
     #       race = self.get_cell_attribute(i, j, 'color')
     #       self.notify_cell_state(i, j, color=HouseState.EMPTY)  # move out
     #       h, l = random.sample(empty_houses, 1)[0]  # new house in (h,l)
     #       self.notify_cell_state(h, l, color=race)
     #       empty_houses.remove((h,l)) # new house removed from market
     #       empty_houses.add((i,j))  # old house now on the market


        self.enable_updates()
        self.update_charts()

    def reset(self):
        self.clear()
        self.shelling(self.size, self.prob, self.simil, self.imb)

    def reset_charts(self):
        self.frustrated_count = 0
        self.frustration_chart.clear_datapoints()
        self.chart_steps = 0

    def update_charts(self):
        self.chart_steps += 1
        if self.chart_steps >= self.update_chart_steps:
            self.frustration_chart.add_datapoint(y=self.frustrated_count)
            self.chart_steps = 0

    def tick(self):
        print('calling tick')
        self.move()
