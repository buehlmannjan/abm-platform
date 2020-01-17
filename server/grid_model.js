const Model = require("./model");

class GridModel extends Model
{
    constructor(config)
    {
        super(config);
        this.type = 'grid';

        this.clear();
    }

    clear()
    {
        this.model_state.rows = 0;
        this.model_state.cols = 0;
        this.model_state.grid = [];
    }

    update_full_state(data)
    {
        this.model_state.rows = data.state.rows;
        this.model_state.cols = data.state.cols;
        this.model_state.grid = data.state.grid;
        //console.log(data.state.grid[0][0]);
    }

    update_cell_state(data)
    {
        Object.keys(data.state).forEach(key =>
            this.model_state.grid[data.col][data.row][key] = data.state[key]
        );
    }
}

module.exports = GridModel;
