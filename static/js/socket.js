document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', () => {
        //СОЕДИНЕНИЕ ПОЛЬЗОВАТЕЛЯ СО СТРАНИЦЕЙ КОМНАТЫ
        //ЗДЕСЬ ПРОИСХОДИТ ПОДКЛЮЧЕНИЕ АУДИО\ВИДЕО
        socket.emit('join', {
            username: fullname,
            conference: conf_id
        });

        let message_input = document.querySelector('#send_text');
        document.querySelector('#send_msg').onclick = (e) => {
            let message = message_input.value;
            if (message.length) {
                socket.emit('send_message', {
                    username: fullname,
                    conference: conf_id,
                    message: message
                })
            }
            message_input.value = "";
            message_input.focus();
        }
    });

    window.onbeforeunload = () => {
        //ДИСКОНЕКТ ПОЛЬЗОВАТЕЛЯ ОТ КОМНАТЫ
        //ЗДЕСЬ РАЗРЫВАЕТСЯ СВЯЗЬ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ С УХОДЯЩИМ
        socket.emit('leave', {
            username: fullname,
            conference: conf_id
        })
    };

    socket.on('receive_message', data => {
        const new_message = document.createElement('p')
        new_message.innerHTML = `<b>${data.username}</b> ${data.message}`;
        document.querySelector('#messages').appendChild(new_message);
    });

    socket.on('join_announcement', data => {
        const new_message = document.createElement('p');
        new_message.innerHTML = `<b>${data.username} зашёл в чат.</b>`;
        document.querySelector('#messages').appendChild(new_message);
    });

    socket.on('leave_announcement', data => {
        const new_message = document.createElement('p');
        new_message.innerHTML = `<b>${data.username} вышел из чата.</b>`;
        document.querySelector('#messages').appendChild(new_message);
    });
});