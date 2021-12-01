function deleteconf() { 
    if (confirm("Вы уверены?")) {
        let xhr = new XMLHttpRequest();
        let data = JSON.stringify({"on_delete": conference_id})
        xhr.open("DELETE", "/conference/delete", true);
        xhr.setRequestHeader('Content-type','application/json; charset=utf-8');
        xhr.onload = () => {
            let answer = JSON.parse(xhr.responseText);
            if (xhr.readyState == 4 && xhr.status == "200") {
                if (answer.deleted == true) {
                    window.location = back_url;
                } else {
                    alert("Конференция не была удалена, перезагрузите страницу");
                }
            }
        }
        xhr.send(data);
    } else {
        return undefined;
    }
}