const video = document.getElementById('videoElement');
let stream = null;

async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    video.style.display = 'block';
  } catch (err) {
    console.error('Erro', err);
    alert('Erro ao acessar câmera.');
  }
}

function stopCamera() {
  if (stream) {
    const tracks = stream.getTracks();
    tracks.forEach((track) => track.stop());
    video.srcObject = null;
    video.style.display = 'none';
  }
}

const textInput = document.getElementById('textInput');
const placeholder = document.getElementById('textPlaceholder');
const imagesContainer = document.getElementById('signImagesContainer');

function handleKeyPress(event) {
  if (event.key === 'Enter') {
    translateText();
  }
}

function translateText() {
  const text = textInput.value.trim();

  if (text === '') {
    placeholder.classList.remove('opacity-0', 'hidden');
    imagesContainer.classList.add('hidden');
    return;
  }

  placeholder.classList.add('opacity-0');
  setTimeout(() => {
    placeholder.classList.add('hidden');
  }, 300);

  imagesContainer.innerHTML = '';

  const numberOfSigns = Math.min(text.split(' ').length, 4) || 1;

  for (let i = 0; i < numberOfSigns; i++) {
    const img = document.createElement('img');
    img.src = `https://placehold.co/300x400/${
      i % 2 === 0 ? '6B63FF' : 'C4BFFF'
    }/ffffff?text=Sinal+${i + 1}`;
    img.className =
      'h-[50vh] md:h-[60vh] w-auto object-contain rounded-xl shadow-lg hover:scale-105 transition-transform duration-300';
    imagesContainer.appendChild(img);
  }

  imagesContainer.classList.remove('hidden');
  imagesContainer.classList.add('flex');
}
