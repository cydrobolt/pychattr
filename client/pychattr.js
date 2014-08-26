/*
* PyChattr JavaScript Client Library 
* [c] Copyright 2014 Chaoyi Zha
* </>ed w/ <3 in Philly in '14
* Authors: Chaoyi Zha <summermontreal@gmail.com>
* Dependencies: socket.io, jQuery 1.x
*/

var domain = 'localhost';
var port = 5000;
var token;

function temit(event, message) {
	socket.emit(event, {"data": message, "token": token});	
}
function tsend(message) {
	socket.send({"data": message, "token": token});	
}
$(document).ready(function(){
    var socket = io.connect('http://' + domain + ':' + port + '/pychattr');
    socket.on('auth', function(msg) {
        $('#log').append('<p>Received: ' + msg + '</p>');
        token = window.prompt('Please insert your token to authenticate.');
        socket.emit('auth', token);
    });
    socket.on('message', function(msg) {
        $('#log').append('<p>Received: ' + msg + '</p>');
        if (msg.tojoin && msg.joined) {
			$('#log').append('<p>PM Request from ' + msg.joined + ' to '+ msg.tojoin +'</p>');
		}
			
    });
    socket.on('disconnected', function(msg) {
        $('#log').append('<p>Disconnected by server.</p>');
        socket.disconnect();
    });
    $('#pm').click(function () {
		var topm = window.prompt('Who would you like to PM');
		socket.emit('pmuser', topm);
		console.log('PMing '+topm);
	});
});

	
