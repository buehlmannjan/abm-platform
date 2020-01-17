class ABMCLient
{
    constructor(model, url)
    {
        if (url === undefined) {
            url = 'ws://localhost:9000/';
        }
        this.finished = false;
        this.stopped = true;

        this.model = model;
        this.ws = new WebSocket(url);

        this.ws.onopen = () => { this.on_open(); };
        this.ws.onerror = (err) => { this.on_error(err); };
        this.ws.onmessage = (evt) => { this.on_message(evt); };
        this.ws.onclose = () => { this.on_close(); };

        this.logger = undefined; // FIXME define logging
        this.timer = undefined;
    }

    on_open()
    {
        console.log('Connect');
        this.model.set_connection(this.ws);
        this.model.send('set_client_type', {
           'type': 'model_client' 
        });
        this.model.create_base();
        this.model.create();
    }

    on_message(evt)
    {
        const data = JSON.parse(evt.data);
        if (data.msg === 'error') {
            console.error(data.value);
        }
        else if (data.msg === 'state_change') {
            this.handle_state_change(data.state);
        }
        else if (data.msg === 'property_change') {
            this.model.handle_property_change(data.prop, data.value);
        }
        else if (data.msg === 'agent_clicked') {
            this.model.handle_agent_clicked(data.data);
        }
        else {
            console.error(`Unknown message type ${data.msg}`);
        }
    }

    on_error(err)
    {
        console.error(`Error ${err}`);
    }

    on_close()
    {
        this.finished = true;
        if (this.timer !== undefined) {
            clearTimeout(this.timer);
            this.timer = undefined;
        }
        console.log("Close");
    }

    tick()
    {
        //console.log("Calling tick");
        this.model.tick();
        if (!this.finished && !this.stopped) {
            if (!this.model.stop_condition()) {
                this.reset_timer();
            }
            else {
                if (!this.stopped) {
                    this.stopped = true;
                    this.stop();
                }
            }
        }
    }

    stop()
    {
        this.model.send('state_change', {
            'state': 'stop'
        });
    }

    reset_timer()
    {
        console.log('reset_timer');
        this.timer = setTimeout(() => { this.tick(); }, this.model.get_timer_speed());
    }

    handle_state_change(state_str)
    {
        if (state_str === 'start') {
            if (this.stopped && !this.finished && !this.model.stop_condition()) {
                this.reset_timer();
                this.stopped = false;
            }
        }
        else if (state_str === 'stop') {
            if (this.timer !== undefined) {
                clearTimeout(this.timer);
                this.timer = undefined;
                this.stopped = true;
            }
        }
        else if (state_str === 'reset') {
            this.model.reset();
            this.finished = false;
            this.stopped = true;
        }
    }
}
