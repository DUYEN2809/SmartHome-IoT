let isRecording = false;
let mediaRecorder;
let audioChunks = [];

const recordButton = document.getElementById("recordButton");
const status = document.getElementById("status");

async function playResponseAudio() {
    const audio = document.getElementById("responseAudio");
    const audioSource = document.getElementById("audioSource");

    // Đặt đường dẫn tới file âm thanh từ API
    audioSource.src = `/get_audio`; // URL với cache buster

    // Load lại file mới và tự động phát
    try {
        await audio.load();
        await audio.play(); // Tự động phát âm thanh
    } catch (error) {
        console.error("Không thể tự động phát âm thanh:", error);
    }
}

recordButton.addEventListener("click", async () => {
    if (!isRecording) {
        // Bắt đầu ghi âm
        if (!mediaRecorder) {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                audioChunks = [];

                // Gửi file âm thanh tới server
                const response = await fetch("/save_audio", {
                    method: "POST",
                    body: audioBlob,
                });
                const result = await response.json();
                await playResponseAudio();
                if (response.ok) {
                    alert(result.message);
                    location.reload(); // Tải lại trang để cập nhật trạng thái
                }
                
            };
        }

        mediaRecorder.start();
        recordButton.textContent = "Dừng";
        status.textContent = "Đang ghi âm...";
    } else {
        // Dừng ghi âm
        mediaRecorder.stop();
        recordButton.textContent = "Nói";
        status.textContent = "Đã dừng ghi âm.";
    }

    isRecording = !isRecording;

});
