class Model
{
    constructor(manager, config, tx, ty) {
        this.manager = manager;
        this.config = config;
        this.container = d3.select(".model_container");
        this.state = {'props':[]};
        this.charts = {};
        this.updates_enabled = true;
        this.translationX = tx;
        this.translationY = ty;

        this.reset();
        this.init_canvas();
        this.init_hidden_canvas();
        this.init_mouse_events();
        this.init_tooltip();
    }

    init_canvas()
    {
        this.canvas = this.container.select("canvas");
        if (this.canvas) {
            this.canvas.remove();
        }
        this.width = this.container.node().clientWidth;
        this.height = this.container.node().clientHeight;
        this.canvas = this.container.append("canvas")
            .attr('width', this.width)
            .attr('height', this.height);
        //this.canvas.node().style.display = 'none';
        this.ctx = this.canvas.node().getContext("2d");
        this.ctx.translate(this.translationX, this.translationY);

        this.manager.document.defaultView.addEventListener('resize', () => {
            //console.log('resize event');
            this.width = this.container.node().clientWidth;
            this.height = this.container.node().clientHeight;
            this.canvas
                .attr("width", this.container.node().clientWidth)
                .attr("height", this.container.node().clientHeight);
            if (this.hidden_canvas !== undefined) {
                this.hidden_canvas
                    .attr("width", this.container.node().clientWidth)
                    .attr("height", this.container.node().clientHeight);
            }
            this.redraw();
        });
    }

    init_hidden_canvas()
    {
        this.hidden_canvas = this.container.append("canvas")
            .attr('width', this.width)
            .attr('height', this.height);
        this.hidden_canvas.node().style.display = 'none';
        this.hidden_ctx = this.hidden_canvas.node().getContext("2d");
        this.hidden_ctx.translate(this.translationX, this.translationY);

        this.__reset_lookup_colors();
    }

    init_tooltip()
    {
        this.tooltip_container = this.container.append('div').attr('id', 'tooltip');
    }

    init_mouse_events()
    {
        this.canvas.on('mousemove', () => {
            const agent = this.canvas_mouse_evt_to_agent(d3.event);
            //console.log(cell);
            if (agent && agent.tooltip !== undefined) {
                this.draw_tooltip(agent);
            }
            else {
                this.hide_tooltip();
            }
        });

        this.canvas.on('click', () => {
            const agent = this.canvas_mouse_evt_to_agent(d3.event);

            if (agent) {
                this.notify_agent_clicked(agent);
            }
        });
    }

    canvas_mouse_evt_to_agent(e)
    {
        const canvas = this.canvas.node();
        const mouseX = e.clientX - canvas.offsetLeft;
        const mouseY = e.clientY - canvas.offsetTop;
        const col = this.hidden_ctx.getImageData(mouseX, mouseY, 1, 1).data;
        //console.log(`canvas_mouse_evt_to_agent(${mouseX}, ${mouseY}): ${col}`);
        return this.__color_to_agent[this.__color_string(col[0], col[1], col[2])];
    }

    destroy()
    {
        this.canvas.remove();
        this.hidden_canvas.remove();
        this.tooltip_container.remove();
    }

    notify_agent_clicked(agent)
    {
        this.manager.send({
            'msg': 'agent_clicked',
            'data': this.agent_id(agent)
        });
    }

   add_property(prop)
    {
        this.state.props.push(prop);

        const id = prop.prop;
        console.log(`Define property change callback for ${id}`);

        if (prop.type === 'slider') {
            d3.select(`input[id=${id}]`).on("input", change_slider_callback(this.manager, id));
        }
        else if (prop.type === 'checkbox') {
            d3.select(`input[id=${id}]`).on("change", change_checkbox_callback(this.manager, id));
        }
        else if (prop.type === 'selectbox') {
            d3.select(`select[id=${id}]`).on("input", change_selectbox_callback(this.manager, id));
        }
    }

    remove_properties()
    {
        /* FIXME: it's not necessary to remove event handlers since elements are being removed from the DOM (?)
        if (this.state.props) {
            for (let prop of this.state.props) {
                d3.select(`input[id=${prop.prop}]`).on("input", null);
            }
        }*/
        this.state.props = [];
    }

    remove_charts()
    {
        this.charts = {};
    }

    add_chart(id, chart)
    {
        this.charts[id] = chart;
    }

    draw_tooltip(agent)
    {
        this.tooltip_container
            .style('opacity', 0.8)
            .style('top', d3.event.pageY + 5 + 'px')
            .style('left', d3.event.pageX + 5 + 'px')
            .html('info: ' + agent.tooltip);
    }

    hide_tooltip()
    {
        this.tooltip_container.style('opacity', 0);
    }

    reset()
    {
        //this.remove_properties();
        this.clear();
    }

    serialize()
    {
        return JSON.stringify({
            'type': this.type,
            'state': this.state,
        });
    }

    redraw()
    {
    }

    enable_updates()
    {
        this.updates_enabled = false;
    }

    disable_updates()
    {
        this.updates_enabled = false;
    }

    __get_next_color()
    {
        let r, g, b;
        if (this.__next_color >= 16777215) {
            this.__next_color = 1; // cycle
        }
        r = (this.__next_color & 0xff);
        g = (this.__next_color & 0xff00) >> 8;
        b = (this.__next_color & 0xff0000) >> 16;

        this.__next_color += 1;

        const c = this.__color_string(r, g, b);
        //console.log(`__get_next_color: ${c}`);
        return c;
    }

    __reset_lookup_colors()
    {
        this.__color_to_agent = {};
        this.__next_color = 1;
    }

    __color_string(r, g, b)
    {
        return "rgb(" + [r, g, b].join(',') + ")";
    }

    chart_add_datapoint(data)
    {
        this.charts[data.chart_num].add_datapoint(data.elem);
    }

    chart_add_shift_datapoint(data)
    {
        this.charts[data.chart_num].add_shift_datapoint(data.elem);
    }

    chart_clear_datapoints(data)
    {
        this.charts[data.chart_num].clear_datapoints();
    }

    chart_update_datapoints(data)
    {
        this.charts[data.chart_num].update_datapoints(data);
    }

    chart_update_config(data)
    {
        this.charts[data.chart_num].update_config(data);
    }
}

function change_slider_callback(manager, id)
{
    return function() {
        const value = parseFloat(this.value).toPrecision(2);
        manager.send({
            'msg': 'property_change',
            'prop': id,
            'value': parseFloat(value)
        });
        d3.select(`output[for=${id}]`)._groups[0][0].innerText = value;
    };
}

function change_checkbox_callback(manager, id)
{
    return function() {
        manager.send({
            'msg': 'property_change',
            'prop': id,
            'value': this.checked
        });
    };
}

function change_selectbox_callback(manager, id)
{
    return function() {
        manager.send({
            'msg': 'property_change',
            'prop': id,
            'value': this.value
        });
    };
}
