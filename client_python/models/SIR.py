import graph_model
import random
import itertools
import math

class SIRModel(graph_model.GraphModel):

    update_chart_steps = 1

    def __init__(self):
        super().__init__()
        self.set_timer_speed(500)
        
        self.infect_count_chart = None
        self.recovered_count_chart = None
        self.active_links_chart = None
        self.chart_steps = 0

    def handle_property_change(self, prop, value):
        if (prop == "size"):
            self.clear()
            self.SIRmod(value, density=self.density, startfrac=self.startfrac, infrate=self.infrate, recrate=self.recrate, gtype=self.gtype)
        elif prop == "density":
            self.clear()
            self.SIRmod(self.size, density=value, startfrac=self.startfrac, infrate=self.infrate, recrate=self.recrate, gtype=self.gtype)
        elif prop == "startfrac":
            self.clear()
            self.SIRmod(self.size, self.density, startfrac=value, infrate=self.infrate, recrate=self.recrate, gtype=self.gtype)
        elif prop == "infrate":
            self.clear()
            self.SIRmod(self.size, self.density, self.startfrac, infrate=value, recrate=self.recrate, gtype=self.gtype)
        elif prop == "recrate":
            self.clear()
            self.SIRmod(self.size, self.density, self.startfrac, self.infrate, recrate=value, gtype=self.gtype)
        elif prop == "gtype":
            self.clear()
            self.SIRmod(self.size, self.density, self.startfrac, self.infrate, self.recrate, gtype = value)
        elif prop == "speed":
            self.set_speed(value)
        elif prop == "steptype":
            self.steptype = value

    def SIRmod(self, n, density, startfrac, infrate, recrate, gtype):
        # disable updates to avoid sending a message each time a node is added during generation

        self.time = 0
        self.disable_updates()
        self.infected_set = set()
        self.susceptible_set = set()
        self.recovered_set = set()
        if gtype == 'Erdos-Renyi':
            pairs = itertools.combinations(range(1,n+1), 2)
            newNode = 1; m = 1
            self.add_node(1, color='red', weight=0, state='infected') # starting node
            self.infected_set.add(1)
            for i in range(1, n):
                newNode += 1
                if random.random() <= startfrac:
                    self.add_node(newNode, weight=m, state='infected', color='red')
                    self.infected_set.add(newNode)
                else:
                    self.add_node(newNode, weight=m, state='susceptible', color='green')
                    self.susceptible_set.add(newNode)
            for j,k in random.sample(list(pairs), math.floor(density*n*(n-1)/2)):
                self.add_edge(j, k)
                self.update_node_props(j,
                        weight=self.get_node_prop(j, 'weight')+1)
                self.update_node_props(k,
                        weight=self.get_node_prop(k, 'weight')+1)
        
        elif gtype == 'Barabasi-Albert':
            newNode = 1; m = 1
            self.nodesWeighted = [1]
            def chooseTarget():
                return self.nodesWeighted[random.randint(0, len(self.nodesWeighted)-1)]
            # generate nodes
            self.add_node(1, color='red', weight=0, state='infected') # starting node
            self.infected_set.add(1)
            for i in range(1, n):
                newNode += 1
                if random.random() <= startfrac:
                    self.add_node(newNode, weight=m, state='infected', color='red')
                    self.infected_set.add(newNode)
                else:
                    self.add_node(newNode, weight=m, state='susceptible', color='green')
                    self.susceptible_set.add(newNode)
                for k in range(m):
                    tgt = chooseTarget()
                    self.add_edge(newNode, tgt)
                    self.nodesWeighted.append(newNode)
                    self.nodesWeighted.append(tgt)
                    self.update_node_props(tgt,
                            weight=self.get_node_prop(tgt, 'weight')+1)

        self.actlinks_set = set()
        for n in self.susceptible_set:
             for neig in self.get_node_neighbors(n):
                if neig in self.infected_set:
                    self.actlinks_set.add((n,neig))
        self.actlinks_count = len(self.actlinks_set)
        self.infect_count = len(self.infected_set)
        self.recovered_count = 0
        self.enable_updates()
        
        # save size
        self.size = n
        self.density = density
        self.startfrac = startfrac
        self.recrate = recrate
        self.infrate = infrate
        self.gtype = gtype
        self.reset_charts()


    def create(self):
        size = 50
        speed = 0.3
        density = 0.1
        infrate = 0.2
        recrate = 1
        startfrac = 0.1
        gtype = 'Erdos-Renyi'
        steptype = 'Sync'

        self.add_property('size', 'Network Size', size, [1, 300], 1)
        self.add_property('density', 'Network Density', density, [0, 1], 'any')
        self.add_property('infrate', 'Infection Rate', infrate, [0, 1], 'any')
        self.add_property('recrate', 'Recovery Rate', recrate, [0, 1], 'any')
        self.add_property('startfrac', 'Initial infected fraction', startfrac, [0, 1], 'any')
        self.add_property('speed', 'Simulation Speed', speed, [0, 1], 'any')
        self.add_property_selectbox('gtype', 'Network Type', 'Erdos-Renyi', ['Erdos-Renyi', 'Barabasi-Albert'])
        self.add_property_selectbox('steptype', 'Dynamics Rule', 'Sync', ['Sync', 'Gillespie'])

        self.infect_count_chart = self.add_chart('line',
                title='Infected nodes count',
                xLabel='t',
                size=8)
        self.recovered_count_chart = self.add_chart('line',
                title='Recovered nodes count',
                xLabel='t',
                size=8)
        self.active_links_chart = self.add_chart('line',
                title='Active links count',
                xLabel='t',
                size=8)

        self.SIRmod(size, density, startfrac, infrate, recrate, gtype)
        
        self.set_speed(speed)
        self.steptype = steptype

    def reset(self):
        self.clear()
        self.SIRmod(self.size, self.density, self.startfrac, self.infrate, self.recrate, self.gtype)

    def set_speed(self, speed):
        self.speed = speed
        self.set_timer_speed(1000 - speed * 1000)

    def sync_step(self):
        self.disable_updates()

        infect_set = set()
        for i,j in self.actlinks_set:
            if i in infect_set:
                continue
            if random.random() < self.infrate/(self.infrate + self.recrate):
                infect_set.add(i)

        recover_set = set()
        for n in self.infected_set:
            agg_infrate = 0
            for neig in self.get_node_neighbors(n):
                if neig in self.infected_set:
                    agg_infrate += self.infrate
            if random.random() < self.recrate/(self.recrate + agg_infrate):
                recover_set.add(n)

        for n in infect_set:
            self.update_node_props(n, color='red')
            self.update_node_props(n, state='infected')
            self.infected_set.add(n)
            self.susceptible_set.remove(n)
        for n in recover_set:
            self.update_node_props(n, color='black')
            self.update_node_props(n, state='recovered')
            self.recovered_set.add(n)
            self.infected_set.remove(n)

        self.actlinks_set = set()
        for n in self.susceptible_set:
             for neig in self.get_node_neighbors(n):
                if neig in self.infected_set:
                    self.actlinks_set.add((n,neig))
        
        self.actlinks_count = len(self.actlinks_set)
        self.infect_count = len(self.infected_set)
        self.recovered_count = len(self.recovered_set)
        
        self.time += 1
        self.enable_updates()
        self.update_charts()

    def gillespie_step(self):

        self.disable_updates()
        self.actlinks_count = len(self.actlinks_set)
 
        self.infect_count = len(self.infected_set)
        if self.infect_count == 0 or self.actlinks_count == 0:
            self.time += 1/self.recrate
            self.enable_updates()
            self.update_charts()
            return

        self.all_rate_inf = self.infrate * self.actlinks_count
        self.all_rate_rec = self.recrate * self.infect_count
        self.all_rate = self.all_rate_inf + self.all_rate_rec

        if random.random() < self.all_rate_inf/self.all_rate:
            prop_link = random.sample(self.actlinks_set, 1)
            n = prop_link[0][0]
            self.update_node_props(n, color='red')
            self.update_node_props(n, state='infected')
            self.infected_set.add(n)
            self.susceptible_set.remove(n)
            for neig in self.get_node_neighbors(n):
                if neig in self.susceptible_set:
                    self.actlinks_set.add((neig, n))
                elif neig in self.infected_set:
                    self.actlinks_set.remove((n, neig))

        else:
            n = random.sample(self.infected_set, 1)[0]
            self.update_node_props(n, color='black')
            self.update_node_props(n, state='recovered')
            self.recovered_set.add(n)
            self.infected_set.remove(n)
            for neig in self.get_node_neighbors(n):
                if neig in self.susceptible_set:
                    self.actlinks_set.remove((neig,n))

        
        self.actlinks_count = len(self.actlinks_set)
 
        self.infect_count = len(self.infected_set)
        self.recovered_count = len(self.recovered_set)
        
        next_time = - math.log(random.random()) / self.all_rate
        self.time += next_time
        self.enable_updates()
        self.update_charts()
        

    def reset_charts(self):
        self.infect_count = 0
        self.actlinks_count = 0

        self.infect_count_chart.clear_datapoints()
        self.recovered_count_chart.clear_datapoints()
        self.active_links_chart.clear_datapoints()
        self.chart_steps = 0

    def update_charts(self):
         self.chart_steps += 1
         if self.chart_steps >= self.update_chart_steps:
             self.infect_count_chart.add_datapoint(x=self.time, y=self.infect_count)
             self.recovered_count_chart.add_datapoint(x=self.time, y=self.recovered_count)
             self.active_links_chart.add_datapoint(x=self.time, y=self.actlinks_count)
             self.chart_steps = 0

    def stop_condition(self):
        return self.actlinks_count == 0 and self.time > 0


    def tick(self):
        print('calling tick')
        if self.steptype == 'Sync':
            self.sync_step()
        elif self.steptype == 'Gillespie':
            self.gillespie_step()
        else:
            raise ValueError('invalid dynamics type')
	
		
