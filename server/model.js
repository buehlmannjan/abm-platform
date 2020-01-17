class Model
{
    constructor(config)
    {
        this.config = config;
        this.model_state = {};
        this.reset();        
    }

    reset()
    {
        this.model_state.props = [];
        this.props_dict = {};
        this.model_state.charts = [];
        this.clear();
    }

    add_property(prop)
    {
        //console.log(prop);
        this.model_state.props.push(prop);
        this.props_dict[prop.prop] = prop;
    }

    property_change(data)
    {
        //console.log(this.model_state.props_dict);
        //console.log(data);
        this.props_dict[data.prop].value = data.value;
    }

    add_chart(data)
    {
        this.model_state.charts.push(data.chart_data);
    }

    chart_set_full_data(data)
    {
        this.model_state.charts[data.chart_num] = data.chart_data;
    }

    chart_add_datapoint(data)
    {
        this.model_state.charts[data.chart_num].data.push(data.elem);
    }

    chart_add_shift_datapoint(data)
    {
        const d = this.model_state.charts[data.chart_num].data;
        if (d.length < this.model_state.charts[data.chart_num].window_size) {
            d.push(data.elem);
        } else {
            d.shift();
            d.push(data.elem);
        }
    }

    chart_update_datapoints(data)
    {
        this.model_state.charts[data.chart_num].data = data.values;
    }

    chart_clear_datapoints(data)
    {
        this.model_state.charts[data.chart_num].data = [];
    }

    chart_update_config(data)
    {
        for (let k in data.config) {
            this.model_state.charts[data.chart_num].config[k] = data.config[k];
        }
    }

    serialize()
    {
        return JSON.stringify(this);
    }
}

module.exports = Model;
