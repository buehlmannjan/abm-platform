""" 
in this model 
    * the initial configuration is uniformly random
    * one grain is added at random at each time-step
    * when topples, a reursive avalanche is triggered (can topple back)
    * 
TODO:
    * mettere condizioni al contorno per permettere di perdere massa?
    * a volte si raggiunge il limite di ricorsione
"""

import grid_model
import random
# for the colormap
from matplotlib import cm  
from matplotlib.colors import rgb2hex


class SandpileModel(grid_model.GridModel):
    update_chart_steps = 1
    

    def __init__(self):
        super().__init__()
        self.size = 0
        self.tres = 8
        self.set_timer_speed(500)
        self.avalanches_count_chart = None
        self.chart_steps = 0
        self.avalanches_orig_count = 0
        self.initial_config = []
        self.stop_level = 1
        self.f_cmap = cm.get_cmap(name = 'hot').reversed()
        self.cmap_h = []
        

    def handle_property_change(self, prop, value):
        if (prop == 'size'):
            #self.clear()
            self.sandpile(size=value, tres=self.tres, stop_level=self.stop_level)
        elif prop == 'treshold':
            self.sandpile(self.size, tres=value, stop_level=self.stop_level)
        elif prop == 'stop':
            self.sandpile(self.size, tres=self.tres, stop_level=value)
        elif prop == 'speed':
            self.set_speed(value)
            
    def handle_agent_clicked(self, data):
        row = data['row']; col = data['col']
        self.drop([row, col])


    def sandpile(self, size, tres=None, stop_level=None, rebuild=True):
        def initial_fun(row, col):
            height = random.randint(0, self.tres)
            color = self.cmap_h[height]
            return {'height': height, 'color': color, 'tooltip': height}
            
        if size <= 0:
            raise ValueError('invalid size')

        self.size = size
        if tres is not None:
            self.tres = tres
        if stop_level is not None:
            self.stop_level = stop_level
        # new color map
        n = self.tres + 8
        points = [x/n for x in range(n)]
        self.cmap_h = [rgb2hex(x) for x in self.f_cmap(points)]  # hex format
            
        if rebuild:
            self.create_grid(
                    size,
                    size,
                    initial_state= initial_fun 
                    )
            # self.initial_config = []
            for i in range(size):
                for j in range(size):
                    curr_color = self.get_cell_attribute(i, j, 'color')
                    curr_height = self.get_cell_attribute(i, j, 'height')
                    curr_cell = (curr_color, curr_height)
                    self.initial_config.append(curr_cell)
            # print(self.initial_config)
        else:
            self.disable_updates()
            k = 0
            for i in range(size):
                for j in range(size):
                    curr_color = self.initial_config[k][0]
                    curr_height = self.initial_config[k][1]
                    self.notify_cell_state(i, j, color = curr_color)
                    self.notify_cell_state(i, j, height = curr_height)
                    self.notify_cell_state(i, j, tooltip = curr_height)
                    k += 1

            self.enable_updates()

        self.reset_charts() 


    def reset(self):
        self.sandpile(self.size, tres=self.tres, stop_level=self.stop_level, rebuild=False)

      
    def create(self):
        size = 5
        speed = 0.1
        tres = 8
        stop_level = 3
        
        self.initial_config = []

        self.add_property('size', 'Grid Size', size, [1, 100], 1)
        self.add_property('treshold', 'Avalanche Threshold', tres, [8, 10], 1)
        self.add_property('stop', 'Stopping Floor', stop_level, [1, 7], 1)
        self.add_property('speed', 'Speed', speed, [0, 1], 'any')
        
        self.avalanches_count_chart = self.add_chart('ts',
                title='Avalanches count',
                xLabel='t')
                
        self.sandpile(size, tres=tres, stop_level=stop_level)
        self.set_speed(speed)
        

    def set_speed(self, speed):
        self.speed = speed
        self.set_timer_speed(1000 - speed * 1000)
        

    def drop(self, arg = None):

        self.disable_updates()
        
        if arg is not None:
            i,j = arg
        else:
            i = random.randint(0, self.size-1)
            j = random.randint(0, self.size-1)
        
        h = self.get_cell_attribute(i, j, 'height')
        self.notify_cell_state(i, j, height = h+1)  # drop the sand grain
        self.notify_cell_state(i, j, color = self.cmap_h[h+1])
        self.notify_cell_state(i, j, tooltip = h+1)
        self.enable_updates()
        
        if h+1 >= self.tres:
            self.avalanches_count += 1
            self.topple((i,j))
        
        self.update_charts()
        
    
    def topple(self, tup):
        
        (i,j) = tup
        self.disable_updates()
        
        loss = 0  # max loss = 8
        
        for neig_i, neig_j in self.iterate_cell_neighbors(i, j): 
            if (neig_i != i or neig_j != j):
                loss += 1
                h_neig = self.get_cell_attribute(neig_i, neig_j, 'height')
                self.notify_cell_state(neig_i, neig_j, height = h_neig+1) 
                self.notify_cell_state(neig_i, neig_j, color = self.cmap_h[h_neig+1])
                self.notify_cell_state(neig_i, neig_j, tooltip = h_neig+1)
        
        h = self.get_cell_attribute(i, j, 'height')
        self.notify_cell_state(i, j, height = h - loss) 
        self.notify_cell_state(i, j, color = self.cmap_h[h-loss])
        self.notify_cell_state(i, j, tooltip = h-loss)
        self.enable_updates()
        for neig_i, neig_j in self.iterate_cell_neighbors(i, j):  
            h_neig = self.get_cell_attribute(neig_i, neig_j, 'height')          
            if h_neig >= self.tres:
                self.topple((neig_i, neig_j))
        return 0  
        

    def reset_charts(self):
        self.avalanches_count = self.avalanches_orig_count

        self.avalanches_count_chart.clear_datapoints()
        self.chart_steps = 0


    def update_charts(self):
        self.chart_steps += 1
        if self.chart_steps >= self.update_chart_steps:
            self.avalanches_count_chart.add_datapoint( self.avalanches_count )
            self.chart_steps = 0

        
    
    def stop_condition(self):
        x = self.stop_level
        for i in range(self.size):
            for j in range(self.size):
                h = self.get_cell_attribute(i, j, 'height')
                if h >= x:
                    check = True
                else:
                    return False
        return check

            
    def tick(self):
        print('calling tick')
        self.drop()

        
