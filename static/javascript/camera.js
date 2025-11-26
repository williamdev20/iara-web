const video = document.getElementById('videoElement');
let stream = null;
let intervalId = null;
let lastSignal = null;

async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 1280 }, height: { ideal: 720 } },
    });

    const video = document.getElementById('videoElement');
    video.srcObject = stream;
    video.style.display = 'block';

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    intervalId = setInterval(() => {
      if (!stream || video.videoWidth === 0) return;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // grayscale quebra o codigo n mexe <3

      // const frame = ctx.getImageData(0, 0, canvas.width, canvas.height);
      // const data = frame.data;
      // for (let i = 0; i < data.length; i += 4) {
      //   const g = (data[i] + data[i + 1] + data[i + 2]) / 3;
      //   data[i] = data[i + 1] = data[i + 2] = g;
      // }

      // ctx.putImageData(frame, 0, 0);

      // ctx.filter = "grayscale(100%)";
      // ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      // ctx.filter = "none";

      canvas.toBlob(
        (blob) => {
          const reader = new FileReader();
          reader.onloadend = () => {
            fetch('/process-frame/', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ frame: reader.result }),
            })
              .then((response) => response.json())
              .then((data) => {
                const response = document.getElementById('response');

                if (data.sinal !== lastSignal) {
                  lastSignal = data.sinal;

                  if (data.sinal !== "Desconhecido") {
                    const voice = new Audio(data.voice_url);
                    voice.play();
                  }
                }

                if (data.sinal === 'Desconhecido') {
                  response.textContent = 'Aguardando sinais...';
                } else {
                  response.textContent = data.sinal || 'Nenhum sinal detectado';
                }
              
              })
              .catch((err) => console.error('Erro ao processar frame:', err));
          };
          reader.readAsDataURL(blob);
        },
        'image/jpeg',
        0.5
      );
    }, 500);
  } catch (err) {
    console.error('Erro:', err);
    alert('Erro ao acessar a câmera.');
  }
}

function stopCamera() {
  if (stream) {
    if (intervalId != null) {
      clearInterval(intervalId);
    }
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

let cancelTranslation = false;

function resetUI() {
  imagesContainer.innerHTML = "";
  imagesContainer.classList.add("hidden");
  placeholder.classList.remove("hidden");
  setTimeout(() => placeholder.classList.remove("opacity-0"), 10);
}

function stopTranslate() {
  cancelTranslation = true;
  resetUI();
}

async function translateText() {
  let text = textInput.value.trim();
  text = text.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  text = text.replace(/[^a-zA-Z]/g, "");
  text = text.toLowerCase();

  cancelTranslation = false;

  if (text === "") {
    resetUI();
    return;
  }

  placeholder.classList.add("opacity-0");
  setTimeout(() => placeholder.classList.add("hidden"), 300);

  imagesContainer.innerHTML = "";
  imagesContainer.classList.remove("hidden");

  const counter = document.createElement("p");
  counter.style.color = "white";
  counter.style.fontSize = "20px";
  counter.style.fontWeight = "bold";
  counter.style.marginBottom = "10px";

  const img = document.createElement("img");
  img.style.width = "200px";
  img.style.height = "240px";
  img.style.objectFit = "cover";
  img.style.borderRadius = "8px";
  img.style.boxShadow = "0px 4px 10px rgba(0,0,0,0.3)";

  imagesContainer.appendChild(counter);
  imagesContainer.appendChild(img);

  for (let i = 0; i < text.length; i++) {
    if (cancelTranslation) return resetUI();

    const letter = text.charAt(i);
    img.src = imgBaseUrl + letter + ".jpeg";
    img.alt = "Letra: " + letter;

    for (let t = 3; t > 0; t--) {
      if (cancelTranslation) return resetUI();
      counter.textContent = `Mudando para o próximo sinal em ${t}s...`;
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }

  resetUI();
}
