var peers = {};
var videoGrid = document.getElementById("video-grid");
var socket = io.connect(`https://${document.domain}:5001`);
var peer = new Peer(userId);

function pasteMessage(username, message) {
    const new_message = document.createElement('p');
    new_message.innerHTML = `<b>${username}</b> ${message}`;
    document.getElementById('messages').append(new_message);
}

function leaveCall() {
    for (let userPeer of Object.values(peers)) {
        userPeer.close();
    }
    socket.emit("user-disconnected", {
        leaveId: userId,
        username: fullname,
        conference: conf_id
    });
}

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

function addUserVideo(videoObj, userStream) {
    videoObj.srcObject = userStream;
    videoObj.onloadedmetadata = () => {
        videoObj.play();
    }
    videoGrid.appendChild(videoObj);
}

function connectToNewUser(user, stream) {
    const call = peer.call(user, stream);
    if (call) {
        const userVideo = document.createElement('video');
        call.on('stream', userVideoStream => {
            addVideoStream(userVideo, userVideoStream);
        })
        call.on('close', () => {
            userVideo.remove();
        })
        console.log(call);
        peers[user] = call;
    }
}

async function fetchChatStory() {
    return fetch(`/getstory/${conf_id}`)
    .then(response => {
        response.json()
        .then(data => {
            data.story.forEach(row => {
                pasteMessage(row.username, row.message);
            })
        })
    })
    .catch(err => { console.error(err); });
}

document.querySelector('#send_text').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') { sendMessage(); }
})
document.querySelector('#send_msg').onclick = (e) => { sendMessage(); }

socket.on('receive-message', data => {
    pasteMessage(data.username, data.message);
});

socket.on('connect', () => {
    fetchChatStory().then(() => {
        navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        .then(stream => {
            var video = document.createElement("video");
            addUserVideo(video, stream);
            peer.on("call", call => {
                if (call) {
                    call.answer(stream);
                    var videoUser = document.createElement("video");
                    call.on("stream", userVideoStream => {
                        addUserVideo(videoUser, userVideoStream);
                    })
                }
            })

            socket.on("user-joined", joinedUserId => {
                if (userId != joinedUserId) {
                    connectToNewUser(joinedUserId, stream);
                }
            });

            // socket.on("user-left", leftUserId => {
            //     peers[leftUserId].close();
            // })
        })
        .catch(err => { console.error(err)} );

        socket.emit('user-connected', {
            joinedId: userId,
            username: fullname,
            conference: conf_id
        });
    });
});
