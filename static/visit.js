import * as bag from '/static/bag.js';

console.log('visit');

function configureVisit(e){
    e.preventDefault();
    // get location id
    const locField = $('#location')[0]
    const location_id = locField[ locField.selectedIndex ].id.split('-')[1];
    console.log(location_id);
    // get selected item ids

    const switches = $('#itemSwitches input').toArray();
    console.log(switches);
    const selectedItems = switches.
	  filter( checkbox => checkbox.checked ).
	  map( checkbox => checkbox.id.split('-')[1]);

    console.log(selectedItems);
    
    // send api request

    $.get('/api/set_availability',{
	"location": location_id,
	"items": JSON.stringify(selectedItems),
    },function(data){
	console.log(data);
	// change visible alert
	$('#initialMessage').css('display','none');
	$('#successLocationName')[0].textContent = data['names']['locations'][location_id];
	$('#itemCount')[0].textContent = data['count'];
	$('#successMessage').css('display','block');
	
    });
    
}

function resetPage(e) {
    e.preventDefault();
    $('#initialMessage').css('display','block');
    $('#successMessage').css('display','none');
    $('#itemSwitches input').prop('checked',false);
}


function newItem(e) {
    e.preventDefault();
    const name = $('#newitem input')[0].value;
    if(name.length > 0){
	$.get('/api/add_item',{'name':name}, function(data) {
	    if(data['success']){
		location.reload();
	    }
	});
    }
}

$('#submitConfig').on('click',configureVisit);
$('#location').on('change',resetPage);
$('#submitNewItem').on('click',newItem);
console.log('end');
