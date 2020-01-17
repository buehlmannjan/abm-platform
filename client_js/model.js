class Model
{
    constructor(config)
    {
        if (config !== undefined)
            this.config = config;
        this.props = {}
        this.charts = []
        this.conn = undefined;

        this.timer_speed = 1000;
        this.pending_msg = [];
        this.enable_updates();
    }

    handle_property_change(prop, value)
    {
        console.error("handle_property_change not implemented");
    }

    handle_agent_clicked(data)
    {
    }

    create()
    {
        console.error("create not implemented");
    }

    tick()
    {
        console.error("tick not implemented");
    }

    set_model_type(kwargs)
    {
        if (kwargs === undefined) {
            console.error("set_model_type not implemented");
        }
        else {
            if (this.__fullname__ === undefined) {
                kwargs.__fullname__ = this.constructor.name;
            }
            else {
                kwargs.__fullname__ = this.__fullname__;
            }
            this.send('set_model_type', kwargs);
        }
    }

    reset()
    {
        console.error("reset not implemented");
    }

    stop_condition()
    {
        return false;
    }

    set_connection(conn)
    {
        this.conn = conn;
    }

    add_property_slider(prop, name, value, range, step)
    {
        this.add_property_generic({
            'type': 'slider',
            'prop': prop,
            'name': name,
            'value': value,
            'range': range,
            'step': step
        });
    }

    add_property_checkbox(prop, name, value)
    {
        this.add_property_generic({
            'type': 'checkbox',
            'prop': prop,
            'name': name,
            'value': value
        });
    }

    add_property_selectbox(prop, name, value, items)
    {
        this.add_property_generic({
            'type': 'checkbox',
            'prop': prop,
            'name': name,
            'value': value,
            'items': items
        });
    }

    add_property_generic(prop)
    {
        this.props[prop.prop] = prop.value;
        this.send('add_property', {
            'prop_data': prop
        });
    }

    create_base()
    {
        this.set_model_type();
    }

    send(msg, args)
    {
        if (args === undefined) {
            args = {};
        }
        args.msg = msg;
        if (!this.updates_enabled) {
            this.pending_msg.push(args);
        }
        else {
            this.send_raw(args);
        }
    }

    send_raw(msg)
    {
        if (this.conn === undefined) {
            console.error("not connected");
        }
        this.conn.send(JSON.stringify(msg));
    }

    set_timer_speed(value)
    {
        this.timer_speed = value;
    }

    get_timer_speed()
    {
        return this.timer_speed;
    }

    disable_updates()
    {
        this.updates_enabled = false;
    }

    enable_updates()
    {
        this.updates_enabled = true;
        if (this.pending_msg.length > 0) {
            this.send('bulk_messages', {
                'data': this.pending_msg
            });
            this.pending_msg = [];
        }
    }

    get_agent_state(...args)
    {

    }

    set_agent_state(...args)
    {

    }

    add_chart(cls, kwargs)
    {
        if (typeof cls == 'string') {
            cls = this.chart_str_to_cls(cls);
        }
        const next_i = this.charts.length;
        const chart = new cls(next_i, this, kwargs);
        this.charts.push(chart);
        return chart;
    }

    chart_str_to_cls(s)
    {
        if (s === 'bar') {
            s = BarChart;
        }
        else if (s === 'ts') {
            s = TSChart;
        }
        else if (s === 'line') {
            s = LineChart;
        }
        else {
            s = undefined;
        }
        return s;
    }
}
