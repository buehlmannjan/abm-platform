Agent Based Models Visualization Platform
=========================================

This short document describes the *abm-platform* and how to use it.

Architecture
============

The *abm-platform* consists of three components:

1. NodeJS server
2. Visualization client
3. Model client

Both clients will connect to the NodeJS server using WebSockets.
The server keeps track of the model data and forwards state updates to the clients.
The visualization client shows the current model state and allows the user to change model parameters from the web interface.
The model client defines the actual model, what parameters can be modified from the web interface and how the state is updated.

How to Install
==============

Both clients are executed locally after the server is brought up.

The NodeJS server can be executed locally using `node server/main.js` or inside of a Docker container.

The Docker image is generated using the `build_server` command on the `docker` folder.
It can be brought up using the `start_server` command on the same folder.

After the server is running, both clients can be executed in any order.

Running the Visualization Client
================================

The visualization client is an HTML5 + ECMAScript6 application that can be executed on any modern browser.
It leverages D3 for visualization.

The client resides in the `index.html` file that can be found in the project root folder.
Opening it up in the browser will result in the application connecting to the NodeJS server.
If a model client is already running, it will retrieve the model information and start showing it.
Otherwise, it will do nothing and wait for a model to connect.

The client window is split in three sections, from left to right:
1. Model properties, settings and status information.
2. The model itself.
3. Any associated charts.

The status section at the bottom left shows whether the client has connected successfully to the server and the name of the model, if any.

Running the Model Client
========================

Model clients can be defined in any supported language.
They implement a WebSockets interface with the NodeJS server.
For now, the supported languages are Python (version 3) and ES6 JavaScript (grid models only).

Example models are located under `models` in the `client_python` folder.
The launcher, a script called `abm_platform.py`, may be used to launch any model that is defined under `models`.
This is achieved by executing the script as follows:

`./abm_platform.py model_name`

Where `model_name` is the module name in which the desired model is located (usually corresponds to the name of the Python script, without the `.py` extension).
This module *must* define a class that inherits from `Model` and provide a constructor with no arguments.

Model Interface
===============

The `Model` base class defines the basic connection handling code, as well as state update, timer configuration, and model properties handling.

Three types of models that inherit from the `Model` class are already defined:

1. Grid Models (`GridModel` class)
2. Graph Models (`GraphModel` class)
3. Fixed Layout Graph Models (`FixedGraphModel` class)

These model types implement protocols that are supported by the both the server and the visualization client.
Each type defines which data it should store, as well as the interface the model implementation will use to change its state.

This framework is extensible, but in order to support additional model types, an implementation of the new protocol is required in all three components.

However, existing types may be used to define custom models where appropriate.

## Base Models

1. `create()`: this method is invoked by the Model Client at startup.

2. `tick()`: this method is invoked from the Model Client timer at each time step.
   See `get_timer_speed` and `set_timer_speed`.

3. `set_model_type()`: sends the model type to the server.

4. `handle_property_change(prop, value)`: this method is invoked when the user changes the value of property `prop` to `value`.

5. `handle_agent_clicked(data)`: this method is invoked when the user clicks on an agent.
	Dictionary `data` describes which agent was clicked.

6. `reset()`: resets the state of the model to the starting point of the simulation.

7. `stop_condition()`: returns `True` if the simulation has finished, `False` otherwise.
	This method is used to automatically stop a running simulation based on a condition of the model.

8. `add_property_slider(id, name, value, range, step)`: defines a slider property for the model with ID `id`.
   - `name`: the property name that will be shown to the user.
   - `value`: initial value.
   - `range`: a two-element list which defines the minimum and maximum value of the property.
   - `step`: step between consecutive values, `any` defines that any precision that can be represented is allowed.

   This will result in the visualization client showing a slider using the specified settings.
   An input change event will invoke `handle_property_change` with the new value.

9. `add_property(id, name, value, range, step)`: alias for `add_property_slider`.

10. `add_property_checkbox(id, name, value)`: defines a checkbox property for the model with ID `id`.
   - `name`: the property name that will be shown to the user.
   - `value`: initial value.

   This will result in the visualization client showing a checkbox using the specified settings.
   An input change event will invoke `handle_property_change` with the new value.

