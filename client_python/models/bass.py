""" 
BASS MODEL
----------
innovation diffusion, an agent becomes aware with prob p_i:

p_i(t) = p Dt + q Dt ( n_i(t)/m_i ) - (p q Dt^2 (n_i(t)/m_i) )
where:
    * m_i: i neighbours number
    * n_i(t): i awake neighbours number
    * p: advertising effect
    * q: word of mouth effect
    
specs:
    * initial configuration: random woke agents with density d
    * stopping condition: stops after max_steps or all agents awake

TODO:
"""

import grid_model
import random


class BassModel(grid_model.GridModel):
    update_chart_steps = 1
    

    def __init__(self):
        super().__init__()
        self.size = 0
        self.set_timer_speed(500)
        self.initial_config = []
        
        self.woke_count_chart = None
        self.chart_steps = 0
        # model color map
        self.cmap = ['#ffffff','#ff0000']  # hex format
        

    def handle_property_change(self, prop, value):
        if (prop == 'size'):
            #self.clear()
            self.bass(size=value, d=self.d, p=self.p, q=self.q, max_steps=self.max_steps)
        elif prop == 'density':
            self.bass(size=self.size, d=value, p=self.p, q=self.q, max_steps=self.max_steps)
        elif prop == 'p':
            self.bass(size=self.size, d=self.d, p=value, q=self.q, max_steps=self.max_steps)
        elif prop == 'q':
            self.bass(size=self.size, d=self.d, p=self.p, q=value, max_steps=self.max_steps)
        elif prop == 'max_steps':
            self.bass(size=self.size, d=self.d, p=self.p, q=self.q, max_steps=value)
        elif prop == 'speed':
            self.set_speed(value)
            
    def handle_agent_clicked(self, data):
        i = data['row']; j = data['col']
        self.set_agent_state(i, j, 1)


    def bass(self, size, d, p, q, max_steps=100, rebuild=True):
        def initial_fun(row, col):
            if random.random() < self.d:
                woke = 1
            else:
                woke = 0
            color = self.cmap[woke]
            return {'woke': woke, 'color': color}
            
        self.reset_charts() 
        
        if size <= 0:
            raise ValueError('invalid size')
        self.size = size
        
        self.step = 0
        self.max_steps = max_steps
        
        self.p = p
        self.q = q  
        self.d = d      
            
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
                    curr_woke = self.get_cell_attribute(i, j, 'woke')
                    self.woke_count += curr_woke
                    curr_cell = (curr_color, curr_woke)
                    self.initial_config.append(curr_cell)
            # print(self.initial_config)
        else:        
            self.disable_updates()
            k = 0
            for i in range(size):
                for j in range(size):
                    curr_color = self.initial_config[k][0]
                    curr_woke = self.initial_config[k][1]
                    self.woke_count += curr_woke
                    self.notify_cell_state(i, j, color = curr_color)
                    self.notify_cell_state(i, j, woke = curr_woke)
                    k += 1

            self.enable_updates()


    def reset(self):
        self.bass(self.size, d=self.d, p=self.p, q=self.q, max_steps=self.max_steps, rebuild=False)

      
    def create(self):
        size = 5
        speed = 0.1
        d = 0.1
        p = 0.1
        q = 0.1
        max_steps = 100
        
        self.initial_config = []

        self.add_property('size', 'Grid Size', size, [1, 100], 1)
        self.add_property('density', 'Initial density', d, [0,1], 'any')
        self.add_property('p', 'Advertising effect', p, [0,1], 'any')
        self.add_property('q', 'Word of mouth effect', q, [0,1], 'any')
        self.add_property('steps', 'Max number of steps', max_steps, [100, 1000], 50)
        self.add_property('speed', 'Speed', speed, [0, 1], 'any')
        
        self.woke_count_chart = self.add_chart('ts',
                title='Aware agent count',
                xLabel='t')
                
        self.bass(size, d=d, p=p, q=q, max_steps=max_steps)
        self.set_speed(speed)
        
    def set_agent_state(self, row, col, state):
        self.notify_cell_state(row, col, woke=state)
        self.notify_cell_state(row, col, color=self.cmap[state])
        
        
    def set_speed(self, speed):
        self.speed = speed
        self.set_timer_speed(1000 - speed * 1000)
        

    def awake(self):
        
        self.disable_updates()
      
        # compute the awakening
        for i in range(0, self.size):
            for j in range(0, self.size):
                # if the agent is not awake yet
                if not self.get_cell_attribute(i, j, 'woke'):
                    n_woke = 0
                    n = 0
                    for neig_i, neig_j in self.iterate_cell_neighbors(i, j): 
                        n_woke += self.get_cell_attribute(neig_i, neig_j, 'woke')
                        n += 1
                    p_ij = self.p + self.q*n_woke/n - self.p*self.q*n_woke/n
                    self.notify_cell_state(i, j, tooltip=p_ij)
                    if p_ij > random.random():
                        self.set_agent_state(i, j, 1)
                        self.woke_count += 1
                  
        self.enable_updates()
        self.update_charts()
                        
        return 0  
        

    def reset_charts(self):
        self.woke_count = 0

        self.woke_count_chart.clear_datapoints()
        self.chart_steps = 0


    def update_charts(self):
        self.chart_steps += 1
        if self.chart_steps >= self.update_chart_steps:
            self.woke_count_chart.add_datapoint( self.woke_count )
            self.chart_steps = 0
            print(self.woke_count)

        
    
    def stop_condition(self):
        return self.step > self.max_steps or self.woke_count >= self.size*self.size

            
    def tick(self):
        print('calling tick')
        self.step += 1
        self.awake()

        
