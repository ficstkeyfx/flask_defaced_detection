var socket = io();
socket.emit('notification');
socket.on('connect', function() {
    console.log("Hello");
});
$("#notification").hide();
socket.on('notification', function(status) {
    if(status == 1){
        $("#notification").show();
    }else {
        $("#notification").hide();
    }
    socket.emit('notification');
});