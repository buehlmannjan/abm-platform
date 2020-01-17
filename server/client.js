class Client
{
    constructor(conn)
    {
        this.conn = conn;
        this.type = 'undef';
        this.model = null;
    }

    disconnect()
    {
        this.conn.close();
    }

    set_client_type(type) 
    {
        this.type = type;
    }

    get_model()
    {
        return this.model;
    }

    reset()
    {
        if (this.model) {
            this.model.reset();
        }
    }

    set_model(model)
    {
        //console.log(`client.js: set_model ${model} ${typeof model}`);
        this.model = model;
    }

    add_property(prop)
    {
        console.log(`add_property prop->${Object.keys(prop)}`);
        if (!this.model) {
            console.log("add_property: Model not set");
            return;
        }
        this.model.add_property(prop);
    }

    get_full_state()
    {
        const full_state = {
            'msg': 'full_state',
            'state': {},
        };

        if (this.model !== undefined) {
            full_state.state = this.model;
        }
        return full_state;
    }

    set_name(name)
    {
        if (this.model !== undefined) {
            this.model.__fullname__ = name;
        }
    }

    error(msg)
    {
        this.send({'msg':'error', 'value':msg});
    }

    send(data)
    {
        const msg = JSON.stringify(data);
        console.log(`Sending message [client_type: ${this.type}] ${msg}`);
        this.conn.send(msg, function ack(err) {
		    if (err) {
			    console.log('Error sending message', msg, err);
		    }
	    });
    }
}

module.exports = Client;
