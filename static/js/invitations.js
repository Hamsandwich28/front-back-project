function accept(clicked_id) {
    let el = document.getElementById(clicked_id);
    let i = document.createElement('i');
    i.className = 'fa-solid fa-circle-check';
    el.parentNode.replaceChild(i, el);
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