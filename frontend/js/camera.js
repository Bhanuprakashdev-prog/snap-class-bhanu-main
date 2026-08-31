/**
 * SnapClass WebRTC Camera Engine with Exact 4:3 Crop and HUD Overlays
 */

window.CameraEngine = {
  stream: null,
  activeVideoId: null,

  start: async (videoElementId, facingMode = 'user') => {
    const video = document.getElementById(videoElementId);
    if (!video) {
      console.error(`Video container #${videoElementId} not found.`);
      return false;
    }

    try {
      if (window.CameraEngine.stream) {
        window.CameraEngine.stop();
      }

      const constraints = {
        video: {
          facingMode: facingMode,
          aspectRatio: { ideal: 4 / 3 },
          width: { ideal: 1280 },
          height: { ideal: 960 }
        },
        audio: false
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      video.srcObject = stream;
      video.setAttribute('playsinline', 'true');
      await video.play();

      window.CameraEngine.stream = stream;
      window.CameraEngine.activeVideoId = videoElementId;

      // Update parent HUD indicators if present
      const container = video.closest('.camera-container');
      if (container) {
        const placeholder = container.querySelector('.camera-placeholder');
        if (placeholder) placeholder.style.display = 'none';
        const hud = container.querySelector('.camera-hud');
        if (hud) hud.style.display = 'flex';
      }

      return true;
    } catch (err) {
      console.error('Camera initialization error:', err);
      let msg = 'Camera access was denied. Please allow camera permissions in your browser.';
      if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        msg = 'No camera device found on this system.';
      } else if (err.name === 'NotReadableError') {
        msg = 'Camera is currently in use by another application.';
      }
      window.SnapClass.showToast(msg, 'error');
      return false;
    }
  },

  stop: () => {
    if (window.CameraEngine.stream) {
      window.CameraEngine.stream.getTracks().forEach(track => track.stop());
      window.CameraEngine.stream = null;
    }
  },

  // Captures exact 4:3 frame matching what the user sees in the viewfinder
  captureBlob: async (videoElementId) => {
    const video = document.getElementById(videoElementId);
    if (!video || !window.CameraEngine.stream) return null;

    const canvas = document.createElement('canvas');
    const vWidth = video.videoWidth || 640;
    const vHeight = video.videoHeight || 480;

    // Crop to strictly 4:3 centered if stream differs
    const targetAspect = 4 / 3;
    const currentAspect = vWidth / vHeight;

    let sWidth = vWidth;
    let sHeight = vHeight;
    let sx = 0;
    let sy = 0;

    if (currentAspect > targetAspect) {
      sWidth = vHeight * targetAspect;
      sx = (vWidth - sWidth) / 2;
    } else if (currentAspect < targetAspect) {
      sHeight = vWidth / targetAspect;
      sy = (vHeight - sHeight) / 2;
    }

    canvas.width = 640;
    canvas.height = 480;
    const ctx = canvas.getContext('2d');

    // Draw frame without mirroring (natural unmirrored photo for recognition AI)
    ctx.drawImage(video, sx, sy, sWidth, sHeight, 0, 0, canvas.width, canvas.height);

    return new Promise(resolve => {
      canvas.toBlob(resolve, 'image/jpeg', 0.92);
    });
  }
};
