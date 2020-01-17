import model
import json

class GridModel(model.Model):
    """Defines a model in which each agent is a cell on a 2-D grid"""
    def __init__(self):
        self.rows = None
        self.cols = None
        self.grid = None
        super().__init__()

    def clear(self):
        """Clears grid state and structure."""
        self.rows = 0
        self.cols = 0
        self.grid = []
        self.send('clear')

    def set_model_type(self):
        super().set_model_type(type='grid')

    def create_grid(self, rows, cols, initial_state=None):
        """Creates initial grid sized (rows, cols) with initial state given
        by initial_state callback
            * rows: number of rows
            * cols: number of columns
            * initial_state: function that receives parameters row, col and
                returns a new dictionary for the cell

            Cell state includes keys 'row' and 'col' with cell position.
        """
        if initial_state is None:
            initial_state = lambda row, col: {}
        self.rows = rows
        self.cols = cols
        self.grid = [
                [{'row': row, 'col': col, **initial_state(row, col)}
                    for row in range(rows)] for col in range(cols)]
        self.notify_full_state()

    def update_cell_state(self, row, col, **kwargs):
        """Update (row, col) cell state to kwargs"""
        self.grid[col][row].update(kwargs)

    def to_dict(self):
        """Return ready-for-serialization grid"""
        return {
            'rows': self.rows,
            'cols': self.cols,
            'grid': self.grid
        }

    def serialize(self):
        """Serialize to JSON"""
        return json.dumps(self.to_dict())

    def __str__(self):
        return self.serialize()

    def notify_full_state(self):
        """Notify the full state of the model"""
        self.send('update_full_state', state=self.to_dict())

    def notify_cell_state(self, row, col, **kwargs):
        """Update (row, col) cell state to kwargs and notify server"""
        self.update_cell_state(row, col, **kwargs)
        self.send('update_cell_state', row=row, col=col, state=kwargs)

    #def iterate_cell_neighbors_8(self, row, col):
    #    """Returns iterator to 8 neighboring cell positions around (row, col) if in range"""
    #    for i in range(-1, 2):
    #        for j in range(-1, 2):
    #            if (i != 0 or j != 0) and self.__pos_in_range(row+i, col+j):
    #                yield (row+i, col+j)

    def iterate_cell_neighbors(self, row, col):
        """Returns iterator to 4 neighboring cell positions around (row, col) if in range"""
        if self.__pos_in_range(row-1, col):
            yield row-1, col
        if self.__pos_in_range(row, col-1):
            yield row, col-1
        if self.__pos_in_range(row+1, col):
            yield row+1, col
        if self.__pos_in_range(row, col+1):
            yield row, col+1

    def get_cell_neighbors(self, row, col):
        """Returns a list with all the neigbors of (row, col) in iterator order.
        See iterate_cell_neighbors(self, row, col)"""
        return list(self.iterate_cell_neighbors(row, col))

    def iterate_cell_neighbors_pbc(self, row, col):
        """Returns iterator to 4 neighboring cell positions around (row, col) at boundary with PBC"""
        for (i,j) in [(-1,0), (0,-1), (1,0), (0,1)]:
             yield ((row+i) % self.rows, (col+j) % self.cols)

    def get_cell_neighbors_pbc(self, row, col):
        """Returns a list with all the neighbors of (row, col) in iterator order, with PBC"""
        return list(self.iterate_cell_neighbors_pbc(row, col))

    def get_size(self):
        """Returns a tuple (rows, columns) which represent the size of the grid"""
        return (self.rows, self.cols)

    def get_cell(self, row, col):
        """Returns cell dictionary for agent at (row, col) if in range"""
        if self.__pos_in_range(row, col):
            return self.grid[col][row]

    def get_cell_attribute(self, row, col, attr):
        """Returns attribute attr from cell at (row, col)"""
        return self.grid[col][row][attr]

    def __pos_in_range(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get_agent_state(self, row, col):
        """Returns agent state of cell at (row, col)."""
        return self.get_cell_attribute(row, col, 'color')

    def set_agent_state(self, row, col, state):
        """Sets agent state of cell at (row, col).
        Override this method to compose more complex states"""
        self.notify_cell_state(row, col, color=state)
