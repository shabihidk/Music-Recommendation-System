// Toggle play/pause state
const playButton = document.querySelector('.play-btn');
const pauseButton = document.querySelector('.pause-btn');
const player = document.querySelector('.audio-player');

playButton.addEventListener('click', function () {
    player.play();
    playButton.style.display = 'none';
    pauseButton.style.display = 'inline-block';
});

pauseButton.addEventListener('click', function () {
    player.pause();
    playButton.style.display = 'inline-block';
    pauseButton.style.display = 'none';
});

// Example of a simple audio player setup
const audioPlayer = document.createElement('audio');
audioPlayer.src = 'your-audio-file.mp3'; // Replace with your audio file path
audioPlayer.classList.add('audio-player');
document.body.appendChild(audioPlayer);

// Simulate a playlist selection (example)
const playlistCards = document.querySelectorAll('.playlist-card');

playlistCards.forEach(card => {
    card.addEventListener('click', () => {
        const playlistName = card.querySelector('h3').textContent;
        alert(`Now playing playlist: ${playlistName}`);
        // Here you could load a playlist of songs dynamically
    });
});
