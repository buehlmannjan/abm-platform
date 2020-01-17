import graph_model
import random
import itertools
import math
import numpy

class IsingModel(graph_model.GraphModel):

    update_steps = 1
    update_chart_steps = 1

    def __init__(self):
        super().__init__()
        self.set_timer_speed(500)
        
        self.magnetiz_chart = None
        self.active_links_chart = None
        self.chart_steps = 0

    def handle_property_change(self, prop, value):
        if (prop == "size"):
            self.clear()
            self.ising(value, density=self.density, extfield=self.extfield, gtype=self.gtype, temperature=self.temperature)
        elif prop == "density":
            self.clear()
            self.ising(self.size, density=value, extfield=self.extfield, gtype=self.gtype, temperature=self.temperature)
        elif prop == "extfield":
            self.clear()
            self.ising(self.size, self.density, extfield=value, gtype=self.gtype, temperature=self.temperature)
        elif prop == "gtype":
            self.clear()
            self.ising(self.size, self.density, self.extfield, gtype = value, temperature=self.temperature)
        elif prop == "speed":
            self.set_speed(value)
        elif prop == "temperature":
            self.clear()
            self.ising(self.size, self.density, self.extfield, self.gtype, temperature=value)
        elif prop == 'update_steps':
            self.update_steps = value

    def ising(self, n, density, extfield, gtype, temperature):
        # disable updates to avoid sending a message each time a node is added during generation

        self.time = 0
        self.disable_updates()
        self.red_set = set()
        self.blue_set = set()
        if gtype == 'Erdos-Renyi':
            pairs = itertools.combinations(range(1,n+1), 2)
            newNode = 1; m = 1
            self.add_node(1, color='red', weight=0, state=1) # starting node
            self.red_set.add(1)
            for i in range(1, n):
                newNode += 1
                if random.random() < 0.5:
                    self.add_node(newNode, weight=m, color='red', state=1)
                    self.red_set.add(newNode)
                else:
                    self.add_node(newNode, weight=m, color='blue', state=-1)
                    self.blue_set.add(newNode)
            for j,k in random.sample(list(pairs), math.floor(density*n*(n-1)/2)):
                self.add_edge(j, k)
                self.update_node_props(j,
                        weight=self.get_node_prop(j, 'weight')+1)
                self.update_node_props(k,
                        weight=self.get_node_prop(k, 'weight')+1)
            self.nlinks = math.floor(density*n*(n-1)/2)
        
        elif gtype == 'Barabasi-Albert':
            newNode = 1; m = 1
            self.nodesWeighted = [1]
            def chooseTarget():
                return self.nodesWeighted[random.randint(0, len(self.nodesWeighted)-1)]
            # generate nodes
            self.add_node(1, color='red', weight=0, state=1) # starting node
            self.red_set.add(1)
            for i in range(1, n):
                newNode += 1
                if random.random() < 0.5:
                    self.add_node(newNode, weight=m, color='red', state=1)
                    self.red_set.add(newNode)
                else:
                    self.add_node(newNode, weight=m, color='blue', state=-1)
                    self.blue_set.add(newNode)
                for k in range(m):
                    tgt = chooseTarget()
                    self.add_edge(newNode, tgt)
                    self.nodesWeighted.append(newNode)
                    self.nodesWeighted.append(tgt)
                    self.update_node_props(tgt,
                            weight=self.get_node_prop(tgt, 'weight')+1)
            self.nlinks = n

        self.actlinks_set = set()
        for node in self.red_set:
             for neig in self.get_node_neighbors(node):
                if neig in self.blue_set:
                    self.actlinks_set.add((node,neig))
        
        self.enable_updates()
        
        # save size
        self.size = n
        self.density = density
        self.extfield = extfield
        self.gtype = gtype
        self.temperature = temperature
        self.reset_charts()


    def create(self):
        size = 50
        speed = 0.3
        density = 0.1
        extfield = 0
        temperature = 1
        gtype = 'Erdos-Renyi'
        update_steps = 1

        self.add_property('size', 'Network Size', size, [1, 300], 1)
        self.add_property('density', 'Network Density (E-R)', density, [0, 1], 'any')
        self.add_property('extfield', 'External field', extfield, [-1, 1], 'any')
        self.add_property('temperature', 'Temperature', temperature, [0.01, 3], 'any')
        self.add_property('speed', 'Simulation Speed', speed, [0, 0.99], 'any')
        self.add_property('update_steps', '# steps per update', update_steps, [1, 300], 10)
        self.add_property_selectbox('gtype', 'Network Type', 'Erdos-Renyi', ['Erdos-Renyi', 'Barabasi-Albert'])

        self.magnetiz_chart = self.add_chart('line', 
                title='Magnetization',
                xLabel='t',
                yLim = [-1,1],
                size=8)
        self.active_links_chart = self.add_chart('line',
                title='Active links count',
                yLim = [0,1],
                xLabel='t',
                size=8)

        self.ising(size, density, extfield, gtype, temperature)
        
        self.set_speed(speed)
        self.update_steps = update_steps

    def reset(self):
        self.clear()
        self.ising(self.size, self.density, self.extfield, self.gtype, self.temperature)

    def set_speed(self, speed):
        self.speed = speed
        self.set_timer_speed(1000 - speed * 1000)

    def step(self):

        self.disable_updates()
        
        node = random.randrange(1, self.size+1)
        currstate = self.get_node_prop(node, 'state')
        interact = 0
        neigh = self.get_node_neighbors(node)

        for n2 in neigh:
            interact += self.get_node_prop(n2, 'state')

        moveprob = math.exp(- (2/self.temperature) * currstate * (self.extfield + interact))
        if random.random() < moveprob:
            self.update_node_props(node, state= - currstate)
            if currstate == 1:
                self.update_node_props(node, color='blue')
                self.red_set.remove(node)
                self.blue_set.add(node)
            else:
                self.update_node_props(node, color='red')
                self.red_set.add(node)
                self.blue_set.remove(node)

        self.time += 1

        self.actlinks_set = set()
        for n in self.red_set:
             for neig in self.get_node_neighbors(n):
                if neig in self.blue_set:
                    self.actlinks_set.add((n,neig))
        
        self.actlinks_count = len(self.actlinks_set)
        self.magnetiz_count = len(self.red_set)

        if self.time % self.update_steps == 0:
            self.enable_updates()
            self.update_charts()
            self.disable_updates()
        

    def reset_charts(self):
        self.magnetiz_count = 0
        self.actlinks_count = 0

        self.magnetiz_chart.clear_datapoints()
        self.active_links_chart.clear_datapoints()
        self.chart_steps = 0

    def update_charts(self):
         self.chart_steps += 1
         if self.chart_steps >= self.update_chart_steps:
             self.magnetiz_chart.add_datapoint(x=self.time, y=2*self.magnetiz_count/self.size - 1)
             self.active_links_chart.add_datapoint(x=self.time, y=self.actlinks_count/self.nlinks)
             self.chart_steps = 0


    def tick(self):
        print('calling tick')
        self.step()
	
		
