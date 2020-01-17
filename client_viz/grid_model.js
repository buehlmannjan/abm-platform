class GridModel extends Model
{
    constructor(manager, config)
    {
        super(manager, config, 20, 20);
        this.type = 'grid';
    }

    agent_id(agent)
    {
        return {'row': agent.row, 'col': agent.col};
    }

    clear()
    {
        this.state.rows = 0;
        this.state.cols = 0;
        this.state.grid = [];
    }

    update_full_state(data)
    {
        // FIXME same as import_state, but data attributes are organized differently
        //console.log(`update_full_state: ${Object.keys(data)}`);
        this.state.rows = data.state.rows;
        this.state.cols = data.state.cols;
        this.state.grid = data.state.grid;
        this.reset_size(this.state.rows, this.state.cols);
    }

    update_cell_state(data)
    {
        Object.keys(data.state).forEach(key => {
            this.state.grid[data.col][data.row][key] = data.state[key];
            if (key === 'color') {
                this.update_cell_color(data);
            }
        });
    }

    enable_updates()
    {
        super.enable_updates();
    }

    import_state(data)
    {
        // FIXME same as import_full_state, but data attributes are organized differently
        this.state.rows = data.rows;
        this.state.cols = data.cols;
        this.state.grid = data.grid;
        this.reset_size(this.state.rows, this.state.cols);
    };

    reset_size(newrows, newcols)
    {
        const ctx = this.ctx;

        console.log(`reset_size: ${newrows} ${newcols}`);
        let size = [newrows, newcols];

        // FIXME hardcoded squared size
        this.grid_width = d3.min([this.width, this.height]);
        this.grid_height = this.grid_width;

        this.ctx.clearRect(0, 0, this.width-this.translationX, this.height-this.translationY);

        // save drawing params
        this.size = size;
        this.wcellsize = (this.grid_width-this.translationX) / size[0];
        this.hcellsize = (this.grid_height-this.translationY) / size[1];

        ctx.beginPath();
        ctx.strokeStyle = "#eee";
        d3.range(size[0]+1).forEach((d) => {
            ctx.moveTo(this.wcellsize*d, 0);
            ctx.lineTo(this.wcellsize*d, this.grid_height-this.translationY);
        });
        d3.range(size[1]+1).forEach((d) => {
            ctx.moveTo(0, this.hcellsize*d);
            ctx.lineTo(this.grid_width-this.translationX, this.hcellsize*d);
        });
        ctx.stroke();
        ctx.closePath();

        this.draw_grid();
        this.draw_hidden_canvas();
    }

    redraw()
    {
        // FIXME this is not clean, but it's required to redraw properly on window resize
        this.ctx.translate(this.translationX, this.translationY);
        this.hidden_ctx.translate(this.translationX, this.translationY);
        this.reset_size(this.size[0], this.size[1]);
    }

    draw_grid()
    {
        const ctx = this.ctx;

        ctx.strokeStyle = "white";

        for (let col of this.state.grid) {
            for (let d of col) {
                ctx.fillStyle = d.color;
                ctx.roundRect(
                    this.wcellsize*d.col+1,
                    this.hcellsize*d.row+1,
                    this.wcellsize-2,
                    this.hcellsize-2,
                    3, true, true);
            }
        }
    }

    draw_hidden_canvas()
    {
        const ctx = this.hidden_ctx;

        this.__reset_lookup_colors();
        ctx.strokeStyle = "white";

        ctx.clearRect(0, 0, this.width-20, this.height-20);

        // FIXME copy/paste from draw_grid
        for (let col of this.state.grid) {
            for (let d of col) {
                const color = this.__get_next_color();
                ctx.fillStyle = color;
                ctx.roundRect(
                    this.wcellsize*d.col+1,
                    this.hcellsize*d.row+1,
                    this.wcellsize-2,
                    this.hcellsize-2,
                    3, true, true);
                this.__color_to_agent[color] = d;
            }
        }
    }

    update_cell_color(data)
    {
        const ctx = this.ctx;
        //console.log(`update_cell_color: ${data.row} ${data.col} ${data.state.color}`);

        ctx.strokeStyle = "white";
        ctx.fillStyle = data.state.color;
        ctx.roundRect(
            this.wcellsize*data.col+1,
            this.hcellsize*data.row+1,
            this.wcellsize-2,
            this.hcellsize-2,
            3, true, true);
    }
}

// rounded rectangle syntactic sugar for canvas 2D context
// taken from http://js-bits.blogspot.com/2010/07/canvas-rounded-corner-rectangles.html
CanvasRenderingContext2D.prototype.roundRect = function(x, y, width, height, radius, fill, stroke)
{
    if (stroke === undefined) {
        stroke = true;
    }
    if (radius === undefined) {
        radius = 5;
    }
    this.beginPath();
    this.moveTo(x + radius, y);
    this.lineTo(x + width - radius, y);
    this.quadraticCurveTo(x + width, y, x + width, y + radius);
    this.lineTo(x + width, y + height - radius);
    this.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    this.lineTo(x + radius, y + height);
    this.quadraticCurveTo(x, y + height, x, y + height - radius);
    this.lineTo(x, y + radius);
    this.quadraticCurveTo(x, y, x + radius, y);
    this.closePath();
    if (stroke) {
        this.stroke();
    }
    if (fill) {
        this.fill();
    }        
}
