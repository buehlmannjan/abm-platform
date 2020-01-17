import graph_model
import random

class BarabasiModel(graph_model.GraphModel):
    __fullname__ = 'Diffusion in Barabási-Albert'

    def __init__(self):
        super().__init__()
        self.set_timer_speed(500)

    def handle_property_change(self, prop, value):
        if (prop == 'size'):
            self.clear()
            self.barabasi(value)
        elif prop == 'speed':
            self.set_diffusion_speed(value)

    def barabasi(self, n):
        # disable updates to avoid sending a message each time a node is added during generation
        self.disable_updates()

        # init start node id and model parameter
        newNode = 1; m = 1
        self.nodesWeighted = [1]
        def chooseTarget():
            return self.nodesWeighted[random.randint(0, len(self.nodesWeighted)-1)]
        # generate nodes
        self.add_node(1, color='blue', weight=0) # starting node
        for i in range(1, n):
            newNode += 1
            self.add_node(newNode, weight=m)
            for k in range(m):
                tgt = chooseTarget()
                self.add_edge(newNode, tgt)
                self.nodesWeighted.append(newNode)
                self.nodesWeighted.append(tgt)
                self.update_node_props(tgt,
                        weight=self.get_node_prop(tgt, 'weight')+1)

        self.enable_updates()

        # save size
        self.size = n

    def create(self):
        size = 50
        speed = 0.1

        self.add_property('size', 'Network Size', size, [1, 100], 1)
        self.add_property('speed', 'Diffusion Speed', speed, [0, 1], 'any')

        self.barabasi(size)
        self.set_diffusion_speed(speed)

    def reset(self):
        self.barabasi(self.size)

    def set_diffusion_speed(self, speed):
        self.set_timer_speed(1000 - speed * 1000)

    def diffuse(self):
        self.disable_updates()

        #print('node_iterator -> {}'.format([(x, self.get_node_prop(x, 'color')) for x in self.node_iterator()]))
        change_set = set()
        for n in (x for x in self.node_iterator() if self.get_node_prop(x, 'color') == 'blue'):
            #print('get_node_neighbors -> {}'.format(self.get_node_neighbors(n)))
            for neig in self.get_node_neighbors(n):
                if self.get_node_prop(neig, 'color') != 'blue':
                    change_set.add(neig)
        for n in change_set:
            self.update_node_props(n, color='blue')

        self.enable_updates()

    def tick(self):
        print('calling tick')
        self.diffuse()
