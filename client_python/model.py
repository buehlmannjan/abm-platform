from chart import BarChart, TSChart, LineChart

import json
import websocket

class Model(object):
    def __init__(self, config=None):
        self.config = config if config is not None else {}
        self.props = {}
        self.charts = []
        self.conn = None

        self.timer_speed = 1000 # 1 sec default timer
        self.pending_msg = []
        self.enable_updates()

    def handle_property_change(self, prop, value):
        raise NotImplementedError('handle_property_change not implemented')

    def handle_agent_clicked(self, data):
        pass

    def create(self):
        raise NotImplementedError('create not implemented')

    def tick(self):
        raise NotImplementedError('tick not implemented')

    def set_model_type(self, **kwargs):
        if len(kwargs) == 0:
            raise NotImplementedError('set_model_type not implemented')
        else:
            if hasattr(self, '__fullname__'):
                kwargs['__fullname__'] = self.__fullname__
            else:
                kwargs['__fullname__'] = self.__class__.__name__
            self.send('set_model_type', **kwargs)

    def reset(self):
        raise NotImplementedError('reset not implemented')

    def stop_condition(self):
        return False

    def set_connection(self, conn):
        self.conn = conn

    # FIXME deprecated
    def add_property(self, *args):
        # backwards-compatible API
        self.add_property_slider(*args)

    def add_property_slider(self, prop, name, value, range, step):
        self.add_property_generic(
            type='slider',
            prop=prop,
            name=name,
            value=value,
            range=range,
            step=step
        )

    def add_property_checkbox(self, prop, name, value):
        self.add_property_generic(
            type='checkbox',
            prop=prop,
            name=name,
            value=value
        )

    def add_property_selectbox(self, prop, name, value, items):
        self.add_property_generic(
            type='selectbox',
            prop=prop,
            name=name,
            value=value,
            items=items
        )

    def add_property_generic(self, **kwargs):
        self.props[kwargs['prop']] = kwargs['value']
        self.send('add_property', prop_data=kwargs)

    # FIXME this might not be required as a separated step
    def create_base(self):
        self.set_model_type()

    def send(self, msg, **kwargs):
        kwargs.update({'msg': msg})
        if not self.updates_enabled:
            # queue message
            self.pending_msg.append(kwargs)
        else:
            self.send_raw(kwargs)

    def send_raw(self, msg):
        if self.conn is None:
            raise RuntimeError('not connected')
        self.conn.send(json.dumps(msg))

    def set_timer_speed(self, value):
        self.timer_speed = value

    def get_timer_speed(self):
        return self.timer_speed

    def disable_updates(self):
        self.updates_enabled = False

    def enable_updates(self):
        self.updates_enabled = True
        if len(self.pending_msg) > 0:
            self.send('bulk_messages', data=self.pending_msg)
            self.pending_msg = []

    def get_agent_state(self, *args):
        pass

    def set_agent_state(self, *args):
        pass

    def add_chart(self, cls, **kwargs):
        if isinstance(cls, str):
            cls = self.chart_str_to_cls(cls)
        next_i = len(self.charts)
        chart = cls(next_i, parent=self, **kwargs)
        self.charts.append(chart)
        return chart

    @staticmethod
    def chart_str_to_cls(s):
        if s == 'bar':
            s = BarChart
        elif s == 'ts':
            s = TSChart
        elif s == 'line':
            s = LineChart
        else:
            s = None
        return s
