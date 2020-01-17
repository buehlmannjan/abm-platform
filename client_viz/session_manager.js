class SessionManager
{
    constructor(document)
    {
        this.document = document;

        this.settings = [];
        this.charts = [];
        this.model = null;
        this.started = false;

        this.set_status_msg('red', 'Disconnected');
        this.set_model_msg('red', '(none)');
        this.init_buttons();
        this.set_button_state(false);
    }

    connect(url)
    {
        this.conn = new WebSocket(url);

        this.conn.addEventListener('open', () => {
            console.log('Connection established');
            this.set_status_msg('green', `Connected to ${url}`);
            this.remove_properties(); // reset properties if set
            this.remove_charts(); // same with charts
            this.send({
                'msg': 'set_client_type',
                'type': 'viz_client'
            });
        });
        
        this.conn.addEventListener('message', event => {
            //console.log('Received message', event.data);
            this.receive(event.data);
        });

        this.conn.addEventListener('close', () => {
            console.log('Server closed connection');
            // FIXME this is also in the constructor
            this.set_status_msg('red', 'Disconnected');
            this.destroy_model();
        });
    }

    receive(msg)
    {
        const data = JSON.parse(msg);
        //console.log(`Received data after JSON.parse -> ${data.msg}`);
        if (data.msg === 'full_state') {
            this.import_state(data.state);
        }
        else if (data.msg === 'set_model_type') {
            if (data.type === 'graph') {
                this.create_model(GraphModel, data.config);
            } else if (data.type === 'grid') {
                this.create_model(GridModel, data.config);
            }
            this.set_model_msg('green', data.__fullname__);
            this.model.__fullname__ = data.__fullname__;
            //console.log(data);
        }
        else if (data.msg === 'reset') {
            this.set_model_msg('red', '(none)');
            this.destroy_model();
        }
        else if (data.msg === 'state_change') {
            if (!this.model) {
                console.log('Model not set');
                return;
            }
            if (data.state === 'stop' && this.started) {
                // change play/stop button if model decides to stop
                this.set_play_button_text(false);
            }
        }
        else if (data.msg === 'add_property') {
            if (!this.model) {
                console.log('Model not set');
                return;
            }
            this.add_property(data.prop_data);
        }
        else if (data.msg === 'add_chart') {
            if (!this.model) {
                console.log('Model not set');
                return;
            }
            this.add_chart(data.chart_num, data.chart_data);
        }
        else if (data.msg === 'bulk_messages') {
            if (!this.model) {
                console.log("Model not set");
                return;
            }
            this.model.disable_updates();
            for (let msg of data.data) {
                if (this.model[msg.msg] === undefined) {
                    console.error(`Invalid message (ignoring): ${msg.msg}`);
                } else {
                    this.model[msg.msg](msg);
                }
            }
            this.model.enable_updates();
        }
        else {
            if (!this.model) {
                console.log('Model not set');
                return;
            }
            if (this.model[data.msg] === undefined) {
                console.error(`Invalid message (ignoring): ${data.msg}`);
            } else {
                this.model[data.msg](data);
            }
        }
    }

    send(msg)
    {
        const data = JSON.stringify(msg);
        this.conn.send(data);
    }

    import_state(state)
    {
        // set model type
        this.model = undefined;
        if (state.type === 'graph') {
            console.log('create GraphModel');
            this.create_model(GraphModel, state.config);
        } else if (state.type === 'grid') {
            console.log('create GridModel');
            this.create_model(GridModel, state.config);
        }
        if (this.model === undefined) {
            console.log('Invalid model');
            return;
        }
        this.model.__fullname__ = state.__fullname__;
        this.set_model_msg('green', state.__fullname__);

        // remove old properties and reset
        this.remove_properties();
        for (let prop of state.model_state.props) {
            this.add_property(prop);
        }

        // remove old charts and reset
        let chart_num = 0;
        this.remove_charts();
        for (let chart of state.model_state.charts) {
            this.add_chart(chart_num, chart);
            chart_num++;
        }

        // set data
        //console.log(`en import_state de session_manager: import ${Object.keys(state)}`);
        this.model.import_state(state.model_state);

        // stop if it was playing before
        this.stop_model();
    }

    add_property(data)
    {
        if (data.type === 'slider') {
            this.add_slider(data.prop, data.name, data.value, data.range, data.step);
        }
        else if (data.type === 'checkbox') {
            this.add_checkbox(data.prop, data.name, data.value);
        }
        else if (data.type === 'selectbox') {
            this.add_selectbox(data.prop, data.name, data.value, data.items);
        }
    }

    add_slider(prop, name, value, range, step)
    {
        const container = d3.select('.settings_container').append('div')
            .classed('settings', 1);

        this.settings.push({
            'type': 'slider',
            'prop': prop,
            'value': value,
            'element': container.node()
        });

        container.append('label')
            .attr('for', prop)
            .classed('setting_text', 1)
            .text(name);

        container.append('input')
            .attr('name', prop)
            .attr('id', prop)
            .attr('type', 'range')
            .attr('min', range[0])
            .attr('max', range[1])
            .attr('step', step)
            .attr('value', value);

        container.append('output')
            .attr('name', 'value')
            .attr('for', prop)
            .classed('setting_value', 1)
            .text(value);

        this.model.add_property({
            'type': 'slider',
            'prop': prop,
            'name': name,
            'value': value,
            'range': range,
            'step': step
        });
    }

    add_checkbox(prop, name, value)
    {
        let container = d3.select('.settings_container').append('div')
            .classed('checkbox_container', 1)
            .text(name);

        this.settings.push({
            'type': 'checkbox',
            'prop': prop,
            'value': value,
            'element': container.node()
        });

        container = container
            .append('label')
            .classed('control control--checkbox', 1);

        container.append('input')
            .attr('type', 'checkbox')
            .attr('id', prop);

        container.append('div')
            .classed('control__indicator', 1);

        this.model.add_property({
            'type': 'checkbox',
            'prop': prop,
            'name': name,
            'value': value
        });
    }

    add_selectbox(prop, name, value, items)
    {
        const element = d3.select('.settings_container')
            .append('div')
                .classed('selectbox_container', 1)
                .text(name);

        const container = element.append('div').classed('select', 1);

        this.settings.push({
            'type': 'selectbox',
            'prop': prop,
            'value': value,
            'element': element.node()
        });

        const select = container.append('select')
            .attr('id', prop);

        for (let i of items) {
            select.append('option').text(i);
        }

        container.append('div').classed('select__arrow', 1);

        this.model.add_property({
            'type': 'selectbox',
            'prop': prop,
            'name': name,
            'items': items
        });
    }

    add_chart(id, chart_data)
    {
        const container = this.document.getElementsByClassName('charts_container')[0];
        const config = chart_data.config;

        const element = this.document.createElement('div');
        element.className = 'chart';

        container.appendChild(element);

        this.model.add_chart(id, new Chart(id, this, element, config, chart_data.data));

        this.charts.push(element);
    }

    remove_properties()
    {
        const container = this.document.getElementsByClassName('settings_container')[0];

        for (let prop of this.settings) {
            //console.log(prop.element);
            container.removeChild(prop.element);
        }
        this.settings = [];

        if (this.model) {
            this.model.remove_properties();
        }
    }

    remove_charts()
    {
        const container = this.document.getElementsByClassName('charts_container')[0];

        for (let chart of this.charts) {
            container.removeChild(chart);
        }
        this.charts = [];

        if (this.model) {
            this.model.remove_charts();
        }
    }

    set_status_msg(color, msg)
    {
        const msg_container = d3.select('#status_msg');
        msg_container.node().style.color = color;
        msg_container.text(msg);
    }

    set_model_msg(color, msg)
    {
        const msg_container = d3.select('#model_msg');
        msg_container.node().style.color = color;
        msg_container.text(msg);
    }

    init_buttons()
    {
        const play_button = this.document.getElementsByClassName('play_button')[0];
        const reset_button = this.document.getElementsByClassName('reset_button')[0];

        play_button.innerHTML = 'Play';
        reset_button.innerHTML = 'Reset';

        play_button.addEventListener('click', () => {
            if (this.started) {
                this.stop_model();
            } else {
                this.start_model();
            }
            this.set_play_button_text(this.started);
        });
        reset_button.addEventListener('click', () => { this.reset_model(); });
    }

    set_play_button_text(started)
    {
        const play_button = d3.select('.play_button');
        if (started) {
            play_button.text('Stop');
        } else {
            play_button.text('Play');
        }
        this.started = started;
    }

    set_button_state(enabled)
    {
        const play_button = this.document.getElementsByClassName('play_button')[0];
        const reset_button = this.document.getElementsByClassName('reset_button')[0];

        // reset play_button text
        play_button.innerHTML = 'Play';

        if (enabled) {
            play_button.removeAttribute('disabled');
            reset_button.removeAttribute('disabled');
        } else {
            play_button.setAttribute('disabled',"");
            reset_button.setAttribute('disabled',"");
        }
    }

    create_model(t, config)
    {
        //console.log(`layout: ${config.layout}`);
        this.model = new t(this, config);
        this.started = false;

        this.set_button_state(true);
    }

    destroy_model()
    {
        this.remove_properties();
        this.remove_charts();

        if (this.model) {
            this.model.destroy();
            this.started = false;
            this.model = null;
        }

        this.set_button_state(false);
    }

    start_model()
    {
        if (this.model) {
            this.started = true;
            this.send({
                'msg': 'state_change',
                'state': 'start'
            });
        }
    }

    stop_model()
    {
        if (this.model) {
            this.started = false;
            this.send({
                'msg': 'state_change',
                'state': 'stop'
            });
        }
    }

    reset_model()
    {
        if (this.model) {
            this.started = false;
            this.send({
                'msg': 'state_change',
                'state': 'reset'
            });
        }
    }
}
