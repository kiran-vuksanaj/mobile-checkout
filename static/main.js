import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm"
console.log("connected!")


function additem(e) {
    e.preventDefault()
    $.get('api/add_item',{'name':e.target.elements.name.value}, function() {
	loadinventory(-1);
    })
    console.log(e)
}

function delitem(e) {
    e.preventDefault()
    idstring = e.target.parentElement.parentElement.id
    $.get('api/del_item',{'i_id':idstring.substring(idstring.search('-')+1,idstring.length)}, function() {
	loadinventory(-1);
    })
}

function displayinventory(data) {
    console.log(data)
    const inventoryList = $('#inventory_list')
    const addItemRow = $('#item-new')
    console.log(inventoryList)
    inventoryList.empty()
    for(const idx in data['items']) {
	const item = data['items'][idx]
	console.log(item)
	inventoryList.append(
	    `<tr id="item-${item[0]}"><td>${item[1]}</td><td style="width:0px;" class="text-end"><button class="btn btn-danger delitem">X</button></td></tr>`)
    }
    inventoryList.append(addItemRow)
    $(".delitem").on('click',delitem)
    $("#additem").on('submit',additem)
}

function loadinventory(v_id) {
    let args = {}
    if(v_id >= 0){
	args['v_id'] = v_id
    }
    $.getJSON('api/items', args, displayinventory)
}


function getGraphData() {
    $.getJSON('api/qty',function(reply) {
	console.log(reply);
	// set the dimensions and margins of the graph
	var margin = {top: 10, right: 30, bottom: 30, left: 60},
	    width = 460 - margin.left - margin.right,
	    height = 400 - margin.top - margin.bottom;

	var svg = d3.select('#d3-box').append("svg")
	    .attr('width', width+margin.left+margin.right)
	    .attr('height', height + margin.top + margin.bottom)
	    .append('g')
	    .attr('transform',
		  'translate('+ margin.left + ',' + margin.top + ')');

	var data = reply['data'].map( function(d) { return { date: d3.timeParse('%Y-%m-%d')(d[0]), value: d[1] } } );
	console.log(data)

	// X axis
	var x = d3.scaleTime()
	    .domain( d3.extent(data, function(d) {return d.date} ))
	    .range([ 0, width ]);
	svg.append('g')
	    .attr('transform', 'translate(0,' + height + ')')
	    .call(d3.axisBottom(x));

	// Y axis
	var y = d3.scaleLinear()
	    .domain([0, d3.max(data, function(d) {return d.value})])
	    .range( [height, 0] );
	svg.append('g')
	    .call(d3.axisLeft(y));

	svg.append('path')
	    .datum(data)
	    .attr('fill','none')
	    .attr('stroke','steelblue')
	    .attr('stroke-width',1.5)
	    .attr('d', d3.line()
		  .x( function(d) { return x(d.date) })
		  .y( function(d) { return y(d.value) })
		 );
    })
}
getGraphData()

// Append the SVG element.
console.log(svg.node())
console.log(d3Container)
d3Container.append(svg.node());



loadinventory(-1)
console.log('complete')

