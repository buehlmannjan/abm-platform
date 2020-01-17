////

var canvas = document.querySelector("canvas"),
    context = canvas.getContext("2d"),
    width = canvas.width,
    height = canvas.height;

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function(d) { return d.id; }).strength(0.5))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2))
    .alphaDecay(0);

// initial graph: one node without connections
var graph = {
    "nodes": [{"id": 1, "weight": 0, "visited": true}],
    "links": []
}
var graphDict = {1: graph.nodes[0]};
var nodesWeighted = [1];
var newNode = 1; // ids of existing nodes
var m = 1;

var wait = 20/0.5;
var count = 0;
var size = 50;

function generate_barabasi(num) {
  function chooseTarget() {
    // choose a target for an incoming node
    var chosen = nodesWeighted[Math.floor((Math.random() * nodesWeighted.length))];
    return chosen;
  }
  function addNode() {
    newNode += 1;
    graph.nodes.push({"id": newNode, "weight": m, "visited": false}); // add new node
    graphDict[newNode] = graph.nodes[newNode];
    for (var k=0; k<m; k++) {
        var tgt = chooseTarget(newNode-1)
        graph.links.push({source: newNode, target: tgt}); // add new link
        nodesWeighted.push(newNode, tgt) // add nodes to weighted list because they each have one more link now
        graph.nodes[tgt-1].weight += 1
    }
  }
  for (var i = 1; i < num; i++) addNode();
}

function update_size(size) {
  d3.select("output[for=size]")._groups[0][0].innerText = size;
}

function update_speed(speed) {
  d3.select("output[for=speed]")._groups[0][0].innerText = parseFloat(speed).toFixed(2);
}

function register_handlers() {
  d3.select("input[id=size]")
    .on("input", change_size);

  d3.select("input[id=speed]")
    .on("input", change_speed);
}

function start_simulation() {
  simulation
    .nodes(graph.nodes)
    .on("tick", ticked);

  simulation.force("link")
    .links(graph.links);
}

function diffuse() {
  count++;
  if (count > wait) {
    count = 0;
    var visited = {};
    graph.nodes.forEach(n => {
      if (n.visited) visited[n.id] = true;
    });
    graph.links.forEach(l => {
      if (visited[l.source.id])
        l.target.visited = true;
      if (visited[l.target.id])
        l.source.visited = true;
    });
  }
}

function ticked() {
  context.clearRect(0, 0, width, height);

  context.beginPath();
  graph.links.forEach(drawLink);
  context.strokeStyle = "#aaa";
  context.stroke();

  // draw non-visited nodes
  context.beginPath();
  graph.nodes.forEach(n => {
    if (!n.visited)
      drawNode(n);
  });
  context.fill();
  context.strokeStyle = "#fff";
  context.stroke();

  // draw visited nodes
  context.beginPath();
  graph.nodes.forEach(n => {
    if (n.visited) {
      //console.log("drawing visited node");
      drawNode(n);
    }
  });
  context.fill();
  context.strokeStyle = "blue";
  context.stroke();

  diffuse();
}

function change_size() {
  graph = { "nodes": [{"id": 1, "weight": 0, "visited": true}],
    "links": []
  }
  graphDict = {1: graph.nodes[0]};
  nodesWeighted = [1];
  newNode = 1; // ids of existing nodes
  size = this.value;

  generate_barabasi(size);
  update_size(size);
  
  simulation
    .nodes(graph.nodes)
    .on("tick", ticked);

  simulation.force("link")
    .links(graph.links);

  simulation.alpha(1).restart();
}

function change_speed() {
  wait = 20/this.value;
  update_speed(this.value);
}

function drawLink(d) {
  context.moveTo(d.source.x, d.source.y);
  context.lineTo(d.target.x, d.target.y);
}

function drawNode(d) {
  context.moveTo(d.x + 3, d.y);
  context.arc(d.x, d.y, 3, 0, 2 * Math.PI);
}

generate_barabasi(size);
register_handlers();
start_simulation();
