/*
* PyChattr JavaScript Client Library 
* [c] Copyright 2014 Chaoyi Zha and DogeBoosting
* </>ed w/ <3 in Philly in '14
* Authors: Chaoyi Zha <summermontreal@gmail.com>
* Dependencies: socket.io, jQuery 1.x, jQuery UI, stringjs
*/

var domain = 'localhost';
var port = 5000;
var skip, pmdiv, token, pms, rli, sessuser;
pms = {}, rli = {};

function applog (item) {
	var d = new Date();
	$('#log').append('['+d+'] '+item);
}
function temit(event, message) {
	socket.emit(event, {"data": message, "token": token});	
}
function tsend(message) {
	socket.send({"data": message, "token": token});	
}


$(document).ready(function() {
	$( "#tabs" ).tabs();
	$('#reconnect').hide();
    var socket = io.connect('http://' + domain + ':' + port + '/pychattr', {reconnect: false});
    socket.on('auth', function(msg) {
        applog('<p>Received: ' + msg + '</p>');
        token = "";
        try {
			if (predtok.length > 5) {
				// if predefined token, e.g DogeBoosting
				socket.emit('auth', predtok);
				$('#toksub').hide();
			}
		}
		catch(err) {
			console.log(err);
			applog("<p style='color:green'>Enter your token details below to continue. </p>");
		
		}
        
		
    });
    $('#toksub').click(function () {
		token = $('#token').val();
		socket.emit('auth', token);
		$('#tokform').hide();
	});
    socket.on('message', function(msg) {
		var iswelcome = S(msg).between('Welcome, ', '. You are connected.').s
        if(iswelcome.length>0) {
			sessuser = iswelcome;
			$('#sessuser').html(sessuser);
						
		}
		var isjoin = S(msg).between('', 'has come online.').s
        if(isjoin.length>0) {
			applog('<p style="color:blue">'+msg+"</p>");
			skip = true;
						
		}
		var isleave = S(msg).between('', 'has disconnected').s
        if(isleave.length>0) {
			applog('<p style="color:blue">'+msg+"</p>");
			skip = true;
						
		}
		
        var isjson = S(msg).between('{', '}').s
        if(isjson.length>1) {
			console.log('incoming JSON: '+msg);
			
			var json = JSON.parse(msg);
			if (json.tojoin != undefined && json.joined != undefined) {
				applog('<p>PM Request from ' + json.joined + ' to '+ json.tojoin +'</p>');
				if (json.tojoin == sessuser) {
					var d = new Date();
					console.log('Received PM');
					pms[json.joined] = "PM:"+json.joined+"+"+json.tojoin;
					socket.emit('jroom', pms[json.joined]);
					applog('<p>You were PMed by '+json.joined+'.</p>');
					pmdiv = "<h3>PM with "+json.joined+"</h3>\
							<div class='well' id='PM_"+json.joined+"_"+json.tojoin+"' style='color:black'>\
								<p>["+d+"] <b>"+json.joined+": </b>Opened PM</p>\
							</div>\
							<br /><form id='form-#{tid}k'><input type='text' style='width:70%;display:inline' class='form-control' id='input-#{tid}'/><input type='submit' style='width:20%;display:inline' id='submit-#{tid}' class='form-control'/></form>";
					addTab(json.joined, pmdiv, pms[json.joined]);
				}
				else if (json.joined == sessuser) {
					var d = new Date();
					console.log('sent PM');
					pms[json.tojoin] = "PM:"+json.joined+"+"+json.tojoin;
					applog('<p>You PMed '+json.tojoin+'.</p>');
					pmdiv = "<h3>PM with "+json.tojoin+"</h3>\
							<div class='well' id='PM_"+json.joined+"_"+json.tojoin+"' style='color:black'>\
								<p>["+d+"] <b>"+json.joined+": </b>Opened PM</p>\
							</div>\
							<br /><form id='form-#{tid}k'><input type='text' style='width:70%;display:inline' class='form-control' id='input-#{tid}'/><input type='submit' style='width:20%;display:inline' id='submit-#{tid}' class='form-control'/></form>";
					addTab(json.tojoin, pmdiv, pms[json.tojoin]);
				}
			} // close isnewpm
			else if (json.room != undefined && json.text != undefined && json.from != undefined) {
				// if incoming communication
				console.log('Incoming!');
				var recvroom_fa = json.room.replace(":", "_");
				var recvroom = recvroom_fa.replace("+", "_");
				$('#'+recvroom).append('<p><b>'+json.from+'</b>: '+json.text+"</p>"); // add to corresponding well
			}
			else {
				applog('<p>Invalid JSON received: '+msg+"</p>");
			}
    } // close isjson
		else {
			if (skip==false) {
				applog('<p>Received: ' + msg + '</p>');
			}
			else {
				skip = false;
			}
		 } // close notjson
			
    }); // close onmsg
    
    $("body").on('submit', 'form', function() {
	  var tid = S(String(this.id)).between('form-', 'k').s;
	  var text = $('#input-'+tid).val();
	  var tjson = '{"room": "'+rli[tid]+'", "text": "'+text+'"}';
	  socket.emit('sendmsg', tjson);
	  console.log('emitted sendmsg');
	  $('#input-'+tid).val("");
	  return false;
	});
    
    socket.on('skick', function(msg) {
        applog('<p>Kicked from server: '+msg+'</p>');
        socket.disconnect();
        console.log('kicked');
        $('#reconnect').show();
    });
    socket.on('disconnect', function() {
		applog('<p style="color:red">Lost connection to server</p>');
	});
     socket.on('error', function(msg) {
        applog('<p style="color:red">Error: '+msg+'</p>');
        if (msg=="You are not logged in!") {
			$('#tokform').show();
		}
    });
    $('#pm').click(function () {
		var topm = window.prompt('Who would you like to PM');
		socket.emit('pmuser', topm);
		console.log('PMing '+topm);
	});
	$('#disconnect').click(function () {
		socket.disconnect();
		applog('<p>Client Disconnected</p>');
		$('#reconnect').show();
	});
	$('#reconnect').click(function () {
		socket.socket.connect()
		applog('<p>Client Reconnecting...</p>');
		$('#reconnect').hide();
		$('#tokform').show();
	});
	
	
	function qroom(room) {
		socket.emit('qroom', room);
	}
	
	// TABBING
    var tabTitle = $( "#tab_title" ),
      tabContent = $( "#tab_content" ),
      tabTemplate = "<li><a href='#{href}'>#{label}</a> <span class='ui-icon ui-icon-close' role='presentation'>Remove Tab</span></li>",
      tabCounter = 2;
    var tabs = $( "#tabs" ).tabs(); 
    // actual addTab function: adds new tab using the input from the form above
    function addTab(tabTitle, tabContent, room) {
      var label = tabTitle || "Tab " + tabCounter,
        id = "tabs-" + tabCounter,
        tabContent = tabContent.replace( /#\{tid\}/g, tabCounter )
        li = $( tabTemplate.replace( /#\{href\}/g, "#" + id ).replace( /#\{label\}/g, label ) ),
        tabContentHtml = tabContent || "Tab " + tabCounter + " content.";
 
		  tabs.find( ".ui-tabs-nav" ).append( li );
		  tabs.append( "<div id='" + id + "'>" + tabContentHtml + "</div>" );
		  tabs.tabs( "refresh" );
		  rli[tabCounter] = room;
		  tabCounter++;
	   }
 
    // close icon: removing the tab on click
    tabs.delegate( "span.ui-icon-close", "click", function() {
      var panelId = $( this ).closest( "li" ).remove().attr( "aria-controls" );
      $( "#" + panelId ).remove();
      var qpm = S(panelId).between('tabs-', '').s
      socket.emit('qroom', rli[qpm])
      var index = pms.indexOf(rli[qpm]);
      delete pms[index];
      delete rli[qpm];
      tabs.tabs( "refresh" );
  });
	
	
	
	
	/*
	$('#jroom').click(function () {
		socket.disconnect();
		applog('<p>Client Disconnected</p>');
	});
	
	$('#lroom').click(function () {
		socket.disconnect();
		applog('<p>Client Disconnected</p>');
	});
	*/
});

	
