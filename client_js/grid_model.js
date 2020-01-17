class GridModel extends Model
{
    constructor()
    {
        super();
        this.rows = undefined;
        this.cols = undefined;
        this.grid = undefined;
    }

    clear()
    {
        this.rows = 0;
        this.cols = 0;
        this.grid = [];
        this.send('clear');
    }

    set_model_type()
    {
        super.set_model_type({
            type: 'grid'
        });
    }

    create_grid(rows, cols, initial_state)
    {
        if (initial_state === undefined) {
            initial_state = (row, col) => {
                return {};
            };
        }
        this.rows = rows;
        this.cols = cols;
        this.grid = [];
        for (let i = 0; i < cols; i++) {
            this.grid.push([]);
            for (let j = 0; j < rows; j++) {
                this.grid[i].push({
                    'row': j,
                    'col': i,
                    ...initial_state(j, i)
                });
            }
        }
        this.notify_full_state();
    }

    update_cell_state(row, col, kwargs)
    {
        for (let k in kwargs) {
            this.grid[col][row][k] = kwargs[k];
        }
    }

    to_dict()
    {
        /* this method is not necessary in JS, but we define it anyway 
           to avoid serialization of additional attributes in classes that inherit
           this one */
        return {
            'rows': this.rows,
            'cols': this.cols,
            'grid': this.grid
        };
    }

    serialize()
    {
        return JSON.stringify(this.to_dict());
    }

    notify_full_state()
    {
        this.send('update_full_state', {
            'state': this.to_dict()
        });
    }

    notify_cell_state(row, col, kwargs)
    {
        this.update_cell_state(row, col, kwargs);
        this.send('update_cell_state', {
            'row': row,
            'col': col,
            'state': kwargs
        });
    }

    iterate_cell_neighbors(row, col)
    {
        const _grid = this;
        return {
            [Symbol.iterator]() {
                let counter = 0;
                return {
                    next() {
                        let i, j;
                        do {
                            i = -1 + (counter % 3);
                            j = -1 + Math.floor(counter / 3);
                            counter++;
                        } while (counter <= 9 && ((i == 0 && j == 0) || !_grid.__pos_in_range(row+i, col+j)));
                        const value = [row+i, col+j];
                        //console.log(`value: ${value}`);
                        let done = counter > 9;
                        return {
                            'value': value,
                            'done': done
                        };
                    }
                }
            }
        };
    }

    get_size()
    {
        return [this.rows, this.cols];
    }

    get_cell(row, col)
    {
        if (this.__pos_in_range(row, col)) {
            return this.grid[col][row];
        }
    }

    get_cell_attribute(row, col, attr)
    {
        if (this.__pos_in_range(row, col)) {
            return this.grid[col][row][attr];
        }
    }

    __pos_in_range(row, col)
    {
        return 0 <= row && row < this.rows && 0 <= col && col < this.cols; 
    }

    get_agent_state(row, col)
    {
        return this.get_cell_attribute(row, col, 'color');
    }

    set_agent_state(row, col, state)
    {
        this.notify_cell_state(row, col, {
            'color': state
        });
    }
}
