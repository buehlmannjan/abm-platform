import threading
import websocket
import logging
import json

#websocket.enableTrace(True)

class ABMClient(object):
    def __init__(self, model, url='ws://localhost:9000/'):
        self.finished = False
        self.stopped = True
        def handle_prop_change_callback(ws, msg):
            data = json.loads(msg)
            # handle error notifications here
            if data['msg'] == 'error':
                self.logger.error(data['value'])
            elif data['msg'] == 'state_change':
                self.handle_state_change(data['state'])
            elif data['msg'] == 'property_change':
                self.model.handle_property_change(data['prop'], data['value'])
            elif data['msg'] == 'agent_clicked':
                self.model.handle_agent_clicked(data['data'])
            else:
                self.logger.error('Unknown message type: {0}'.format(data[msg]))
        self.model = model
        self.ws = websocket.WebSocketApp(url,
                on_open=lambda ws: self.on_open(ws),
                on_close=lambda ws: self.on_close(ws),
                on_error=lambda ws, err: self.on_error(ws, err),
                on_message=handle_prop_change_callback,
        )
        self.logger = self.init_logging()
        self.timer = None
        #self.reset_timer()

    def init_logging(self):
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        bf = logging.Formatter('{asctime} {name} {levelname:8s} {message}', style='{')
        handler.setFormatter(bf)
        root.addHandler(handler)
        logger = logging.getLogger('client_python')
        return logger

    def on_open(self, ws):
        self.logger.debug('Connect')
        self.model.set_connection(ws)
        self.model.send('set_client_type', type='model_client')
        self.model.create_base()
        self.model.create()

    def on_error(self, ws, err):
        self.logger.debug('Error: {0}'.format(err))

    def on_close(self, ws):
        self.finished = True
        if self.timer is not None:
            self.timer.cancel()
        self.logger.debug('Close')

    def tick(self):
        self.logger.debug('Calling tick')
        self.model.tick()
        if not self.finished and not self.stopped:
            if not self.model.stop_condition():
                self.reset_timer()
            else:
                if not self.stopped:
                    self.stopped = True
                    self.stop()

    def stop(self):
        self.model.send('state_change', state='stop')

    def reset_timer(self):
        self.timer = threading.Timer(self.model.get_timer_speed() / 1000.0, self.tick)
        self.timer.start()

    def handle_state_change(self, state_str):
        if state_str == 'start':
            if self.stopped and not self.finished and not self.model.stop_condition():
                self.reset_timer()
                self.stopped = False
        elif state_str == 'stop':
            if self.timer is not None:
                self.timer.cancel()
                self.stopped = True
        elif state_str == 'reset':
            self.model.reset()
            self.finished = False
            self.stopped = True

    def start(self):
        self.ws.run_forever()
