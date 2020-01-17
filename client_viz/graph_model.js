// global reference for d3 callback functions
let model = null;

class GraphModel extends Model
{
    constructor(manager, config)
    {
        super(manager, config);

        this.type = 'graph';
        this.document = manager.document;

        this.init_config();

        this.layout = d3.forceSimulation()
            .force("link", d3.forceLink().id(function(d) { return d.id; }).strength(0.5))
            .force("charge", d3.forceManyBody())
            .force("center", d3.forceCenter(this.canvas.node().width / 2, this.canvas.node().height / 2))
            .alphaDecay(0.01);

        model = this;

        this.restart_layout();
    }

    init_config()
    {
        if (this.config === undefined)
            this.config = {};
        this.fixed_layout = false;
        if (this.config.layout === 'fixed') {
            this.fixed_layout = true;
            if (this.config.viewport === undefined) {
                // if autoviewport, setup a 10,10 border within the canvas
                this.config.border_x = 10;
                this.config.border_y = 10;
            }
            else {
                this.config.border_x = 0;
                this.config.border_y = 0;
            }
        }
    }

    agent_id(agent)
    {
        return {'id': agent.id};
    }

    import_state(state)
    {
        this.state.node_dict = {};

        this.state.nodes = state.nodes;
        this.state.links = state.links;

        this.state.nodes.forEach(e => {
            this.state.node_dict[e.id] = e;
            if (this.fixed_layout) {
                e.us_x = e.x;
                e.us_y = e.y;
            }
        });

        if (this.fixed_layout)
            this.rescale_fixed_layout();
        if (this.layout)
            this.restart_layout();
    }

    add_node(data)
    {
        const newNode = {
            'id': data.id,
            ...data.props
        };
        this.state.nodes.push(newNode);
        this.state.node_dict[data.id] = newNode;

        if (this.fixed_layout) {
            // save unscaled positions
            newNode.us_x = newNode.x;
            newNode.us_y = newNode.y;
            this.rescale_fixed_layout();
        }

        this.restart_layout();
    }

    rescale_fixed_layout()
    {
        if (this.state.nodes.length > 0) {
            let min, max;
            if (this.config.viewport !== undefined) {
                min = {'x': this.config.viewport[0], 'y': this.config.viewport[1]};
                max = {'x': this.config.viewport[2], 'y': this.config.viewport[3]};
            }
            else {
                [min, max] = this.nodes_minmax_pos();
            }
            this.rescale_nodes_fpos(min, max, this.config.border_x, this.config.border_y);
        }
    }

    nodes_minmax_pos()
    {
        const min = {}; const max = {};
        min.x = this.state.nodes[0].us_x;
        min.y = this.state.nodes[0].us_y;
        max.x = this.state.nodes[0].us_x;
        max.y = this.state.nodes[0].us_y;

        for (let n of this.state.nodes) {
            if (n.us_x < min.x) {
                min.x = n.us_x;
            }
            else if (n.us_x > max.x) {
                max.x = n.us_x;
            }
            if (n.us_y < min.y) {
                min.y = n.us_y;
            }
            else if (n.us_y > max.y) {
                max.y = n.us_y;
            }
        }

        return [min, max];
    }

    rescale_nodes_fpos(min, max, border_x, border_y)
    {
        const width = this.canvas.node().width;
        const height = this.canvas.node().height;

        for (let n of this.state.nodes) {
            // scale proportionally to a box of border_x,border_y pixels within the canvas
            // min_x: border_x; max_x = width - border_x
            // min_y: border_y; max_y = height - border_y
            n.fx = border_x + ((n.us_x - min.x)/(max.x - min.x)) * (width  - 2*border_x);
            n.fy = border_y + ((n.us_y - min.y)/(max.y - min.y)) * (height - 2*border_y);
        }
    }

    update_node_props(data)
    {
        let position_changed = false;
        Object.keys(data.props).forEach(k => {
            // update unscaled positions
            if (k == 'x') {
                this.state.node_dict[data.id]['us_x'] = data.props[k];
                position_changed = true;
            }
            else if (k == 'y') {
                this.state.node_dict[data.id]['us_y'] = data.props[k];
                position_changed = true;
            }
            this.state.node_dict[data.id][k] = data.props[k];
        });

        if (this.fixed_layout && position_changed) {
            this.rescale_fixed_layout();
        }

        this.layout.restart();
    }

    add_edge(data)
    {
        const n0 = data.source;
        const n1 = data.target;

        this.state.links.push({
            'source': this.state.node_dict[n0],
            'target': this.state.node_dict[n1]
        });

        this.restart_layout();
    }

    clear()
    {
        this.import_state({
            'nodes': [],
            'links': []
        });
    }

    restart_layout() {
        this.layout
            .nodes(this.state.nodes)
            .on("tick", ticked);

        this.layout.force("link")
            .links(this.state.links);
    }
}

function ticked()
{
    model.ctx.clearRect(0, 0, model.canvas.node().width, model.canvas.node().height);
    model.hidden_ctx.clearRect(0, 0, model.canvas.node().width, model.canvas.node().height);
  
    // draw links
    model.ctx.beginPath();
    model.state.links.forEach(drawLink);
    model.ctx.strokeStyle = "#aaa";
    model.ctx.stroke();
    model.ctx.closePath();

    // draw nodes in both canvases
    model.state.nodes.forEach((x) => draw_in_canvas(model, x));
    model.state.nodes.forEach((x) => draw_in_hidden_canvas(model, x));
}

function drawLink(d) {
    model.ctx.moveTo(d.source.x, d.source.y);
    model.ctx.lineTo(d.target.x, d.target.y);
}
  
function drawNode(ctx, d, r, stroke, fill) {
    ctx.beginPath();
    ctx.moveTo(d.x + r, d.y);
    ctx.arc(d.x, d.y, r, 0, 2 * Math.PI);
    ctx.strokeStyle = stroke;
    ctx.stroke();
    ctx.fillStyle = fill;
    ctx.fill();
    ctx.closePath();
}

function draw_in_canvas(model, x)
{
    if (x.size === undefined) {
        x.size = 4; // hardcoded default size
    }
    drawNode(model.ctx, x, x.size, "#aaa", x.color);
}

function draw_in_hidden_canvas(model, x)
{
    let color = x.hidden_color;
    if (color === undefined) {
        color = model.__get_next_color();
        x.hidden_color = color;
        model.__color_to_agent[color] = x;
    }
    //console.log(`paint node ${x.id} in hidden canvas color ${color}`);
    // hardcoded marker size
    drawNode(model.hidden_ctx, x, 10, color, color);
}
