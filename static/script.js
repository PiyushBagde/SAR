// Image/Video Preview and File Handling
document.getElementById('file-upload').addEventListener('change', function (event) {
    const file = event.target.files[0];
    const previewContainer = document.getElementById('image-preview-container');
    const videoPreview = document.getElementById('video-preview');
    const uploadButton = document.querySelector('.upload-button');
    const inputField = document.getElementById('file-upload');


    if (file) {
        const fileType = file.type.split('/')[0]; // 'image' or 'video'

        // For both image and video:
        if (uploadButton) {
            uploadButton.style.display = 'none';
        }

        if (inputField) {
            const fakepath = inputField.value;
            const filename = fakepath.split("\\").pop();
            inputField.nextElementSibling.textContent = filename;
        }

        if (fileType === 'image') {
            const reader = new FileReader();

            reader.onload = function (e) {
                if (previewContainer) {
                    previewContainer.style.display = 'block';
                    previewContainer.innerHTML = `<img id="image-preview" src="${e.target.result}" alt="Preview">`;
                }
            };

            reader.readAsDataURL(file);
        } else if (fileType === 'video') {
            if (videoPreview) {
                videoPreview.style.display = "block";
                videoPreview.innerHTML = `<video id="video-preview-player" width="400px" controls></video>`;
                const videoElement = document.getElementById('video-preview-player');
                if (videoElement) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        videoElement.src = e.target.result;
                    };
                    reader.readAsDataURL(file);
                }
            }
        }
    }
});

// Handle form submission (for both image and video)
document.getElementById('upload-form').addEventListener('submit', function (event) {
    event.preventDefault();
    const formData = new FormData(this);
    const progressBar = document.getElementById('progress-bar');
    const loadingContainer = document.getElementById('loading-animation');

    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];

    if (!file) {
        return; // Or show an error message
    }


    // Show progress bar and loading animation *before* making the request
    if (progressBar) {
        progressBar.style.display = 'block';
        let width = 0;
        const interval = setInterval(() => {
            width += 5;
            progressBar.value = width;
            if (width >= 100) {
                clearInterval(interval);
            }
        }, 200);
    }

    if (loadingContainer) {
        loadingContainer.style.display = "block";
        loadingContainer.innerHTML = '<div class="loader"></div>';
    }


    const fileType = file.type.split('/')[0]; // 'image' or 'video'
    const endpoint = fileType === 'image' ? '/image_upload' : '/video_upload';

    fetch(endpoint, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {


            // Check for errors in the response
            if (data.error) {
                alert(data.error); // Display the error to the user

                // Hide the loading animation and progress bar since there is an error
                if (progressBar) {
                    progressBar.style.display = 'none';
                }
                if (loadingContainer) {
                    loadingContainer.style.display = "none";
                }
                return; // Stop further execution
            }


            // Hide the loading animation and progress bar *after* successful response

            if (progressBar) {
                progressBar.style.display = 'none';
            }
            if (loadingContainer) {
                loadingContainer.style.display = "none";
            }


            if (fileType === 'image') {

                window.location.href = '/results/' + data.original_image_name + '/' + data.annotated_image_name;
            } else { // For video
                window.location.href = '/video_results/' + data.video_path;
            }
        })
        .catch(error => {
            console.error('Error during upload:', error);

            // Hide the loading animation and progress bar in case of error
            if (progressBar) {
                progressBar.style.display = 'none';
            }
            if (loadingContainer) {
                loadingContainer.style.display = "none";
            }

        });
});