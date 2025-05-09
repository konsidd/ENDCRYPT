// Mobile menu toggle
document.getElementById('mobile-menu-button').addEventListener('click', function() {
    const mobileMenu = document.getElementById('mobile-menu');
    mobileMenu.classList.toggle('hidden');
});

// Global variables
let originalImage = null;
let encryptedImageUrl = null;
let decryptedImageUrl = null;
let metricsChart = null;
let distributionChart = null;

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    const imageUpload = document.getElementById('image-upload');
    const processButton = document.getElementById('process-button');
    const downloadEncrypted = document.getElementById('download-encrypted');
    const downloadDecrypted = document.getElementById('download-decrypted');
    
    // Enable process button when image is uploaded
    imageUpload.addEventListener('change', function(event) {
        if (event.target.files.length > 0) {
            processButton.disabled = false;
            
            // Preview the uploaded image
            const file = event.target.files[0];
            const reader = new FileReader();
            reader.onload = function(e) {
                originalImage = e.target.result;
                
                // Create an image element to check dimensions
                const img = new Image();
                img.onload = function() {
                    if (img.width !== 256 || img.height !== 256) {
                        alert('Warning: For best results, image should be 256x256 pixels. Your image will be resized.');
                    }
                };
                img.src = originalImage;
            };
            reader.readAsDataURL(file);
        } else {
            processButton.disabled = true;
        }
    });
    
    // Process button click event
    processButton.addEventListener('click', function() {
        if (!originalImage) return;
        
        // Get encryption parameters
        const encryptionLevel = document.getElementById('encryption-level').value;
        const encryptionKey = document.getElementById('encryption-key').value;
        
        // Show loading state
        showLoading(true);
        
        // Prepare form data
        const formData = new FormData();
        formData.append('image', imageUpload.files[0]);
        formData.append('level', encryptionLevel);
        formData.append('key', encryptionKey);
        
        // Send request to backend
        fetch('/api/process-image', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Display results
                showResults(data);
                // Show metrics
                updateMetricsCharts(data.metrics);
                // Hide loading state
                showLoading(false);
            } else {
                throw new Error(data.message || 'An error occurred');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error processing image: ' + error.message);
            showLoading(false);
        });
    });
    
    // Download buttons
    downloadEncrypted.addEventListener('click', function() {
        if (encryptedImageUrl) {
            downloadImage(encryptedImageUrl, 'encrypted_image.png');
        }
    });
    
    downloadDecrypted.addEventListener('click', function() {
        if (decryptedImageUrl) {
            downloadImage(decryptedImageUrl, 'decrypted_image.png');
        }
    });
});

// Show or hide loading overlay
function showLoading(isLoading) {
    const resultsSection = document.getElementById('results-section');
    const metricsSection = document.getElementById('metrics');
    
    if (isLoading) {
        // Create loading overlay if it doesn't exist
        let loadingOverlay = document.querySelector('.loading');
        if (!loadingOverlay) {
            loadingOverlay = document.createElement('div');
            loadingOverlay.className = 'loading';
            loadingOverlay.innerHTML = '<div class="spinner"></div>';
            document.body.appendChild(loadingOverlay);
        }
        loadingOverlay.style.display = 'flex';
    } else {
        // Hide loading overlay if it exists
        const loadingOverlay = document.querySelector('.loading');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
        
        // Show results sections
        resultsSection.classList.remove('hidden');
        metricsSection.classList.remove('hidden');
    }
}

// Display results
function showResults(data) {
    // Set image sources
    document.getElementById('original-image').src = originalImage;
    document.getElementById('encrypted-image').src = data.encryptedImage;
    document.getElementById('decrypted-image').src = data.decryptedImage;
    
    // Store URLs for download
    encryptedImageUrl = data.encryptedImage;
    decryptedImageUrl = data.decryptedImage;
}

// Update metrics charts
function updateMetricsCharts(metrics) {
    // Bar chart for PSNR and Entropy
    const metricsCtx = document.getElementById('metrics-chart').getContext('2d');
    
    // Destroy previous chart instance if it exists
    if (metricsChart) {
        metricsChart.destroy();
    }
    
    metricsChart = new Chart(metricsCtx, {
        type: 'bar',
        data: {
            labels: ['Original Image', 'Encrypted Image', 'Decrypted Image'],
            datasets: [
                {
                    label: 'Entropy (bits/pixel)',
                    data: [metrics.originalEntropy, metrics.encryptedEntropy, metrics.decryptedEntropy],
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'PSNR (dB)',
                    data: [null, metrics.encryptedPSNR, metrics.decryptedPSNR],
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
    
    // Pie chart for pixel distribution
    const distributionCtx = document.getElementById('distribution-chart').getContext('2d');
    
    // Destroy previous chart instance if it exists
    if (distributionChart) {
        distributionChart.destroy();
    }
    
    // Check if we have pixel distribution data
    if (metrics.pixelDistribution) {
        // Create pixel distribution pie chart
        distributionChart = new Chart(distributionCtx, {
            type: 'pie',
            data: {
                labels: ['Low Values (0-85)', 'Mid Values (86-170)', 'High Values (171-255)'],
                datasets: [{
                    data: [
                        metrics.pixelDistribution.low, 
                        metrics.pixelDistribution.mid, 
                        metrics.pixelDistribution.high
                    ],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(255, 99, 132, 0.7)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    } else {
        // Display message when no distribution data is available
        distributionCtx.font = '16px Arial';
        distributionCtx.fillStyle = '#666';
        distributionCtx.textAlign = 'center';
        distributionCtx.fillText('No pixel distribution data available', distributionCtx.canvas.width/2, distributionCtx.canvas.height/2);
    }
}

// Helper function to download image
function downloadImage(dataUrl, filename) {
    const link = document.createElement('a');
    link.href = dataUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}