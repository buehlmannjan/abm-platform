import fixed_graph_model

graph = '''{"edges":[
{"source":6, "target":20},
{"source":12, "target":0},
{"source":23, "target":13},
{"source":3, "target":1},
{"source":7, "target":20},
{"source":25, "target":3},
{"source":4, "target":11},
{"source":16, "target":20},
{"source":9, "target":0},
{"source":25, "target":13},
{"source":16, "target":4},
{"source":4, "target":13},
{"source":5, "target":15},
{"source":4, "target":17},
{"source":9, "target":25},
{"source":4, "target":25},
{"source":16, "target":8},
{"source":6, "target":5},
{"source":6, "target":18},
{"source":4, "target":5},
{"source":9, "target":19},
{"source":9, "target":20},
{"source":4, "target":14},
{"source":9, "target":5},
{"source":4, "target":15},
{"source":12, "target":3},
{"source":0, "target":1},
{"source":9, "target":17},
{"source":17, "target":15},
{"source":23, "target":18},
{"source":16, "target":5},
{"source":4, "target":23},
{"source":24, "target":6},
{"source":9, "target":14},
{"source":16, "target":6}
],
"nodes":[
{"y":134.324462891,"x":-113.536003113,"id":20,"label":"node1"},
{"y":51.229637146,"x":155.395904541,"id":25,"label":"node2"},
{"y":46.6591949463,"x":-207.792068481,"id":13,"label":"node3"},
{"y":27.60389328,"x":133.966064453,"id":2,"label":"node4"},
{"y":126.531860352,"x":-26.9523639679,"id":24,"label":"node5"},
{"y":163.070098877,"x":-86.976524353,"id":7,"label":"node6"},
{"y":-221.938049316,"x":-80.8975143433,"id":21,"label":"node7"},
{"y":52.953651428,"x":-95.7600021362,"id":4,"label":"node8"},
{"y":-12.805847168,"x":189.149490356,"id":12,"label":"node9"},
{"y":141.481781006,"x":-60.2801208496,"id":6,"label":"node10"},
{"y":-81.550979614,"x":112.394180298,"id":3,"label":"node11"},
{"y":23.1120529175,"x":225.898086548,"id":17,"label":"node12"},
{"y":-87.168624878,"x":-78.1010284424,"id":14,"label":"node13"},
{"y":65.189682007,"x":-212.771820068,"id":11,"label":"node14"},
{"y":-176.750244141,"x":58.5323791504,"id":1,"label":"node15"},
{"y":-52.795600891,"x":154.782455444,"id":0,"label":"node16"},
{"y":176.595153809,"x":30.1155319214,"id":8,"label":"node17"},
{"y":84.641799927,"x":185.32460022,"id":19,"label":"node18"},
{"y":-157.174133301,"x":-258.442382812,"id":10,"label":"node19"},
{"y":77.960739136,"x":53.8596191406,"id":9,"label":"node20"},
{"y":67.204818726,"x":-68.0021133423,"id":5,"label":"node21"},
{"y":50.07220459,"x":-2.34326410294,"id":18,"label":"node22"},
{"y":37.9620285034,"x":-138.772369385,"id":23,"label":"node23"},
{"y":94.446624756,"x":-48.3559761047,"id":16,"label":"node24"},
{"y":155.012207031,"x":-64.1417312622,"id":22,"label":"node25"},
{"y":21.2733154297,"x":110.682693481,"id":15,"label":"node26"}
]}'''

class ShowGraphModel(fixed_graph_model.FixedGraphModel):
    def handle_property_change(self, prop, value):
        pass

    def create(self):
        self.load_json(graph)

    def tick(self):
        pass

    def reset(self):
        pass
