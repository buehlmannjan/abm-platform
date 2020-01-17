class Chart(object):
    """Defines a generic 2-D chart/plot."""
    def __init__(self, num, parent=None, **kwargs):
        """Creates a new chart with id num.

        * parent: abmclient.
        * kwargs: additional configuration options.

        Configuration options:
            * yOrient: either 'left' or 'right', where the
                y-axis should be facing (default: 'left').
            * yLabel: label for the y-axis.
            * xLabel: label for the x-axis.
            * title: Chart title.
            * yLim: two-element list [minimum, maximum] that defines the
                limits of the y-axis.
            * size: for scatter plots, defines the size of the data point.
        """
        self.parent = parent
        self.num = num
        self.data = {
            'config': {
                'type': 'undef',
            },
            'data': []
        }
        self.data['config'].update(kwargs)
        self.x_map = {}

    def init_config(self):
        """Registers chart in the server using id self.num.
        This method should not be called directly."""
        self.parent.send('add_chart',
            chart_num=self.num,
            chart_data=self.data
        )

    def add_datapoint(self, x, y, msg_name='chart_add_datapoint'):
        """Defines a new point in the chart at (x, y)."""
        d = {'x': x, 'y': y}
        self.x_map[x] = d
        self.data['data'].append(d)

        self.parent.send(msg_name,
            chart_num=self.num,
            elem=d
        )

    def add_shift_datapoint(self, x, y):
        """Defines a new point in the chart at (x, y), removing the oldest
        element if there are more than window_size elements."""
        if self.data['window_size'] is not None:
            if len(self.data['data']) < self.data['window_size']:
                self.add_datapoint(x, y, msg_name='chart_add_shift_datapoint')
            else:
                self.data['data'].pop(0)
                self.add_datapoint(x, y, msg_name='chart_add_shift_datapoint')
        else:
            self.add_datapoint(x, y)

    def clear_datapoints(self):
        """Removes all data points from the chart."""
        self.data['data'] = []
        self.parent.send('chart_clear_datapoints', chart_num=self.num)

    def update_y(self, x, y):
        """Updates value for y given an x.

        If more elements with the same x-value exist, only the last to be
        defined will be updated."""
        self.x_map[x]['y'] = y
        # FIXME it's not necessary to send every single point again
        self.__update_datapoints_internal()

    def update_datapoints(self, dx):
        """Updates data points in the chart using tuple list dx."""
        self.data['data'] = [{'x': x[0], 'y': x[1]} for x in dx]
        self.__update_datapoints_internal()

    def __update_datapoints_internal(self):
        self.parent.send('chart_update_datapoints',
                chart_num=self.num,
                values=self.data['data'])

    def update_config(self, **kwargs):
        """Changes configuration parameters given by kwargs."""
        self.data['config'].update(kwargs)
        self.parent.send('chart_update_config',
                chart_num=self.num,
                config=kwargs)

class BarChart(Chart):
    """A bar chart."""
    def __init__(self, num, parent=None, **kwargs):
        super().__init__(num, parent=parent, **kwargs)
        self.data['config'].update(
            {'type':'bar'}
        )
        self.init_config()

class LineChart(Chart):
    """A line plot."""
    def __init__(self, num, parent=None, **kwargs):
        super().__init__(num, parent=parent, **kwargs)
        self.data['config'].update(
            {'type':'line'}
        )
        self.init_config()

class ScatterChart(Chart):
    """A scatter plot."""
    def __init__(self, num, parent=None, **kwargs):
        super().__init__(num, parent=parent, **kwargs)
        self.data['config'].update(
            {'type':'scatter'}
        )
        self.init_config()

class TSChart(Chart):
    """A time series.

    If lines is true, it specializes a line plot, otherwise it is a scatter plot.

    The extent of the plotted window for add_shift_datapoint is defined by
    attribute window_size."""
    def __init__(self, num, parent=None, window_size=None, lines=False, **kwargs):
        super().__init__(num, parent=parent, window_size=None, **kwargs)
        self.window_size = window_size
        self.t = 0
        self.data['config'].update({
            'type': 'line' if lines else 'scatter',
        })
        # FIXME parameter check should be all server-side
        if self.window_size is not None:
            if self.window_size > 0:
                self.data['config'].update({'window_size':self.window_size})
            else:
                raise ValueError('invalid window size')
        self.init_config()

    def add_datapoint(self, y):
        """Defines a new y value for the time series.

        Specializes add_datapoint(x, y), keeping track of the previous value
        for x (discrete time)."""
        next_t = self.t
        super().add_datapoint(next_t, y)
        self.t += 1

    def add_shift_datapoint(self, y):
        """Defines a new y value for the time series.

        Specializes add_shift_datapoint(x, y), keeping track of the previous value
        for x (discrete time).

        Removes oldest value if there already are window_size elements."""
        next_t = self.t
        super().add_shift_datapoint(next_t, y)
        self.t += 1
