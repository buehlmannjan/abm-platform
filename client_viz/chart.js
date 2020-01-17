class Chart
{
    constructor(id, manager, container, config, data)
    {
        this.id = id;
        this.manager = manager;
        this.container = container;
        this.config = this.init_config_with_defaults(config);

        this.chart_data = [];
        if (data !== undefined) {
            this.chart_data = data;
        }

        this.area = this.get_series_from_type(this.config.type)
            .crossValue(d => d.x)
            .mainValue(d => d.y);

        this.xExtent = fc.extentLinear()
            .accessors([d => d.x]);

        this.yExtent = fc.extentLinear()
            .accessors([d => d.y]);

        this.chart = undefined;

        if (this.config.type === 'bar') {
            this.chart = fc.chartCartesian(
                d3.scaleBand(),
                d3.scaleLinear()
            )
            .xPadding(0.2);
            this.xExtent = (data => (data.map(d => d.x)));
        }
        else {
            this.chart = fc.chartCartesian(
                d3.scaleLinear(),
                d3.scaleLinear()
            )
            .xNice();
        }
        //console.log(this.chart);

        this.config_chart();
        this.update();
    }

    config_chart()
    {
        if (this.area.size && this.config.size) {
            this.area = this.area.size(this.config.size);
        }

        if (this.config.yLim !== undefined) {
            this.yExtent = (() => this.config.yLim);
        }
        else {
            this.yExtent = fc.extentLinear().accessors([d => d.y]);
            this.chart.yNice();
        }

        this.chart
            .yOrient(this.config.yOrient)
            .yLabel(this.config.yLabel)
            .xLabel(this.config.xLabel)
            .chartLabel(this.config.title)
            .canvasPlotArea(this.area);
    }

    set_id(num)
    {
        this.id = num;
    }

    add_datapoint(elem)
    {
        this.chart_data.push(elem);
        this.update();
    }

    add_shift_datapoint(elem)
    {
        if (this.config.window_size === undefined) {
            this.add_datapoint(elem);
        }
        else {
            this.chart_data.push(elem);
            if (this.chart_data.length >= this.config.window_size) {
                this.chart_data.shift();
            }
            this.update();
        }
    }

    update_datapoints(data)
    {
        this.chart_data = data.values;
        this.update();
    }

    clear_datapoints()
    {
        this.chart_data = [];
        this.update();
    }

    update_config(data)
    {
        for (let k in data.config) {
            this.config[k] = data.config[k];
        }

        this.config_chart();
        this.update();
    }

    update()
    {
        this.chart
            .yDomain(this.yExtent(this.chart_data))
            .xDomain(this.xExtent(this.chart_data));

        d3.select(this.container)
            .datum(this.chart_data)
            .call(this.chart);
    }

    get_series_from_type(type)
    {
        let series = fc.seriesCanvasLine();
        if (type === 'scatter') {
            series = fc.seriesCanvasPoint();
        }
        else if (type === 'bar') {
            series = fc.autoBandwidth(fc.seriesCanvasBar()).align('left');
        }
        return series;
    }

    init_config_with_defaults(config)
    {
        if (config.type === undefined) {
            config.type = 'line';
        }
        if (config.yOrient === undefined) {
            config.yOrient = 'left';
        }
        if (config.yLabel === undefined) {
            config.yLabel = 'y';
        }
        if (config.xLabel === undefined) {
            config.xLabel = 'x';
        }
        if (config.title === undefined) {
            config.title = `Chart ${this.id}`;
        }

        if (config.type === 'scatter' && config.size === undefined) {
            config.size = 1;
        }

        return config;
    }
}
