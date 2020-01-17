class Chart
{
    constructor(num, parent, kwargs)
    {
        if (kwargs === undefined) {
            kwargs = {};
        }
        this.parent = parent;
        this.num = num;
        this.data = {
            config: {
                type: 'undef',
                ...kwargs
            },
            data: []
        };
        this.x_map = {};
    }

    init_config()
    {
        this.parent.send('add_chart', {
            chart_num: this.num,
            chart_data: this.data
        });
    }

    add_datapoint(x, y, msg_name)
    {
        if (msg_name === undefined) {
            msg_name = 'chart_add_datapoint';
        }
        const d = {x: x, y: y};
        this.x_map[x] = d;
        this.data['data'].push(d);

        this.parent.send(msg_name, {
            chart_num: this.num,
            elem: d
        });
    }

    add_shift_datapoint(x, y)
    {
        if (this.data.config.window_size !== undefined) {
            if (this.data.data.length < this.data.config.window_size) {
                this.add_datapoint(x, y, 'chart_add_shift_datapoint');
            }
            else {
                this.data.data.shift();
                this.add_datapoint(x, y, 'chart_add_shift_datapoint');
            }
        }
        else {
            this.add_datapoint(x, y);
        }
    }

    clear_datapoints()
    {
        this.data.data = [];
        this.parent.send('chart_clear_datapoints', {
            chart_num: this.num
        });
    }

    update_y(x, y)
    {
        this.x_map[x].y = y;
        this.__update_datapoints_internal();
    }

    update_datapoints(dx)
    {
        this.data.data = [];
        for (const [x, y] of dx) {
            this.data.data.push({
                x: x, y: y
            });
        }
        this.__update_datapoints_internal();
    }

    __update_datapoints_internal()
    {
        this.parent.send('chart_update_datapoints', {
            chart_num: this.num,
            values: this.data.data
        });
    }

    update_config(kwargs)
    {
        if (kwargs === undefined) {
            kwargs = {};
        }

        for (const [k, v] in kwargs) {
            this.data.config[k] = v;
        }
        this.parent.send('chart_update_config', {
            chart_num: this.num,
            config: kwargs
        });
    }
}

class BarChart extends Chart
{
    constructor(num, parent, kwargs)
    {
        super(num, parent, kwargs);
        this.data.config.type = 'bar';
        this.init_config();
    }
}

class LineChart extends Chart
{
    constructor(num, parent, kwargs)
    {
        super(num, parent, kwargs);
        this.data.config.type = 'line';
        this.init_config();
    }
}

class ScaterChart extends Chart
{
    constructor(num, parent, kwargs)
    {
        super(num, parent, kwargs);
        this.data.config.type = 'scatter';
        this.init_config();
    }
}

class TSChart extends Chart
{
    constructor(num, parent, kwargs)
    {
        super(num, parent, kwargs);
        if (kwargs === undefined) {
            kwargs = {};
        }
        this.window_size = kwargs.window_size;
        this.t = 0;
        if (kwargs.lines === true) {
            this.data.config.type = 'line';
        }
        else {
            this.data.config.type = 'scatter';
        }
        this.init_config();
    }

    add_datapoint(y)
    {
        const next_t = this.t;
        super.add_datapoint(next_t, y);
        this.t++;
    }

    add_shift_datapoint(y)
    {
        const next_t = this.t;
        super.add_shift_datapoint(next_t, y);
    }
}
