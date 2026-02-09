
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

    // Reset button
    document.getElementById('reset-btn').addEventListener('click', () => {
      socket.emit('reset');
    });

    socket.on('connect', () => {
      document.getElementById('status').textContent = 'Connected';
    });

    socket.on('light_update', (data) => {
      const color = data.color;
      resetLights();
      if (lights[color]) {
        lights[color].classList.add('lit');
      }
      document.getElementById('status').textContent = `Active: ${color.toUpperCase()}`;
    });

    socket.on('stats_update', (data) => {
      document.getElementById('cycle').textContent = data.cycle;
      document.getElementById('red-pct').textContent = data.red_pct + '%';
      document.getElementById('yellow-pct').textContent = data.yellow_pct + '%';
      document.getElementById('green-pct').textContent = data.green_pct + '%';
    });

    socket.on('disconnect', () => {
      document.getElementById('status').textContent = 'Disconnected – reconnecting...';
      resetLights();
    });
});
