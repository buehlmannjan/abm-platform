const TreeState = {
    'ALIVE': 'green',
    'BURNING': 'red',
    'DEAD': 'black',
    'EMPTY': 'white'
};

class ForestFireModel extends GridModel
{
    constructor()
    {
        super();
        this.burn_steps = 20;
        this.size = 0;
        this.set_timer_speed(500);
        this.burning_count_chart = undefined;
        this.chart_steps = 0;
        this.alive_orig_count = 0;

        this.__fullname__ = 'Forest Fire';
    }

    handle_property_change(prop, value)
    {
        if (prop === 'size') {
            this.forest(value);
        }
        else if (prop === 'probability') {
            this.forest(this.size, value);
        }
        else if (prop === 'speed') {
            this.set_timer_speed(value);
        }
    }

    handle_agent_clicked(data)
    {
        const row = data.row;
        const col = data.col;

        if (this.get_agent_state(row, col) === TreeState.ALIVE) {
            this.set_on_fire(row, col);
        }
    }

    set_on_fire(row, col)
    {
        this.burning_count += 1;
        this.alive_count -= 1;
        this.set_agent_state(row, col, TreeState.BURNING);
        this.update_charts();
    }

    stop_condition()
    {
        return this.alive_count == 0 && this.burning_count == 0;
    }

    forest(size, prob, rebuild)
    {
        if (size <= 0) {
            console.error('invalid forest size');
        }
        if (prob !== undefined) {
            this.prob = prob;
        }
        if (rebuild === undefined) {
            rebuild = true;
        }
        let old_size = this.size;
        this.size = size;

        if (rebuild) {
            this.create_grid(size, size, (row, col) => {
                let c = TreeState.EMPTY;
                if (Math.random() < this.prob) {
                    c = TreeState.ALIVE;
                }
                return {'color': c};
            });
            this.alive_orig_count = 0;
            for (let i = 0; i < size; i++) {
                for (let j = 0; j < size; j++) {
                    if (this.get_agent_state(i, j) === TreeState.ALIVE) {
                        this.alive_orig_count += 1;
                    }
                }
            }
        }
        else {
            if (old_size != size) {
                console.error('forest size change with rebuild=False');
            }
            this.disable_updates();
            for (let i = 0; i < size; i++) {
                for (let j = 0; j < size; j++) {
                    let cur_state = this.get_agent_state(i, j);
                    if (cur_state != TreeState.EMPTY) {
                        this.set_agent_state(i, j, TreeState.ALIVE);
                    }
                }
            }
            this.enable_updates();
        }
        this.reset_charts();

        for (let i = 0; i < size; i++) {
            for (let j = 0; j < size; j++) {
                this.update_cell_state(i, j, {
                    'steps': 0
                });
            }
        }    
    }

    create()
    {
        const size = 50;
        const speed = 0.1;
        const prob = 0.5;

        this.add_property_slider('size', 'Grid Size', size, [1, 100], 1);
        this.add_property_slider('probability', 'Probability', prob, [0, 1], 'any');
        this.add_property_slider('speed', 'Speed', speed, [0, 1], 'any');

        this.burning_count_chart = this.add_chart('ts', {
            'title': 'Burning Count',
            'xLabel': 't'
        });
        this.cell_stats_chart = this.add_chart('bar', {
            'title': 'Cell Stats',
            'yLabel': 'Count',
            'xLabel': 'State'
        });

        this.forest(size, prob);
        this.set_speed(speed);
    }

    reset()
    {
        this.forest(this.size, this.prob, false);
    }

    set_speed(speed)
    {
        this.speed = speed;
        this.set_timer_speed(1000 - speed * 1000);
    }

    burn()
    {
        const burning = new Set();
        const to_burn = new Set();
        const size = this.size;

        this.disable_updates();

        for (let i = 0; i < size; i++) {
            for (let j = 0; j < size; j++) {
                if (this.get_agent_state(i, j) === TreeState.BURNING) {
                    burning.add([i, j]);
                    for (const [neig_i, neig_j] of this.iterate_cell_neighbors(i, j)) {
                        if (this.get_agent_state(neig_i, neig_j) === TreeState.ALIVE) {
                            to_burn.add([neig_i, neig_j]);
                        }
                    }
                }
            }
        }

        for (const [i, j] of burning) {
            const steps = this.get_cell_attribute(i, j, 'steps');
            if (steps < this.burn_steps) {
                this.update_cell_state(i, j, {
                    steps: steps+1
                });
            }
            else {
                this.set_agent_state(i, j, TreeState.DEAD);
                this.dead_count += 1;
                this.burning_count -= 1;
            }
        }

        for (const [i, j] of to_burn) {
            this.set_agent_state(i, j, TreeState.BURNING);
            this.burning_count += 1;
            this.alive_count -= 1;
        }

        this.update_charts();

        this.enable_updates();
    }

    reset_charts()
    {
        this.alive_count = this.alive_orig_count;
        this.burning_count = 0;
        this.dead_count = 0;

        this.burning_count_chart.clear_datapoints();
        this.chart_steps = 0;

        this.cell_stats_chart.clear_datapoints();
        this.cell_stats_chart.update_config({
            'yLim': [0, this.alive_count]
        });
        this.cell_stats_chart.add_datapoint('Alive', this.alive_count);
        this.cell_stats_chart.add_datapoint('Burning', this.burning_count);
        this.cell_stats_chart.add_datapoint('Dead', this.dead_count);
    }

    update_charts()
    {
        this.burning_count_chart.add_datapoint((this.burning_count + this.dead_count) / this.alive_orig_count);

        this.cell_stats_chart.update_datapoints([
            ['Alive', this.alive_count],
            ['Burning', this.burning_count],
            ['Dead', this.dead_count]
        ]);
    }

    tick()
    {
        console.log('calling tick');
        this.burn();
    }
}
