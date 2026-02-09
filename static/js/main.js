
window.addEventListener("DOMContentLoaded", (event) => {
    const socket = io();

    const lights = {
      red:    document.getElementById('red'),
      yellow: document.getElementById('yellow'),
      green:  document.getElementById('green')
    };

    function resetLights() {
      Object.values(lights).forEach(light => light.classList.remove('lit'));
    }

    socket.on('connect', () => {
      document.getElementById('status').textContent = 'Connected';
    });

    socket.on('light_update', (data) => {
      const color = data.color;
      resetLights();

      if (lights[color]) {
        lights[color].classList.add('lit');
        document.getElementById('status').textContent = `Active: ${color.toUpperCase()}`;
      }
    });

    socket.on('disconnect', () => {
      document.getElementById('status').textContent = 'Disconnected – reconnecting...';
      resetLights();
    });
});
