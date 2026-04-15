const startCameraButton = document.querySelector("#startCameraButton");
const stopCameraButton = document.querySelector("#stopCameraButton");
const captureButton = document.querySelector("#captureButton");
const analyzeButton = document.querySelector("#analyzeButton");
const autoAnalyzeButton = document.querySelector("#autoAnalyzeButton");
const fileInput = document.querySelector("#fileInput");
const cameraPreview = document.querySelector("#cameraPreview");
const uploadVideo = document.querySelector("#uploadVideo");
const imagePreview = document.querySelector("#imagePreview");
const emptyPreview = document.querySelector("#emptyPreview");
const sourceLabel = document.querySelector("#sourceLabel");
const videoScrubberWrap = document.querySelector("#videoScrubberWrap");
const videoScrubber = document.querySelector("#videoScrubber");
const trafficLight = document.querySelector("#trafficLight");
const scoreValue = document.querySelector("#scoreValue");
const confidenceValue = document.querySelector("#confidenceValue");
const headline = document.querySelector("#headline");
const reasons = document.querySelector("#reasons");
const playfulSuggestion = document.querySelector("#playfulSuggestion");
const caution = document.querySelector("#caution");
const statusMessage = document.querySelector("#statusMessage");
const workingCanvas = document.querySelector("#workingCanvas");

let cameraStream = null;
let currentSource = null;
let autoAnalyzeTimer = null;

function releaseCurrentObjectUrl() {
  if (currentSource?.objectUrl) {
    URL.revokeObjectURL(currentSource.objectUrl);
  }
}

function setStatus(message) {
  statusMessage.textContent = message;
}

function setSource(name) {
  sourceLabel.textContent = name;
}

function hideAllMedia() {
  cameraPreview.classList.add("hidden");
  uploadVideo.classList.add("hidden");
  imagePreview.classList.add("hidden");
  emptyPreview.classList.add("hidden");
}

function showEmptyState() {
  releaseCurrentObjectUrl();
  hideAllMedia();
  emptyPreview.classList.remove("hidden");
  videoScrubberWrap.classList.add("hidden");
  currentSource = null;
  analyzeButton.disabled = true;
  autoAnalyzeButton.disabled = true;
  captureButton.disabled = true;
  setSource("ソース未選択");
}

function stopAutoAnalyze() {
  if (autoAnalyzeTimer) {
    window.clearInterval(autoAnalyzeTimer);
    autoAnalyzeTimer = null;
  }
  autoAnalyzeButton.textContent = "実況モード OFF";
}

function stopCamera() {
  if (cameraStream) {
    for (const track of cameraStream.getTracks()) {
      track.stop();
    }
    cameraStream = null;
  }
  cameraPreview.srcObject = null;
  stopCameraButton.disabled = true;
  captureButton.disabled = true;
  stopAutoAnalyze();
  if (!currentSource || currentSource.kind === "camera") {
    showEmptyState();
  }
}

async function startCamera() {
  try {
    stopCamera();
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "user" },
      audio: false,
    });

    cameraStream = stream;
    hideAllMedia();
    cameraPreview.classList.remove("hidden");
    cameraPreview.srcObject = stream;
    currentSource = { kind: "camera" };
    setSource("ライブカメラ");
    analyzeButton.disabled = false;
    autoAnalyzeButton.disabled = false;
    stopCameraButton.disabled = false;
    captureButton.disabled = false;
    setStatus("カメラ準備完了。AI判定できます。");
  } catch (error) {
    console.error(error);
    setStatus("カメラを開始できませんでした。権限設定を確認してください。");
  }
}

function drawMediaToCanvas(element) {
  const context = workingCanvas.getContext("2d");
  const sourceWidth = element.videoWidth || element.naturalWidth || element.width;
  const sourceHeight = element.videoHeight || element.naturalHeight || element.height;
  const maxSide = 1280;
  const scale = Math.min(1, maxSide / Math.max(sourceWidth, sourceHeight));
  workingCanvas.width = Math.max(1, Math.round(sourceWidth * scale));
  workingCanvas.height = Math.max(1, Math.round(sourceHeight * scale));
  context.drawImage(element, 0, 0, workingCanvas.width, workingCanvas.height);
  return workingCanvas.toDataURL("image/jpeg", 0.86);
}

async function captureCurrentFrame() {
  if (!currentSource) {
    return null;
  }
  if (currentSource.kind === "camera") {
    return drawMediaToCanvas(cameraPreview);
  }
  if (currentSource.kind === "upload-image") {
    return drawMediaToCanvas(imagePreview);
  }
  if (currentSource.kind === "upload-video") {
    return drawMediaToCanvas(uploadVideo);
  }
  return null;
}

