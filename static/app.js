/* COURT VISION AI: MAIN JAVASCRIPT CONTROLLER */

document.addEventListener("DOMContentLoaded", () => {
    // UI Elements
    const dropzone = document.getElementById("dropzone");
    const videoInput = document.getElementById("video-input");
    const dropzoneDefault = document.getElementById("dropzone-default");
    const previewContainer = document.getElementById("preview-container");
    const videoPreview = document.getElementById("video-preview");
    const fileNameDisplay = document.getElementById("file-name");
    const fileSizeDisplay = document.getElementById("file-size");
    const btnRemoveVideo = document.getElementById("btn-remove-video");
    const btnAnalyze = document.getElementById("btn-analyze");
    
    const outputPlaceholder = document.getElementById("output-placeholder");
    const loadingOverlay = document.getElementById("loading-overlay");
    const loadingStatus = document.getElementById("loading-status");
    const loadingSubstatus = document.getElementById("loading-substatus");
    const resultsDisplay = document.getElementById("results-display");
    const resFilename = document.getElementById("res-filename");
    const resSize = document.getElementById("res-size");
    const reportContent = document.getElementById("report-content");

    let selectedFile = null;
    let loadingInterval = null;

    // Status message logs during analysis
    const statusSteps = [
        { status: "Uploading video...", substatus: "Sending video file to FastAPI backend" },
        { status: "Uploading to Gemini Cloud...", substatus: "Transferring file to Google's multimodal file API" },
        { status: "Processing video...", substatus: "Google is parsing kinematics and temporal sequence" },
        { status: "Biomechanical analysis...", substatus: "Inspecting joints, base stance, and set points" },
        { status: "Form flaw extraction...", substatus: "Isolating primary release and stance errors" },
        { status: "Querying ChromaDB...", substatus: "Retrieving matching coaching drills and reference clips" },
        { status: "Synthesizing coaching plan...", substatus: "Assembling custom coaching guide with YouTube timestamps" }
    ];

    // Drag and Drop Event Listeners
    ["dragenter", "dragover"].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.classList.add("dragover");
        }, false);
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.classList.remove("dragover");
        }, false);
    });

    dropzone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    // File Input Listener
    videoInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    // Remove Selected Video
    btnRemoveVideo.addEventListener("click", (e) => {
        e.stopPropagation(); // Avoid triggering dropzone click
        resetUploadState();
    });

    // Start Analysis Pipeline
    btnAnalyze.addEventListener("click", () => {
        if (!selectedFile) return;
        runRAGAnalysis();
    });

    // Helper: Handle File Selection and Validate
    function handleFileSelect(file) {
        // Validate it is a video file
        if (!file.type.startsWith("video/")) {
            alert("Invalid file format. Please upload a video file (.mp4, .mov).");
            return;
        }

        // Validate size (10MB Max limit)
        const sizeInMB = file.size / (1024 * 1024);
        if (sizeInMB > 10.0) {
            alert(`File size exceeds 10MB limit. Your file is ${sizeInMB.toFixed(2)}MB. Please crop the video.`);
            return;
        }

        selectedFile = file;

        // Display metadata
        fileNameDisplay.textContent = file.name;
        fileSizeDisplay.textContent = `${sizeInMB.toFixed(2)} MB`;

        // Load preview
        const fileURL = URL.createObjectURL(file);
        videoPreview.src = fileURL;
        
        // Toggle view
        dropzoneDefault.style.display = "none";
        previewContainer.style.display = "flex";
        btnAnalyze.disabled = false;
    }

    // Helper: Reset Upload Panel state
    function resetUploadState() {
        selectedFile = null;
        videoInput.value = "";
        videoPreview.src = "";
        
        previewContainer.style.display = "none";
        dropzoneDefault.style.display = "flex";
        btnAnalyze.disabled = true;
    }

    // Helper: Cycle through status logging messages
    function startLoadingAnimations() {
        let stepIdx = 0;
        
        // Show initial message
        loadingStatus.textContent = statusSteps[0].status;
        loadingSubstatus.textContent = statusSteps[0].substatus;
        
        loadingInterval = setInterval(() => {
            stepIdx++;
            if (stepIdx < statusSteps.length) {
                loadingStatus.textContent = statusSteps[stepIdx].status;
                loadingSubstatus.textContent = statusSteps[stepIdx].substatus;
            } else {
                // If it takes longer, display a waiting tag
                loadingStatus.textContent = "Finalizing coaching report...";
                loadingSubstatus.textContent = "Formatting Markdown outputs and verification drill links";
            }
        }, 3000); // Shift steps every 3 seconds
    }

    function stopLoadingAnimations() {
        if (loadingInterval) {
            clearInterval(loadingInterval);
            loadingInterval = null;
        }
    }

    // Main API Fetch Call
    async function runRAGAnalysis() {
        const formData = new FormData();
        formData.append("file", selectedFile);

        // UI transitions to loading mode
        outputPlaceholder.style.display = "none";
        resultsDisplay.style.display = "none";
        loadingOverlay.style.display = "flex";
        btnAnalyze.disabled = true;
        
        startLoadingAnimations();

        try {
            const response = await fetch("/api/coach/analyze", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Server error during video processing.");
            }

            const data = await response.json();

            if (data.status === "success") {
                renderAnalysisResult(data);
            } else {
                throw new Error("Invalid response status from API.");
            }

        } catch (error) {
            console.error("RAG pipeline failed:", error);
            alert(`Analysis failed: ${error.message}`);
            
            // Revert layout back to wait state
            outputPlaceholder.style.display = "flex";
        } finally {
            // Remove loading screen
            stopLoadingAnimations();
            loadingOverlay.style.display = "none";
            btnAnalyze.disabled = false;
        }
    }

    // Helper: Render markdown and details onto dashboard
    function renderAnalysisResult(data) {
        // Set metadata headers
        resFilename.textContent = data.filename;
        resSize.textContent = `${(data.size_bytes / (1024 * 1024)).toFixed(2)} MB`;
        
        // Parse and render markdown using marked.js
        // Customizing marked target configuration to open links in a new tab
        marked.setOptions({
            gfm: true,
            breaks: true
        });
        
        const rawReport = data.report;
        const htmlReport = marked.parse(rawReport);
        
        reportContent.innerHTML = htmlReport;
        
        // Ensure all rendered links open in a new tab for clean context retention
        const links = reportContent.querySelectorAll("a");
        links.forEach(link => {
            link.setAttribute("target", "_blank");
            link.setAttribute("rel", "noopener noreferrer");
        });

        // Trigger show transitions
        resultsDisplay.style.display = "flex";
    }
});
