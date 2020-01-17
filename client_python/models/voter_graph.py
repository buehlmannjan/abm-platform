import graph_model
import random
import itertools
import math
import numpy

class VoterModel(graph_model.GraphModel):

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
            self.voter(value, density=self.density, startfrac=self.startfrac, gtype=self.gtype)
        elif prop == "density":
            self.clear()
            self.voter(self.size, density=value, startfrac=self.startfrac, gtype=self.gtype)
        elif prop == "startfrac":
            self.clear()
            self.voter(self.size, self.density, startfrac=value, gtype=self.gtype)
        elif prop == "gtype":
            self.clear()
            self.voter(self.size, self.density, self.startfrac, gtype = value)
        elif prop == "speed":
            self.set_speed(value)
        elif prop == "steptype":
            self.steptype = value

    def voter(self, n, density, startfrac, gtype):
        # disable updates to avoid sending a message each time a node is added during generation

        self.time = 0
        self.disable_updates()
        self.red_set = set()
        self.blue_set = set()
        if gtype == 'Erdos-Renyi':
            pairs = itertools.combinations(range(1,n+1), 2)
            newNode = 1; m = 1
            self.add_node(1, color='red', weight=0) # starting node
            self.red_set.add(1)
            for i in range(1, n):
                newNode += 1
                if random.random() <= startfrac:
                    self.add_node(newNode, weight=m, color='red')
                    self.red_set.add(newNode)
                else:
                    self.add_node(newNode, weight=m, color='blue')
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
            self.add_node(1, color='red', weight=0) # starting node
            self.red_set.add(1)
            for i in range(1, n):
                newNode += 1
                if random.random() <= startfrac:
                    self.add_node(newNode, weight=m, color='red')
                    self.red_set.add(newNode)
                else:
                    self.add_node(newNode, weight=m, color='blue')
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
        self.startfrac = startfrac
        self.gtype = gtype
        self.reset_charts()


    def create(self):
        size = 50
        speed = 0.3
        density = 0.1
        startfrac = 0.5
        gtype = 'Erdos-Renyi'
        steptype = 'Node'

        self.add_property('size', 'Network Size', size, [1, 300], 1)
        self.add_property('density', 'Network Density', density, [0, 1], 'any')
        self.add_property('startfrac', 'Initial red fraction', startfrac, [0, 1], 'any')
        self.add_property('speed', 'Simulation Speed', speed, [0, 0.99], 'any')
        self.add_property_selectbox('gtype', 'Network Type', 'Erdos-Renyi', ['Erdos-Renyi', 'Barabasi-Albert'])
        self.add_property_selectbox('steptype', 'Dynamics Rule', 'Node', ['Node', 'Link'])

        self.magnetiz_chart = self.add_chart('line', 
                title='Red fraction',
                xLabel='t',
                yLim = [0,1],
                size=8)
        self.active_links_chart = self.add_chart('line',
                title='Active links count',
                yLim = [0,1],
                xLabel='t',
                size=8)

        self.voter(size, density, startfrac, gtype)
        
        self.set_speed(speed)
        self.steptype = steptype

    def reset(self):
        self.clear()
        self.voter(self.size, self.density, self.startfrac, self.gtype)

    def set_speed(self, speed):
        self.speed = speed
        self.set_timer_speed(1000 - speed * 1000)

    def node_step(self):
        self.disable_updates()

        node = random.randrange(1, self.size+1)
        #print(node)
        all_neighs = self.get_node_neighbors(node)
        #print(all_neighs)
        neigh = random.sample(all_neighs, 1)[0]
        if neigh in self.red_set:
            self.update_node_props(node, color = 'red')
            if node in self.blue_set:
                self.blue_set.remove(node)
                self.red_set.add(node)
        else:
            self.update_node_props(node, color = 'blue')
            if node in self.red_set:
                self.blue_set.add(node)
                self.red_set.remove(node)

        self.actlinks_set = set()
        for node in self.red_set:
             for neig in self.get_node_neighbors(node):
                if neig in self.blue_set:
                    self.actlinks_set.add((node,neig))
        
        self.actlinks_count = len(self.actlinks_set)
        self.magnetiz_count = len(self.red_set)
        self.time += 1/self.size
        self.enable_updates()
        self.update_charts()

    def link_step(self):

        self.disable_updates()
        
        l = random.sample(self.actlinks_set, 1)[0]
        if (l[0] in self.red_set and l[1] in self.red_set) or (l[0] in self.blue_set and l[1] in self.blue_set):
            return
        else:
            randstate = random.sample([0,1],1)[0]
            if randstate == 1:
                self.update_node_props(l[0], color = 'red')
                self.update_node_props(l[1], color = 'red')
                if(l[0] in self.red_set):
                    self.blue_set.remove(l[1])
                else:
                    self.blue_set.remove(l[0])
                self.red_set.add(l[0])
                self.red_set.add(l[1])
            else:
                self.update_node_props(l[0], color = 'blue')
                self.update_node_props(l[1], color = 'blue')
                if(l[0] in self.red_set):
                    self.red_set.remove(l[0])
                else:
                    self.red_set.remove(l[1])
                self.blue_set.add(l[0])
                self.blue_set.add(l[1])

        self.actlinks_set = set()
        for n in self.red_set:
             for neig in self.get_node_neighbors(n):
                if neig in self.blue_set:
                    self.actlinks_set.add((n,neig))
        
        self.actlinks_count = len(self.actlinks_set)
        self.magnetiz_count = len(self.red_set)
        if self.actlinks_count > 0:
            self.time += 1/self.size * numpy.random.geometric(self.actlinks_count/self.nlinks)
        self.enable_updates()
        self.update_charts()
        

    def reset_charts(self):
        self.magnetiz_count = 0
        self.actlinks_count = 0

        self.magnetiz_chart.clear_datapoints()
        self.active_links_chart.clear_datapoints()
        self.chart_steps = 0

    def update_charts(self):
         self.chart_steps += 1
         if self.chart_steps >= self.update_chart_steps:
             self.magnetiz_chart.add_datapoint(x=self.time, y=self.magnetiz_count/self.size)
             self.active_links_chart.add_datapoint(x=self.time, y=self.actlinks_count/self.nlinks)
             self.chart_steps = 0

    def stop_condition(self):
        return self.actlinks_count == 0 and self.time > 0

    def tick(self):
        print('calling tick')
        if self.steptype == 'Node':
            self.node_step()
        elif self.steptype == 'Link':
            self.link_step()
        else:
            raise ValueError('invalid dynamics type')
	
		