11. `add_property_selectbox(id, name, current, values)`: defines a selection box property for the model with ID `id`.
   - `name`: the property name that will be shown to the user.
   - `current`: initial value.
   - `values`: list of all possible values.

   This will result in the visualization client showing a selection box using the specified settings.
   An input change event will invoke `handle_property_change` with the new value.

12. `send(d)`: sends dictionary `d` as a JSON-encoded message.

13. `send_raw(data)`: sends raw (non-encoded) `data`. Used internally by `send(d)`.

14. `create_base()`: initializes the base model.
   Invokes `set_model_type`.

15. `set_timer_speed(delay)`: defines the timer delay `delay` at which each time step occurs.

16. `get_timer_speed()`: gets the current timer delay.

17. `add_chart(cls, ...)`: creats a new chart of class `cls` which is associated with the current model.
	If `cls` is a string, the class name is defined using the following key:
	- `bar`: `BarChart` class.
	- `ts`: `TSChart` class.
	- `line`: `LineChart` class.

	Additional parameters define chart properties (as a dictionary) which are sent to the class constructor.

18. `disable_updates()`: disables sending updates to the server, queueing successive messages locally.

19. `enable_updates()`: enables sending updates the server, resulting in queued messages to be sent as a single bulk message.

## Grid Models

A grid model defines a squared grid of size *n* rows times *m* columns, in which each cell may have different properties.

The public interface is as follows:

1. `create_grid(rows, cols, initial_state=f)`: defines a new grid sized `rows`*x*`cols` in which the initial state of each cell is defined by calling function `f(i, j)`, where `i` and `j` are row and column number respectively.

2. `update_cell_state(i, j, ...)`: updates cell state in position row `i`, column `j`.
   Additional parameters define cell properties (as a dictionary).

3. `notify_full_state()`: notifies the server (and additional clients) the full state of the grid.

4. `notify_cell_state(i, j)`: notifies the server (and additional clients) the state of a single cell in position row `i`, column `j`.

5. `iterate_cell_neighbors(i, j)`: returns an iterator to all neighboring cells of row `i`, column `j`.
It is considered that vertical, horizontal and diagonal adjacent cells are neighbors.

6. `get_size()`: returns a tuple with the number of rows and columns of the grid.

7. `get_cell(i, j)`: returns a dictionary with the properties of the cell at row `i`, column `j`.

8. `get_cell_attribute(i, j, prop)`: returns the value of property `prop` of the cell at row `i`, column `j`.

9. `get_agent_state(i, j)`: returns a state representation for the cell at row `i`, column `j`.
	By default, it returns the `color` property of the cell.
	This representation may be overridden to define any type of state abstractions.

10. `set_agent_state(i, j, value)`: sets the state for the cell at row `i`, column `j` to `value`.
	By default, it sets the `color` property of the cell.
	This representation may be overridden to define any type of state abstractions.

## Graph Models

A graph model defines a graph using adjacency lists.
It allows nodes with properties and edges to be defined, implementing the following public interface:

1. `add_node(nodeid, color='black', ...)`: adds a node to the current graph with ID `nodeid`.
Additional parameters define node attributes (as a dictionary).
By default, a color attribute is defined with value *black*.

2. `add_edge(node0, node1)`: adds an edge connecting nodes `node0` and `node1`.

3. `get_node_prop(nodeid, prop)`: returns the local copy of property `prop` from node `nodeid`.

4. `update_node_props(nodeid, ...)`: updates node properties from node `nodeid`.
Additional parameters define which attributes are to be modified and their respective values (as a dictionary).

5. `get_node_neighbors(nodeid)`: returns a list of the nodes that are connected to `nodeid`.

6. `node_iterator()`: returns an iterator to every node in the graph.

7. `get_agent_state(nodeid)`: returns a state representation for the node `nodeid`.
	By default, it returns the `color` property of the node.
	This representation may be overridden to define any type of state abstractions.

8. `set_agent_state(nodeid, value)`: sets the state for the node `nodeid` to `value`.
	By default, it sets the `color` property of the node.
	This representation may be overridden to define any type of state abstractions.

## Fixed Layout Graph Models

This model class inherits from `GraphModel`, allowing graphs with fixed node positions to be defined.

It defines the following additional methods:

