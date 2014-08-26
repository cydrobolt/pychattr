/*
* PyChattr JavaScript Client Library 
* [c] Copyright 2014 Chaoyi Zha and DogeBoosting
* </>ed w/ <3 in Philly in '14
* Authors: Chaoyi Zha <summermontreal@gmail.com>
* Dependencies: socket.io.min.js
*/

var domain = 'localhost';
var port = 5000;

$(document).ready(function(){
    var socket = io.connect('http://' + domain + ':' + port + '/pychattr');
    socket.on('auth', function(msg) {
        $('#log').append('<p>Received: ' + msg + '</p>');
    });
    socket.on('message', function(msg) {
        $('#log').append('<p>Received: ' + msg + '</p>');
    });
    $('form#broadcast').submit(function(event) {
        socket.emit('my broadcast event', {data: $('#broadcast_data').val()});
        return false;
    });
});
