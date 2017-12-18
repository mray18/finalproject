

function postData(path, entry, callback) {
    console.log('URL', path);
    var httpRequest = new XMLHttpRequest();

    httpRequest.open('POST', path);
    httpRequest.setRequestHeader('Content-type', 'application/json');

    httpRequest.onreadystatechange = function () {
        if (httpRequest.readyState === 4 && httpRequest.status === 200) {
            var data = JSON.parse(httpRequest.responseText);
            if (callback) {
                if (data.errorMessage) {
                    callback(data.errorMessage);
                }
                callback(null, data.updated);
            }
        }
    };
    console.log("sending: ", entry);
    httpRequest.send(entry);
}		 
		
function getData(path, callback) {
    var httpRequest = new XMLHttpRequest();
    httpRequest.onreadystatechange = function () {
        if (httpRequest.readyState === 4) {
            if (httpRequest.status === 200) {
                var data = JSON.parse(httpRequest.responseText);
                if (callback) {
                    callback(data);
                }
            }
        }
    };

    httpRequest.open('GET', path);
    httpRequest.send();
}


function putData(path, entry, callback) {
    var httpRequest = new XMLHttpRequest();

    httpRequest.open('PUT', path);
    httpRequest.setRequestHeader('Content-type', 'application/json');

    httpRequest.onreadystatechange = function () {
        if (httpRequest.readyState === 4 && httpRequest.status === 200) {
            var data = JSON.parse(httpRequest.responseText);
            if (callback) {
                if (data.errorMessage) {
                    callback(data.errorMessage);
                }
                callback(null, data.updated);
            }
        }
    };
    console.log("sending: ", entry);
    httpRequest.send(entry);
}

function deleteData(path, entry, callback) {
    var httpRequest = new XMLHttpRequest();

    httpRequest.open('DELETE', path);
    httpRequest.setRequestHeader('Content-type', 'application/json');

    httpRequest.onreadystatechange = function () {
        if (httpRequest.readyState === 4 && httpRequest.status === 200) {
            var data = JSON.parse(httpRequest.responseText);
            if (callback) {
                if (data.errorMessage) {
                    callback(data.errorMessage);
                }
                callback(null, data.updated);
            }
        }
    };
    console.log("sending: ", entry);
    httpRequest.send(entry);
}