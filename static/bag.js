import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm"

console.log('bag')

var margin = {
    top: 30,
    right: 30,
    bottom: 70,
    left: 60},
    width = 460 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

var svg = d3.select('#bagGraph').
    append('svg').
    attr('width',width + margin.left + margin.right).
    attr('height',width + margin.top + margin.bottom).
    append('g').
    attr('transform',
	 'translate('+margin.left+','+margin.top+')');

const locationTitle = $('#locationTitle')[0];
const locField = $('#location')[0]

function changeGraphData(location) {
    locationTitle.textContent = locField.value;
    $.get('/api/bag', {'location':location}, buildGraph);
}

function buildGraph(data) {
    // console.log(data);
    var content = data['data']
    // console.log(content)

    // update title
    
    // reset graph contents
    
    svg.selectAll('*').remove();

    
    // x axis
    var x = d3.scaleBand().
	range([ 0, width ]).
	domain(content.map( function(entry) {return data['names']['items'][ entry[0] ]} )).
	padding(0.2);
    svg.append('g').
	attr('transform','translate(0,'+height+')').
	call(d3.axisBottom(x)).
	selectAll('text').
	attr('transform', 'translate(-10,0)rotate(-45)').
	style('text-anchor','end');

    // y axis
    var y = d3.scaleLinear().
	domain([0, 1.2*content.reduce( (a,b) => Math.max(a,b[1]), -Infinity) ]).
	range([height,0]);
    svg.append('g').
	call(d3.axisLeft(y));

    svg.selectAll('mybar').
	data(content).
	enter().
	append('rect').
	attr('x', function(d) { return x( data['names']['items'][ d[0] ] ) }).
	attr('y', function(d) {return y(d[1])}).
	attr('width', x.bandwidth()).
	attr('height', function(d) {return height - y(d[1])}).
	attr('fill','#69b3a2');
}

function selectedLocation(e) {
    return e.target[ e.target.selectedIndex ].id.split("-")[1];
}

$('#location').on('change', function(e) {
    changeGraphData( selectedLocation(e) );
});

changeGraphData( locField[ locField.selectedIndex ].id.split("-")[1] );

console.log('end');
