const video = document.getElementById('videoElement');
let stream = null;

async function startCamera() {
  try {
      // Solicita resolução maior
      stream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 1280 }, height: { ideal: 720 } }
      });

      const video = document.getElementById("videoElement");
      video.srcObject = stream;
      video.style.display = "block";

      // Canvas criado UMA VEZ
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");

      // Enviar frames a cada 200ms (5 FPS)
      intervalId = setInterval(() => {
          if (!stream || video.videoWidth === 0) return;

          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;

          // Desenha o frame
          ctx.drawImage(video, 0, 0);

          // Alta qualidade do JPEG 
          const frameData = canvas.toDataURL("image/jpeg", 1.0);

          fetch("/process-frame/", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ frame: frameData })
          })
              .then(res => res.json())
              .then(data => {
                // Receni d volta
                document.getElementById('response').textContent = data.sinal || "N recebi nd"
                console.log(data)
              })
              .catch(err => console.error("Erro:", err));

      }, 500);

  } catch (err) {
      console.error("Erro:", err);
      alert("Erro ao acessar a câmera.");
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