function updateResult(result) {
  trafficLight.dataset.signal = result.signal;
  scoreValue.textContent = String(result.score);
  confidenceValue.textContent = `${result.confidence}%`;
  headline.textContent = result.headline;
  reasons.replaceChildren(
    ...result.reasons.map((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      return li;
    }),
  );
  playfulSuggestion.textContent = result.playfulSuggestion;
  caution.textContent = result.caution;
}

async function analyzeCurrentFrame() {
  const imageDataUrl = await captureCurrentFrame();
  if (!imageDataUrl) {
    setStatus("先にカメラまたはファイルを選択してください。");
    return;
  }

  analyzeButton.disabled = true;
  setStatus("AIが空気を読んでいます...");

  try {
    const response = await fetch("/api/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        imageDataUrl,
        sourceLabel: sourceLabel.textContent,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Unknown API error");
    }
    updateResult(payload);
    setStatus(`${payload.model} が ${payload.generatedAt} に判定しました。`);
  } catch (error) {
    console.error(error);
    setStatus(`判定に失敗しました: ${error.message}`);
  } finally {
    analyzeButton.disabled = false;
  }
}

function onVideoScrub() {
  if (!uploadVideo.duration || Number.isNaN(uploadVideo.duration)) {
    return;
  }
  uploadVideo.currentTime = Number(videoScrubber.value) * uploadVideo.duration;
}

async function loadFile(file) {
  stopAutoAnalyze();
  releaseCurrentObjectUrl();

  if (!file) {
    showEmptyState();
    return;
  }

  const url = URL.createObjectURL(file);

  if (file.type.startsWith("image/")) {
    hideAllMedia();
    imagePreview.src = url;
    imagePreview.classList.remove("hidden");
    currentSource = { kind: "upload-image", objectUrl: url };
    analyzeButton.disabled = true;
    autoAnalyzeButton.disabled = true;
    captureButton.disabled = true;
    videoScrubberWrap.classList.add("hidden");
    setSource(`画像ファイル: ${file.name}`);
    setStatus("画像を読み込み中です...");
    return;
  }

  if (file.type.startsWith("video/")) {
    hideAllMedia();
    uploadVideo.src = url;
    uploadVideo.classList.remove("hidden");
    currentSource = { kind: "upload-video", objectUrl: url };
    analyzeButton.disabled = true;
    autoAnalyzeButton.disabled = true;
    captureButton.disabled = true;
    videoScrubberWrap.classList.remove("hidden");
    setSource(`動画ファイル: ${file.name}`);
    setStatus("動画を読み込み中です...");
    return;
  }

  setStatus("未対応のファイル形式です。画像か動画を選択してください。");
}

startCameraButton.addEventListener("click", startCamera);
stopCameraButton.addEventListener("click", stopCamera);
captureButton.addEventListener("click", async () => {
  if (!cameraStream) {
    return;
  }
  const snapshot = await captureCurrentFrame();
  hideAllMedia();
  imagePreview.src = snapshot;
  imagePreview.classList.remove("hidden");
  currentSource = { kind: "upload-image", dataUrl: snapshot };
  analyzeButton.disabled = false;
  autoAnalyzeButton.disabled = true;
  captureButton.disabled = true;
  stopCameraButton.disabled = false;
  setSource("カメラ静止画");
  setStatus("カメラ映像を静止画として固定しました。");
});

analyzeButton.addEventListener("click", analyzeCurrentFrame);

autoAnalyzeButton.addEventListener("click", () => {
  if (autoAnalyzeTimer) {
    stopAutoAnalyze();
    setStatus("実況モードを停止しました。");
    return;
  }
  autoAnalyzeTimer = window.setInterval(() => {
    void analyzeCurrentFrame();
  }, 8000);
  autoAnalyzeButton.textContent = "実況モード ON";
  setStatus("実況モード中。8秒ごとに再判定します。");
  void analyzeCurrentFrame();
});

fileInput.addEventListener("change", (event) => {
  const [file] = event.target.files;
  void loadFile(file);
});

videoScrubber.addEventListener("input", onVideoScrub);

uploadVideo.addEventListener("loadedmetadata", () => {
  videoScrubber.value = "0";
  analyzeButton.disabled = false;
  setStatus("動画を読み込みました。再生位置のフレームで判定します。");
});

uploadVideo.addEventListener("timeupdate", () => {
  if (!uploadVideo.duration || Number.isNaN(uploadVideo.duration)) {
    return;
  }
  videoScrubber.value = String(uploadVideo.currentTime / uploadVideo.duration);
});

imagePreview.addEventListener("load", () => {
  analyzeButton.disabled = false;
  setStatus("画像を読み込みました。AI判定できます。");
});

window.addEventListener("beforeunload", stopCamera);

showEmptyState();
