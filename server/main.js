const WebSocketServer = require('ws').Server;
//const Session = require('./session');
const GraphModel = require('./graph_model');
const GridModel = require('./grid_model');
const Client = require('./client');

const server = new WebSocketServer({port: 9000});
const clients = {};

function createClient(conn)
{
    return new Client(conn);
}

function handleMessage(client, msg)
{
    let broadcast = true;
    console.log(`Message received [client_type: ${client.type}] ${msg}`);
    const data = JSON.parse(msg);
    if (data.msg === 'set_client_type') {
        client.set_client_type(data.type);
        if (data.type === 'model_client') {
            if (clients.model_client && client !== clients.model_client) {
                client.error('Model already connected');
                client.disconnect();
            } else {
                clients.model_client = client;
                // reset model if there's a new model client
                client.reset();
                if (clients.viz_client) {
                    clients.viz_client.send({'msg':'reset'});
                }
            }
        }
        else if (data.type === 'viz_client') {
            clients.viz_client = client;
            // set model type and send full state to viz client if there's already a model connected
            if (clients.model_client) {
                client.set_model(clients.model_client.get_model());
                client.send(clients.model_client.get_full_state());
            }
        }
        broadcast = false;
    }
    else if (data.msg === 'set_model_type') {
        let model = undefined;
        if (data.type === 'graph') {
            model = new GraphModel(data.config);
        }
        else if (data.type === 'grid') {
            model = new GridModel(data.config);
        }
        if (model === undefined) {
            console.error(`Invalid model type: ${data.type}`);
            return;
        }
        client.set_model(model);
        if (data.__fullname__ !== undefined) {
            client.set_name(data.__fullname__);
        }
    }
    else if (data.msg === 'add_property') {
        client.add_property(data.prop_data);
    }
    else if (data.msg === 'bulk_messages') {
        if (!client.model) {
            console.log("Model not set");
            return;
        }
        for (let msg of data.data) {
            //console.log(msg);
            if (client.model[msg.msg] === undefined) {
                console.error(`Invalid message (ignoring): ${msg.msg}`);
            } else {
                client.model[msg.msg](msg);
            }
        }
    }
    else if (data.msg === 'state_change') {
        if (clients.model_client) {
            /*if (data.state === 'reset') {
                clients.model_client.model.clear();
            }*/
            console.log(`State change: ${data.state}`);
        }
    }
    else if (data.msg === 'agent_clicked') {
        if (clients.model_client) {
            console.log(`Agent clicked: ${JSON.stringify(data.data)}`);
        }
    }
    else {
        if (client.model) {
            if (client.model[data.msg] === undefined) {
                console.error(`Invalid message: ${data.msg}`);
            } else {
                client.model[data.msg](data);
            }
        }
        else {
            console.log("Model not set");
        }
    }

    if (broadcast) {
        // broadcast to the other client
        if (client === clients['viz_client'] && clients['model_client'])
            clients['model_client'].send(data);
        else if (client === clients['model_client'] && clients['viz_client'])
            clients['viz_client'].send(data);
    }
}

server.on('connection', conn => {
    console.log('Connection established');
    const client = createClient(conn);

    conn.on('message', (msg) => {
        handleMessage(client, msg);
    });

    conn.on('close', () => {
        console.log('Connection closed');
        // FIXME remove pointer (clients.model_client or clients.viz_client)
        if (client === clients.viz_client) {
            clients.viz_client = undefined;
        }
        else if (client === clients.model_client) {
            clients.model_client = undefined;
            // reset viz if model disconnects
            if (clients.viz_client) {
                clients.viz_client.send({'msg': 'reset'});
            }
        }
    });
});
