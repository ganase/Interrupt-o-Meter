const video = document.getElementById('preview');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const sourceUserInput = document.getElementById('sourceUser');

let stream = null;
let timer = null;
const intervalMs = 5000;

async function startCamera() {
  stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
  video.srcObject = stream;
}

function stopCamera() {
  if (!stream) return;
  for (const track of stream.getTracks()) track.stop();
  stream = null;
}

function captureBase64() {
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 360;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL('image/jpeg', 0.75).split(',')[1];
}

async function analyzeOnce() {
  const payload = {
    source_user: sourceUserInput.value || 'me',
    captured_at: new Date().toISOString(),
    image_base64: captureBase64(),
  };
  const res = await fetch('/api/analyze/frame', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) return;
  const data = await res.json();
  document.getElementById('talkOk').textContent = data.talk_ok_score;
  document.getElementById('scheduleBusy').textContent = data.schedule_busy_score;
  document.getElementById('visualBusy').textContent = data.visual_busy_score;
  document.getElementById('comment').textContent = data.comment;
}

startBtn.addEventListener('click', async () => {
  try {
    await startCamera();
    if (timer) clearInterval(timer);
    await analyzeOnce();
    timer = setInterval(analyzeOnce, intervalMs);
  } catch (e) {
    alert('カメラアクセスに失敗しました。予定表のみモードでご利用ください。');
  }
});

stopBtn.addEventListener('click', () => {
  if (timer) clearInterval(timer);
  timer = null;
  stopCamera();
});
