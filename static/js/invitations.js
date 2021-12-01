function accept(clicked_id) {
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/invitation_accept", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({"accepted_id": `${clicked_id}`}));
    xhr.onload = () => {
        console.log(xhr.response);
    }
    const activated = document.querySelector(`#${clicked_id}`);
    activated.innerHTML = "Принято";
    activated.disabled = true;
}