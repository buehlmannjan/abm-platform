const Model = require("./model");
class GraphModel extends Model
{
    constructor(config)
    {
        super(config);
        this.type = 'graph';
    }

    import_state(state)
    {
        this.model_state.nodes = state.nodes;
        this.model_state.links = state.links;

        this.generate_node_dict();
    }

    generate_node_dict()
    {
        this.model_state.node_dict = {};
        this.model_state.nodes.forEach(e => {
            this.model_state.node_dict[e.id] = e;
        });
    }

    clear()
    {
        this.import_state({
            'nodes': [],
            'links': []
        });
    }

    add_node(data)
    {
        const node = {
            'id': data.id,
            ...data.props
        };
        this.model_state.nodes.push(node);
        this.model_state.node_dict[data.id] = node;
    }

    update_node_props(data)
    {
        //console.log("before update_node_props");
        //console.log(this.model_state.node_dict[data.id]);
        Object.keys(data.props).forEach(k => {
            this.model_state.node_dict[data.id][k] = data.props[k];
        });
        //console.log("after update_node_props");
        //console.log(this.model_state.node_dict[data.id]);
    }

    add_edge(data)
    {
        //console.log('estoy agregando un link en el graph_model del server');
        this.model_state.links.push({
            'source': data.source,
            'target': data.target
        });
    }
}

module.exports = GraphModel;
