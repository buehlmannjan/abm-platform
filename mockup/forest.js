////

/*var canvas = document.querySelector("canvas"),
    context = canvas.getContext("2d"),
    width = canvas.width,
    height = canvas.height;
*/

var w=50*10+20;
var h=50*10+20;
var size = 50;
var wcellsize;
var hcellsize;
var probability = 0.5;
var speed = 0.5;
var steps = 20;

var svg;

var grid,running=false,timer;

var liveC="#00c000";
var burningC="#c00000";
var deadC="#000000";

function resetSize(newsize) {
  var oldsvg = d3.select("#chart")
    .select("svg");
  
  if (oldsvg)
    oldsvg.remove();

  svg = d3.select("#chart")
    .append("svg")
    .attr('width', w)
    .attr('height', h)
    .append("g")
    .attr("transform","translate(20,20)");

  size = newsize;
  wcellsize = (w-20) / size;
  hcellsize = (h-20) / size;

  svg.selectAll(".gridv")
    .data(d3.range(size+1))
    .enter()
    .append("path")
    .attr("d",function(d) {
      return "M"+(wcellsize*d)+",0 v "+(h-20)
    })
    .style("stroke","#eee");
  svg.selectAll(".gridv")
    .data(d3.range(size+1))
    .enter()
    .append("path")
    .attr("d",function(d) {
      return "M0,"+(hcellsize*d)+" h "+(w-20)
    })
    .style("stroke","#eee");

  generate_grid(probability);

  svg.selectAll(".col").data(grid).enter()
    .append("g").classed("col",1)
    .attr("transform",function(d,i) {
      return "translate("+hcellsize*i+",0)";
    })
    .selectAll(".cells")
    .data(function(d) {return d;})
    .enter()
    .append("rect")
    .classed("cells",1);
  drawGrid();
}

function generate_grid(prob) {
  reset();
  grid=d3.range(size).map(function(i) {
    return d3.range(size).map(function(j) {
      return {value:Math.random()<prob?1:0,row:j,col:i,steps:0};
    })
  });  
}

function update_size(size) {
  d3.select("output[for=size]")._groups[0][0].innerText = size;
}

function update_probability(prob) {
  d3.select("output[for=probability]")._groups[0][0].innerText = parseFloat(prob).toFixed(2);
}

function update_speed(speed) {
  d3.select("output[for=speed]")._groups[0][0].innerText = parseFloat(speed).toFixed(2);
}

function register_handlers() {
  d3.select("input[id=size]")
    .on("input", change_size);

  d3.select("input[id=probability]")
    .on("input", change_probability);

  d3.select("input[id=speed]")
    .on("input", change_speed);
}

function change_size() {
  resetSize(this.value);
  update_size(this.value);
  set_on_fire();
  run();
}

function change_probability() {
  stop();
  probability = this.value;
  generate_grid(probability)
  drawGrid();
  update_probability(probability);
  set_on_fire();
  run();
}

function change_speed() {
  speed = this.value;
  stop();
  update_speed(speed);
  run();
}

function stop() {
  clearInterval(timer);
  timer=undefined;
  running=0;
  /*d3.select("#launch")
    .property("value","launch model")
    .on("click",run);*/
}

function reset() {
  stop();
  grid = d3.range(size).map(function(i) {
    return d3.range(size).map(function(j) {
      return {value:0,row:j,col:i,steps:0};
    })
  });
}

function run() {
  console.log("update speed", 1000-1000*speed);    
  timer = setInterval(update, 1000-1000*speed);
  running = 1;
  /*d3.select("#launch")
    .property("value","stop")
    .on("click",stop);*/
}

function drawGrid() {
  svg.selectAll(".col")
    .data(grid)
    .selectAll(".cells")
    .data(function(d) {
      return d;
    })
    .attr("y",function(d) {
      return hcellsize*d.row+1;
    })
    .attr("x", 1)
    .attr("width", wcellsize-2)
    .attr("height", hcellsize-2)
    .attr("rx", 3)
    .attr("ry", 3)
    .style("stroke", "white")
    .style("fill", function(d) {
      switch (d.value) {
        case 0: return "white";
        case 1: return liveC;
        case 2: return burningC;
        default: return deadC;
      }
    })
    .attr("id",function(d) {return "C"+d.row+"-"+d.col;})
    .on("click", function(d) {
      if(running){
        stop();
      }
      var live=d.value=1-d.value;
      d3.select(this)
        .transition()
        .style("fill",live?liveC:"white");
    })
}

function neighbors(i,j) {
  var n=[];
  if (i) {
    if (j) {
      n.push(grid[i-1][j-1]);
    }
    n.push(grid[i-1][j]);
    if (j < size-1){
      n.push(grid[i-1][j+1]);
    }
  }
  if (j) {
    n.push(grid[i][j-1]);
  }
  if (j < size-1) {
    n.push(grid[i][j+1]);
  }
  if (i < size-1) {
    if (j) {
      n.push(grid[i+1][j-1]);
    }
    n.push(grid[i+1][j]);
    if (j < size-1) {
      n.push(grid[i+1][j+1]);
    }
  }
  return n;
}

function evolve() {
  console.log("evolve");
  var total = 0;
  var newgrid = d3.range(size).map(function(i) {
    return d3.range(size).map(function(j) {
      return grid[i][j].value;
    })
  });

  d3.range(size).forEach(function(i) {
    d3.range(size).forEach(function(j) {

      n = neighbors(i,j);
      if (grid[i][j].value == 2) {
        if (grid[i][j].steps < steps) {
          //console.log(i, j, grid[i][j].value);
          n.forEach(function(neigh) {
            if (neigh.value == 1) {
              newgrid[neigh.col][neigh.row] = 2;
            }
          });
          grid[i][j].steps++;
          total++;
        } else
        newgrid[i][j] = 3;
      } 
    })
  })

  d3.range(size).forEach(function(i) {
    d3.range(size).forEach(function(j) {
      if(grid[i][j].value!=newgrid[i][j]) {
        total=total+1;
        grid[i][j].value=newgrid[i][j];	
      }
    })
  });
  if(!total) { // no cell has changed in this turn 
    stop();
  }
}

function die(cell) {
  var d=cell.datum()
  cell.transition()
    .duration(1000)
    .attr({"height":0,y:d.row*hcellsize+(hcellsize-2)})
    .style("fill","black")
    .each("end",function() {
      d3.select(this).style("fill","white");
    });
}

function rise(cell) {
  var d=cell.datum();
  svg.append("circle").attr({cx:20*(d.col+.5),cy:20*(d.row+.5),r:0}).style({"fill":"none","stroke":"gold"}).transition().duration(1000)
    .attr("r",300)
    .style("stroke-opacity",0)
    .each("end",function() {d3.select(this).remove();})
  cell.attr({x:10,y:10+d.row*20,height:0,width:0}).style("fill",liveC).transition().delay(500).ease("elastic").attr({x:1,y:1+d.row*20,height:18,width:18})
}

function update() {
  drawGrid();
  evolve();
}

function set_on_fire() {
  if (grid[0][0].value == 1) {
    grid[0][0].value = 2;
    return;
  }
  if (grid[0][size-1].value == 1) {
    grid[0][size-1].value = 2;
    return;
  }
  if (grid[size-1][0].value == 1) {
    grid[size-1][0].value = 2;
    return;
  }
  if (grid[size-1][size-1].value == 1) {
    grid[size-1][size-1].value = 2;
    return;
  }
}

resetSize(size);
register_handlers();
set_on_fire();
run();
