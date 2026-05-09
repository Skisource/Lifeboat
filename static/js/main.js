// Lifeboat Familiarisation - Main JavaScript

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("upload-form");
    const generateBtn = document.getElementById("generate-btn");
    const errorMessage = document.getElementById("error-message");
    const loading = document.getElementById("loading");
    const dropZones = document.querySelectorAll(".drop-zone");

    const files = {
        familiarisation: null,
        pob: null,
    };

    // Set up drop zones
    dropZones.forEach((zone) => {
        const inputName = zone.dataset.input;
        const fileInput = zone.querySelector('input[type="file"]');
        const fileNameDisplay = zone.querySelector(".file-name");

        // Click to open file dialog
        zone.addEventListener("click", () => fileInput.click());

        // File input change
        fileInput.addEventListener("change", (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0], inputName, zone, fileNameDisplay);
            }
        });

        // Drag and drop events
        zone.addEventListener("dragover", (e) => {
            e.preventDefault();
            zone.classList.add("drag-over");
        });

        zone.addEventListener("dragleave", () => {
            zone.classList.remove("drag-over");
        });

        zone.addEventListener("drop", (e) => {
            e.preventDefault();
            zone.classList.remove("drag-over");

            const droppedFiles = e.dataTransfer.files;
            if (droppedFiles.length > 0) {
                const file = droppedFiles[0];
                if (file.name.endsWith(".xlsx")) {
                    handleFile(file, inputName, zone, fileNameDisplay);
                    fileInput.files = droppedFiles;
                } else {
                    showError("Please upload only .xlsx files");
                }
            }
        });
    });

    function handleFile(file, inputName, zone, fileNameDisplay) {
        files[inputName] = file;
        zone.classList.add("has-file");
        fileNameDisplay.textContent = file.name;
        updateGenerateButton();
    }

    function updateGenerateButton() {
        generateBtn.disabled = !(files.familiarisation && files.pob);
    }

    function showError(message) {
        errorMessage.querySelector(".error-text").textContent = message;
        errorMessage.style.display = "block";
    }

    function hideError() {
        errorMessage.style.display = "none";
    }

    // Form submission
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        hideError();

        if (!files.familiarisation || !files.pob) {
            showError("Please upload both files");
            return;
        }

        const formData = new FormData();
        formData.append("familiarisation", files.familiarisation);
        formData.append("pob", files.pob);

        const vesselName = form.querySelector('input[name="vessel_name"]').value;
        if (vesselName) {
            formData.append("vessel_name", vesselName);
        }

        // Show loading
        generateBtn.style.display = "none";
        loading.style.display = "block";

        try {
            const response = await fetch("/generate", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || "Failed to generate PDF");
            }

            // Download the PDF
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "lifeboat_familiarisation.pdf";
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        } catch (error) {
            showError(error.message);
        } finally {
            // Hide loading
            loading.style.display = "none";
            generateBtn.style.display = "inline-flex";
        }
    });
});
