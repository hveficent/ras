function activeDirect() {
    var direct = document.getElementById("direct");
    var iot = document.getElementById("iot");
    if (direct.style.display === "none") {
        direct.style.display = "block";
        iot.style.display = "none";
    }
}

function activeIoT() {
    var direct = document.getElementById("direct");
    var iot = document.getElementById("iot");
    if (iot.style.display === "none") {
        iot.style.display = "block";
        direct.style.display = "none";
    }
}