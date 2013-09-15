/*
    Check if browser implements WebSocket
    
    Open a new WebSocket

    When it's opened send a JSON message.

    When you receive messages, decode them with JSON, do whatever.

    When error occurs, do whatever.

    Close WebSocket after 5 seconds.
*/

function Connection(onopen,onmessage,url, port, path){
    if(url == undefined){
        url = "localhost";
    }
    if(port == undefined){
        port = 8888;
    }
    if(path == undefined){
        path = "/websocket";
    }

    if(!("WebSocket" in window)){
        alert("Your browser doesn't support WebSocket, get one that does.");
    }

    conn = this

    this.ws = new WebSocket("ws://"+url+":"+port+path);
    this.ws.onopen = function() {
        onopen(conn);
    }

    this.ws.onmessage = function (evt) {
        messages = JSON.parse(evt.data);
        for(var i in messages){
            if(messages[i][1] != null){
                onmessage(conn,messages[i][0],messages[i][1]);
            }else{
                onmessage(conn,messages[i][0],null);
            }
        }
    }

    this.ws.onerror = function (evt) {
        alert("Error occured; error is:" + evt.data);
    }

    this.send = function(identifier,content){
        if(content != null){
            conn.ws.send(JSON.stringify([[identifier,content]]));
        }else{
            conn.ws.send(JSON.stringify([[identifier]]));
        }
    }
}
