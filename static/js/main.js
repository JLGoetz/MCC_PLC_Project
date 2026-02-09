
window.addEventListener("DOMContentLoaded", (event) => {
    const evtSource = new EventSource("/stream");

    // Reset all lights
    function resetLights() {
        let lights = ['red', 'green', 'yellow'];
        for (const color of lights){
            // First, get a reference to the DOM element you want to check.
            // You can use methods like document.querySelector(), document.getElementById(), etc.
            const element = document.querySelector(`#${color}`); 
            // or const element = document.getElementById('myElementId');

            // Check if the element variable actually found an element
            if (element) {
            // Use the classList.contains() method
            const hasClass = element.classList.contains('lit');

            if (hasClass) {
                document.getElementById(color).classList.remove('lit');
                } 
            }
        //document.getElementById('red').classList.remove('lit');
        //document.getElementById('yellow').classList.remove('lit');
        //document.getElementById('green').classList.remove('lit');
        }
    }

    evtSource.onmessage = function(event) {
        const active = event.data.trim();  // 'red', 'yellow', or 'green'
        console.log("Received event: " + active);
        resetLights();
        
        if (active === 'red') {
            const element = document.getElementById('red'); 
            if (element) {
                document.getElementById('red').classList.add('lit');
                const hasClass = element.classList.contains('lit');
                console.log("Element found: " + element + ", has 'lit' class: " + hasClass);
            } 
        } else if (active === 'yellow') {
            const element = document.getElementById('yellow'); 
            if (element) {
                document.getElementById('yellow').classList.add('lit');
                const hasClass = element.classList.contains('lit');
                console.log("Element found: " + element + ", has 'lit' class: " + hasClass);
            } 
        } else if (active === 'green') {
            const element = document.getElementById('green'); 
            if (element) {
                document.getElementById('green').classList.add('lit');
                const hasClass = element.classList.contains('lit');
                console.log("Element found: " + element + ", has 'lit' class: " + hasClass);
            } 
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
});
