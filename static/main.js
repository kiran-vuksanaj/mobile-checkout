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
    inventoryList = $('#inventory_list')
    addItemRow = $('#item-new')
    console.log(inventoryList)
    inventoryList.empty()
    for(const idx in data['items']) {
	item = data['items'][idx]
	console.log(item)
	inventoryList.append(
	    `<tr id="item-${item[0]}"><td>${item[1]}</td><td style="width:0px;" class="text-end"><button class="btn btn-danger delitem">X</button></td></tr>`)
    }
    inventoryList.append(addItemRow)
    $(".delitem").on('click',delitem)
    $("#additem").on('submit',additem)
}

function loadinventory(v_id) {
    args = {}
    if(v_id >= 0){
	args['v_id'] = v_id
    }
    $.getJSON('api/items', args, displayinventory)
}

loadinventory(-1)
console.log('complete')