1. `load_json(f)`: loads a graph from JSON dictionary `f`.
	The `f` variable may be a string (filename or JSON string) or a file-like object.

	The JSON dictionary should define the following keys:

	- `nodes`: list of nodes with attribute `id` as node identifier.
	- `edges`: list of edges with attributes `source` and `target` identifying the IDs of both ends.

2. `viewport()`: returns a four-element list which specifies the boundary box of the viewport.
	This method is evaluated and the information is sent to the server when the model is created.
	The actual positions of the nodes as they will be shown in the visualization client are calculated by applying a linear transform that maps positions within the boundary box to the screen canvas.

	Its four elements represent:
	- Upper-left `x` coordinate.
	- Upper-left `y` coordinate.
	- Lower-right `x` coordinate.
	- Lower-right `y` coordinate.

Node positions are defined using the `x` and `y` properties of the node.
If those attributes are not defined, the positions will be calculated using the standard forces method.

Defining Custom Models
======================

In order to define a custom model, the user inherits from one of the supported model types: `GraphModel` or `GridModel`.

Then, the following methods must be defined:

1. `handle_property_change`
2. `create`
3. `tick`
4. `reset`

The following example shows a simple graph model that defines a graph with two nodes connected using a single link:
The model defines a single property that defines the update speed.
The color for node `n0` is changed at each time step to either black or blue.

```python
class SimpleGraphModel(GraphModel):
    def handle_property_change(self, prop, value):
        if prop == 'speed':
            self.set_timer_speed(value * 1000) # speed in ms
    def create(self):
        self.add_property('speed', 'Speed', 0.1, [0,1], 'any')
        # define graph
        self.add_node('n0')
        self.add_node('n1')
        self.add_edge('n0', 'n1')
    def tick(self):
        # cycle n0 color
        if self.get_agent_state('n0') == 'black':
            self.set_agent_state('n0', 'blue')
        else:
            self.set_agent_state('n0', 'black')
    def reset(self):
        pass
```

CSS Theme Guide
================

All the visual aspects of the ABM platform are steered from within two files: index.html and input.css.

### The index.html file:

In here as first all the root variables are defined.

#### :root {
            --urrp_blue: #02019A; /* this is the URRP blue which is used in the title */
            --urrp_cyan: #02B0DB; /* this is the URRP cyan which is used in the left sidebar */
            --fontsize_lbar: 17px; /* this is the font size which is defined for all elements of the left bar */
            --fontweight_lbar: normal; /* this is the regular font weight for the left bar */
            --fontstyle_lbar: normal;
            --fontcolor_lbar: #585858;
            --fontfamily_title: 'Roboto'; /* this is the defined font-family for the title bar */
            --fontfamily_sidebars: 'Lato'; /* this is the defined font-family for the two sidebars*/

If you want to change the font, font-size or the colors of the left or top bar then simply change the value in the variable. 

Lastly, there are three styled objects defined in the html code within the index.html file: The "Agent Based Modelling Platform" title, the "Control Parameters" title in the left sidebar and the "Charts" title in the right sidebar. If you want to change these, then simply scroll to the end of the index.html file and adjust the properties within the html code.

#### .sidebar_l & .sidebar_r

Here all properties for the left and right sidebar are defined.


#### .settings/.setting_value/.checkbox_container/ .selectbox_container

Here all the properties of the settings within the left sidebar are defined. 


#### button

Here all the properties of the Play and Reset button are to be found. 

#### .charts_container & .chart

Here the properties of the charts in the right sidebar can be defined. 


### The input.css file:

The input.css file is divided into three sections: "Sliders", "Checkboxes and radio buttons"  & "select boxes"

#### Sliders

To modify the sliders visually two sections are important: 

input[type=range]::-webkit-slider-runnable-track

This property defines the visual aspects of the slider track. 

input[type=range]::-webkit-slider-thumb

This property defines the visual aspects of the slder thumb. 

These two sections are repeated for all the browsers (-webkit for Safari & Chrome, -moz for Firefox and -ms for Internet Explorer)

#### Checkboxes and radio buttons

Within this section the visual properties of the checkboxes and radio buttons are defined for all their different states (checked, disabled, hover).

#### Select Boxes

This section defines the properties of the select boxes. 

.select select / .select select:hover / .select select:disabled

Here all visual aspects are defined for all the different states. 