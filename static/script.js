// Image Preview and File Handling
document.getElementById('file-upload').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();

        reader.onload = function(e) {
            const previewContainer = document.getElementById('image-preview-container');
            if (previewContainer) { //check if container exists
                previewContainer.style.display = 'block';
                previewContainer.innerHTML = `<img id="image-preview" src="${e.target.result}" alt="Preview">`;
            }



            const uploadButton = document.querySelector('.upload-button');
            if (uploadButton) { //check if label exists
                    uploadButton.style.display = 'none';

            }


            const inputField=document.getElementById('file-upload')

            if (inputField) { //check if label exists
                const fakepath = inputField.value;
                const filename = fakepath.split("\\").pop();
                inputField.nextElementSibling.textContent=filename

            }



            // Progress bar animation (replace with your actual progress updates)

            const progressBar = document.getElementById('progress-bar');
            if (progressBar) { //check if progress bar exists
                progressBar.style.display = 'block';
                let width = 0;

                const interval = setInterval(() => {
                    width += 10;

                    progressBar.value = width;

                    if (width >= 100) {
                        clearInterval(interval);


                    }
                }, 100);



            }

        };

        reader.readAsDataURL(file);
    }
});






// Add any other page-specific JavaScript here (e.g., for results.html)

// Example: Displaying bounding box information, etc.