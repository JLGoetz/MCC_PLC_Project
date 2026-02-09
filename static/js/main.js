 const evtSource = new EventSource("/stream");

// Reset all lights
function resetLights() {
    document.getElementById('red').classList.remove('lit');
    document.getElementById('yellow').classList.remove('lit');
    document.getElementById('green').classList.remove('lit');
}

evtSource.onmessage = function(event) {
    const active = event.data.trim();  // 'red', 'yellow', or 'green'

    resetLights();

    if (active === 'red') {
        document.getElementById('red').classList.add('lit');
    } else if (active === 'yellow') {
        document.getElementById('yellow').classList.add('lit');
    } else if (active === 'green') {
        document.getElementById('green').classList.add('lit');
    }
};

evtSource.onerror = function() {
    console.log("SSE error – will auto-reconnect");
    resetLights();
    document.querySelector('h1').textContent = "Reconnecting...";
};

evtSource.onopen = function() {
    document.querySelector('h1').textContent = "Live Traffic Light";
};