
window.addEventListener('DOMContentLoaded', () => {
    let path = window.location.search.toString()  // что было выбрано

    if (path != ''){
        console.log('Выбрано', path)
        sessionStorage.setItem("url_status", path); // сохраняем выбранный элемент
    } else {
        let run_id = sessionStorage.getItem("run_id");
        if (run_id != null) { // востанавливаем выбранный элемент
            window.location = window.location.href + '?run_id=' + run_id;
        }
    }

});

