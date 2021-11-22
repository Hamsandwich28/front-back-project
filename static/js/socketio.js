document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    let room;

    socket.on('message', data => {
        const p = document.createElement('p');
        const span_username = document.createElement('span');
        const span_timestamp = document.createElement('span');
        const br = document.createElement('br');
        span_username.innerHTML = data.username;
        span_timestamp.innerHTML = data.time_stamp;
        p.innerHTML = span_username.outerHTML + br.outerHTML + data.msg + br.outerHTML
            + span_timestamp.outerHTML;
        document.querySelector('#display-message-section').append(p);
    });

    document.querySelector('#send_message').onclick = () => {
        console.log(username);
        socket.send({'msg': document.querySelector('#user_message').value,
                     'username': username});
    }

    function leaveRoom(room) {
        socket.emit('leave', {'username': username, 'room': room});
    }

    function joinRoom(room) {
        socket.emit('join', {'username': username, 'room': room});
    }

})