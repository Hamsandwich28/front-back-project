const peers = {};
const myvideo = document.createElement('video');
const videogrid = document.getElementById('video-grid');
const page_url = `http://${document.domain}:${location.port}`;
const messages = document.querySelector('#messages');
const mypeer = new Peer(undefined, {
    host: page_url,
    port: "8001"
});

let socket = io.connect(page_url);

function sendMessage() {
    text_box = document.querySelector('#send_text');
    message = text_box.value;
    if (message.length) {
        socket.emit('user-message', {
            id_user: userId,
            username: fullname,
            conference: conf_id,
            message: message
        })
    }
    text_box.value = "";
    text_box.focus();
}

function addVideoStream(video, stream) {
    video.srcObject = stream;
    video.addEventListener('loadedmetadata', () => {
        video.play();
    });
    videogrid.append(video);
}

function connectToNewUser(user, stream) {
    const call = mypeer.call(user, stream);
    const video = document.createElement('video');
    call.on('stream', userVideoStream => {
        addVideoStream(video, userVideoStream);
    })
    call.on('close', () => {
        video.remove();
    })
    peers[user] = call;
}

socket.on('receive-message', data => {
    const new_message = document.createElement('p');
    new_message.innerHTML = `<b>${data.username}</b> ${data.message}`;
    messages.appendChild(new_message);
})

socket.on('connect', () => {
    socket.emit('user-connected', {
        username: fullname,
        conference: conf_id
    });

    navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
    }).then(stream => {
        addVideoStream(myvideo, stream);
        mypeer.on('call', call => {
            call.answer(stream);
            const video = document.createElement('video');
            call.on('stream', userVideoStream => {
                addVideoStream(video, userVideoStream);
            })
        })

        socket.on('user-joined', userid => {
            connectToNewUser(userid, stream);
        })
    })

    document.querySelector('#send_text').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') { sendMessage(); }
    })
    document.querySelector('#send_msg').onclick = (e) => { sendMessage(); }
})

window.onbeforeunload = () => {
    socket.emit('user-disconnected', {
        username: fullname,
        conference: conf_id
    })
    peers[userId].close();
};