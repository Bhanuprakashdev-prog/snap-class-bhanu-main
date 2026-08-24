window.Camera = {
    stream: null,
    
    start: async (videoElementId) => {
        const videoElement = document.getElementById(videoElementId);
        if (!videoElement) {
            console.error(`Video element ${videoElementId} not found`);
            return false;
        }

        try {
            // Request 4:3 aspect ratio explicitly
            const constraints = {
                video: {
                    facingMode: 'user',
                    aspectRatio: 4/3,
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                },
                audio: false
            };
            
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            videoElement.srcObject = stream;
            
            // Required for iOS Safari
            videoElement.setAttribute('playsinline', true);
            videoElement.play();
            
            window.Camera.stream = stream;
            return true;
        } catch (err) {
            console.error('Camera access denied or error:', err);
            window.SnapClassAPI.showToast('Please allow camera access to use FaceID', 'error');
            return false;
        }
    },
    
    stop: () => {
        if (window.Camera.stream) {
            window.Camera.stream.getTracks().forEach(track => track.stop());
            window.Camera.stream = null;
        }
    },
    
    captureBlob: async (videoElementId) => {
        const video = document.getElementById(videoElementId);
        if (!video || !window.Camera.stream) return null;
        
        const canvas = document.createElement('canvas');
        // Use actual video dimensions
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        const ctx = canvas.getContext('2d');
        // Draw image naturally
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        return new Promise((resolve) => {
            canvas.toBlob(resolve, 'image/jpeg', 0.9);
        });
    }
};
