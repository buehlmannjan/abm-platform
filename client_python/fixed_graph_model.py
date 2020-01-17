import json
import graph_model

class FixedGraphModel(graph_model.GraphModel):
    """Fixed layout graph."""
    def __init__(self, config=None):
        if config is None:
            config = {}
        config['layout'] = 'fixed'
        viewport = self.viewport()
        if viewport is not None:
            config['viewport'] = viewport
        super().__init__(config)
    def load_json(self, f):
        """Loads the graph defined as a JSON dictionary in f.

        The f variable may be a filename, string or file-like object.

        The dictionary should contain a node list at key 'nodes' and any
        edges at key 'edges'.

        Each element must be a dictionary:

        nodes: key id defines the node id, additional keys are defined as
            node properties.
            Keys x and y define the position in the fixed layout.
        edges: keys source and target define the each end of the edge.
        """
        obj = None
        if isinstance(f, str):
            try:
                obj = json.loads(f)
            except:
                obj = json.load(open(f, 'r'))
        elif isinstance(f, file):
            obj = json.load(f)
        else:
            raise TypeError('f has invalid type: {}'.format(type(obj)))
        if 'nodes' not in obj or 'edges' not in obj:
            raise TypeError('missing nodes/edges list in JSON input')

        for n in obj['nodes']:
            node_id = n['id']
            del n['id']
            self.add_node(node_id, **n)

        for e in obj['edges']:
            self.add_edge(e['source'], e['target'])
    def viewport(self):
        """4-element list that defines the viewport for the fixed layout.

        Elements correspond to [UL_x, UL_y, LR_x, LR_y], where each position
        represents the boundary coordinates of the viewport:
            * UL_{x,y}: upper left (x, y)
            * LR_{x,y}: lower right (x, y)

        The viewport is computed automatically if None is returned.
        """
        pass
