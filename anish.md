// main.js - Excel Data Visualizer

// Global variables
let uploadedFiles = [];
let currentGraphs = [];
let plotlyGraphs = {};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadUserFiles();
    setupGraphTypeOptions();
});

// Initialize all event listeners
function initializeEventListeners() {
    // File upload
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.getElementById('upload-btn');
    
    if (uploadBtn) {
        uploadBtn.addEventListener('click', () => fileInput.click());
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', handleFileUpload);
    }
    
    // Graph controls
    const plotBtn = document.getElementById('plot-btn');
    if (plotBtn) {
        plotBtn.addEventListener('click', plotGraph);
    }
    
    // Export buttons
    const exportPdfBtn = document.getElementById('export-pdf');
    const exportJpgBtn = document.getElementById('export-jpg');
    
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', () => exportGraph('pdf'));
    }
    
    if (exportJpgBtn) {
        exportJpgBtn.addEventListener('click', () => exportGraph('jpg'));
    }
    
    // Compare graphs button
    const compareBtn = document.getElementById('compare-btn');
    if (compareBtn) {
        compareBtn.addEventListener('click', compareGraphs);
    }
    
    // File selection change
    const fileSelect = document.getElementById('file-select');
    if (fileSelect) {
        fileSelect.addEventListener('change', handleFileSelection);
    }
    
    // Graph type change
    const graphType = document.getElementById('graph-type');
    if (graphType) {
        graphType.addEventListener('change', updateGraphOptions);
    }
}

// Handle file upload
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file type
    const validTypes = ['.xlsx', '.xls', '.csv'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    
    if (!validTypes.includes(fileExtension)) {
        showNotification('Please upload a valid Excel or CSV file', 'error');
        return;
    }
    
    // Show loading
    showLoading(true);
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/upload/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('File uploaded successfully!', 'success');
            uploadedFiles.push(data.file);
            updateFileList();
            populateFileSelect();
            
            // Auto-select the newly uploaded file
            document.getElementById('file-select').value = data.file.id;
            handleFileSelection();
        } else {
            showNotification(data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showNotification('Upload failed. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

// Handle file selection
async function handleFileSelection() {
    const fileSelect = document.getElementById('file-select');
    const selectedFileId = fileSelect.value;
    
    if (!selectedFileId) {
        clearSheetAndColumnSelects();
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`/get_file_data/${selectedFileId}/`, {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            populateSheetSelect(data.sheets);
            if (data.sheets.length > 0) {
                document.getElementById('sheet-select').value = data.sheets[0];
                await loadSheetColumns();
            }
        } else {
            showNotification('Failed to load file data', 'error');
        }
    } catch (error) {
        console.error('Error loading file data:', error);
        showNotification('Error loading file data', 'error');
    } finally {
        showLoading(false);
    }
}

// Load sheet columns
async function loadSheetColumns() {
    const fileId = document.getElementById('file-select').value;
    const sheetName = document.getElementById('sheet-select').value;
    
    if (!fileId || !sheetName) return;
    
    showLoading(true);
    
    try {
        const response = await fetch(`/get_columns/${fileId}/${encodeURIComponent(sheetName)}/`, {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            populateColumnSelects(data.columns);
        } else {
            showNotification('Failed to load columns', 'error');
        }
    } catch (error) {
        console.error('Error loading columns:', error);
        showNotification('Error loading columns', 'error');
    } finally {
        showLoading(false);
    }
}

// Plot graph
async function plotGraph() {
    const fileId = document.getElementById('file-select').value;
    const sheetName = document.getElementById('sheet-select').value;
    const graphType = document.getElementById('graph-type').value;
    const xColumn = document.getElementById('x-column').value;
    const yColumns = Array.from(document.getElementById('y-columns').selectedOptions)
                          .map(option => option.value);
    
    // Validation
    if (!fileId || !sheetName || !graphType || !xColumn || yColumns.length === 0) {
        showNotification('Please fill all required fields', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/plot_graph/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                file_id: fileId,
                sheet_name: sheetName,
                graph_type: graphType,
                x_column: xColumn,
                y_columns: yColumns
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            renderGraph(data.graph_data, data.graph_id);
            currentGraphs.push({
                id: data.graph_id,
                type: graphType,
                data: data.graph_data
            });
            updateGraphList();
            showNotification('Graph plotted successfully!', 'success');
        } else {
            showNotification(data.error || 'Failed to plot graph', 'error');
        }
    } catch (error) {
        console.error('Error plotting graph:', error);
        showNotification('Error plotting graph', 'error');
    } finally {
        showLoading(false);
    }
}

// Render graph using Plotly
function renderGraph(graphData, graphId, containerId = 'graph-container') {
    const container = document.getElementById(containerId);
    
    // Clear previous graph
    container.innerHTML = '';
    
    // Create graph div
    const graphDiv = document.createElement('div');
    graphDiv.id = `graph-${graphId}`;
    graphDiv.className = 'plotly-graph';
    container.appendChild(graphDiv);
    
    // Parse graph data if it's a string
    const plotData = typeof graphData === 'string' ? JSON.parse(graphData) : graphData;
    
    // Configure layout
    const layout = {
        ...plotData.layout,
        autosize: true,
        margin: { t: 50, r: 50, b: 50, l: 50 },
        hovermode: 'closest',
        showlegend: true,
        legend: {
            x: 1,
            xanchor: 'right',
            y: 1
        }
    };
    
    // Configure options
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToAdd: ['drawline', 'drawopenpath', 'eraseshape'],
        toImageButtonOptions: {
            format: 'png',
            filename: 'graph_export',
            height: 600,
            width: 800,
            scale: 1
        }
    };
    
    // Plot the graph
    Plotly.newPlot(graphDiv.id, plotData.data, layout, config);
    
    // Store reference
    plotlyGraphs[graphId] = {
        div: graphDiv.id,
        data: plotData.data,
        layout: layout
    };
}

// Compare multiple graphs
function compareGraphs() {
    const selectedGraphs = Array.from(document.querySelectorAll('.graph-checkbox:checked'))
                               .map(cb => cb.value);
    
    if (selectedGraphs.length < 2) {
        showNotification('Please select at least 2 graphs to compare', 'warning');
        return;
    }
    
    // Create comparison modal
    const modal = createComparisonModal();
    document.body.appendChild(modal);
    
    // Render selected graphs in grid
    const gridContainer = modal.querySelector('.comparison-grid');
    selectedGraphs.forEach((graphId, index) => {
        const graph = currentGraphs.find(g => g.id === graphId);
        if (graph) {
            const gridItem = document.createElement('div');
            gridItem.className = 'comparison-grid-item';
            gridItem.id = `compare-graph-${index}`;
            gridContainer.appendChild(gridItem);
            
            // Render graph in comparison view
            renderGraph(graph.data, `compare-${graphId}`, gridItem.id);
        }
    });
    
    // Show modal
    modal.style.display = 'block';
}

// Export graph
async function exportGraph(format) {
    const activeGraphId = getActiveGraphId();
    if (!activeGraphId) {
        showNotification('No graph to export', 'warning');
        return;
    }
    
    showLoading(true);
    
    try {
        const graphDiv = plotlyGraphs[activeGraphId].div;
        
        if (format === 'pdf') {
            // Export as PDF using Plotly and jsPDF
            Plotly.toImage(graphDiv, { format: 'png', width: 800, height: 600 })
                .then(function(dataUrl) {
                    const pdf = new jsPDF('l', 'mm', 'a4');
                    pdf.addImage(dataUrl, 'PNG', 10, 10, 280, 180);
                    pdf.save('graph_export.pdf');
                    showNotification('Graph exported as PDF', 'success');
                });
        } else if (format === 'jpg') {
            // Export as JPG
            Plotly.toImage(graphDiv, { format: 'jpeg', width: 800, height: 600 })
                .then(function(dataUrl) {
                    const link = document.createElement('a');
                    link.download = 'graph_export.jpg';
                    link.href = dataUrl;
                    link.click();
                    showNotification('Graph exported as JPG', 'success');
                });
        }
    } catch (error) {
        console.error('Export error:', error);
        showNotification('Export failed', 'error');
    } finally {
        showLoading(false);
    }
}

// Helper Functions

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Show loading indicator
function showLoading(show) {
    const loader = document.getElementById('loading-indicator');
    if (loader) {
        loader.style.display = show ? 'block' : 'none';
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Update file list display
function updateFileList() {
    const fileList = document.getElementById('file-list');
    if (!fileList) return;
    
    fileList.innerHTML = uploadedFiles.map(file => `
        <div class="file-item">
            <span class="file-name">${file.name}</span>
            <span class="file-date">${new Date(file.uploaded_at).toLocaleDateString()}</span>
            <button class="delete-btn" onclick="deleteFile(${file.id})">Delete</button>
        </div>
    `).join('');
}

// Populate dropdowns
function populateFileSelect() {
    const select = document.getElementById('file-select');
    select.innerHTML = '<option value="">Select a file</option>' +
        uploadedFiles.map(file => `<option value="${file.id}">${file.name}</option>`).join('');
}

function populateSheetSelect(sheets) {
    const select = document.getElementById('sheet-select');
    select.innerHTML = '<option value="">Select a sheet</option>' +
        sheets.map(sheet => `<option value="${sheet}">${sheet}</option>`).join('');
}

function populateColumnSelects(columns) {
    const xSelect = document.getElementById('x-column');
    const ySelect = document.getElementById('y-columns');
    
    const options = columns.map(col => `<option value="${col}">${col}</option>`).join('');
    
    xSelect.innerHTML = '<option value="">Select X axis</option>' + options;
    ySelect.innerHTML = options;
}

// Clear selections
function clearSheetAndColumnSelects() {
    document.getElementById('sheet-select').innerHTML = '<option value="">Select a sheet</option>';
    document.getElementById('x-column').innerHTML = '<option value="">Select X axis</option>';
    document.getElementById('y-columns').innerHTML = '';
}

// Get active graph ID
function getActiveGraphId() {
    return currentGraphs.length > 0 ? currentGraphs[currentGraphs.length - 1].id : null;
}

// Create comparison modal
function createComparisonModal() {
    const modal = document.createElement('div');
    modal.className = 'comparison-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close-modal" onclick="this.parentElement.parentElement.remove()">&times;</span>
            <h2>Graph Comparison</h2>
            <div class="comparison-grid"></div>
        </div>
    `;
    return modal;
}

// Update graph options based on type
function updateGraphOptions() {
    const graphType = document.getElementById('graph-type').value;
    const yColumnsSelect = document.getElementById('y-columns');
    
    // Enable/disable multiple selection based on graph type
    if (graphType === 'pie' || graphType === 'histogram') {
        yColumnsSelect.multiple
// main.js - Excel Data Visualizer

// Global variables
let uploadedFiles = [];
let currentGraphs = [];
let plotlyGraphs = {};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadUserFiles();
    setupGraphTypeOptions();
});

// Initialize all event listeners
function initializeEventListeners() {
    // File upload
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.getElementById('upload-btn');
    
    if (uploadBtn) {
        uploadBtn.addEventListener('click', () => fileInput.click());
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', handleFileUpload);
    }
    
    // Graph controls
    const plotBtn = document.getElementById('plot-btn');
    if (plotBtn) {
        plotBtn.addEventListener('click', plotGraph);
    }
    
    // Export buttons
    const exportPdfBtn = document.getElementById('export-pdf');
    const exportJpgBtn = document.getElementById('export-jpg');
    
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', () => exportGraph('pdf'));
    }
    
    if (exportJpgBtn) {
        exportJpgBtn.addEventListener('click', () => exportGraph('jpg'));
    }
    
    // Compare graphs button
    const compareBtn = document.getElementById('compare-btn');
    if (compareBtn) {
        compareBtn.addEventListener('click', compareGraphs);
    }
    
    // File selection change
    const fileSelect = document.getElementById('file-select');
    if (fileSelect) {
        fileSelect.addEventListener('change', handleFileSelection);
    }
    
    // Graph type change
    const graphType = document.getElementById('graph-type');
    if (graphType) {
        graphType.addEventListener('change', updateGraphOptions);
    }
}

// Handle file upload
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file type
    const validTypes = ['.xlsx', '.xls', '.csv'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    
    if (!validTypes.includes(fileExtension)) {
        showNotification('Please upload a valid Excel or CSV file', 'error');
        return;
    }
    
    // Show loading
    showLoading(true);
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/upload/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('File uploaded successfully!', 'success');
            uploadedFiles.push(data.file);
            updateFileList();
            populateFileSelect();
            
            // Auto-select the newly uploaded file
            document.getElementById('file-select').value = data.file.id;
            handleFileSelection();
        } else {
            showNotification(data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showNotification('Upload failed. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

// Handle file selection
async function handleFileSelection() {
    const fileSelect = document.getElementById('file-select');
    const selectedFileId = fileSelect.value;
    
    if (!selectedFileId) {
        clearSheetAndColumnSelects();
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`/get_file_data/${selectedFileId}/`, {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            populateSheetSelect(data.sheets);
            if (data.sheets.length > 0) {
                document.getElementById('sheet-select').value = data.sheets[0];
                await loadSheetColumns();
            }
        } else {
            showNotification('Failed to load file data', 'error');
        }
    } catch (error) {
        console.error('Error loading file data:', error);
        showNotification('Error loading file data', 'error');
    } finally {
        showLoading(false);
    }
}

// Load sheet columns
async function loadSheetColumns() {
    const fileId = document.getElementById('file-select').value;
    const sheetName = document.getElementById('sheet-select').value;
    
    if (!fileId || !sheetName) return;
    
    showLoading(true);
    
    try {
        const response = await fetch(`/get_columns/${fileId}/${encodeURIComponent(sheetName)}/`, {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            populateColumnSelects(data.columns);
        } else {
            showNotification('Failed to load columns', 'error');
        }
    } catch (error) {
        console.error('Error loading columns:', error);
        showNotification('Error loading columns', 'error');
    } finally {
        showLoading(false);
    }
}

// Plot graph
async function plotGraph() {
    const fileId = document.getElementById('file-select').value;
    const sheetName = document.getElementById('sheet-select').value;
    const graphType = document.getElementById('graph-type').value;
    const xColumn = document.getElementById('x-column').value;
    const yColumns = Array.from(document.getElementById('y-columns').selectedOptions)
                          .map(option => option.value);
    
    // Validation
    if (!fileId || !sheetName || !graphType || !xColumn || yColumns.length === 0) {
        showNotification('Please fill all required fields', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/plot_graph/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                file_id: fileId,
                sheet_name: sheetName,
                graph_type: graphType,
                x_column: xColumn,
                y_columns: yColumns
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            renderGraph(data.graph_data, data.graph_id);
            currentGraphs.push({
                id: data.graph_id,
                type: graphType,
                data: data.graph_data
            });
            updateGraphList();
            showNotification('Graph plotted successfully!', 'success');
        } else {
            showNotification(data.error || 'Failed to plot graph', 'error');
        }
    } catch (error) {
        console.error('Error plotting graph:', error);
        showNotification('Error plotting graph', 'error');
    } finally {
        showLoading(false);
    }
}

// Render graph using Plotly
function renderGraph(graphData, graphId, containerId = 'graph-container') {
    const container = document.getElementById(containerId);
    
    // Clear previous graph
    container.innerHTML = '';
    
    // Create graph div
    const graphDiv = document.createElement('div');
    graphDiv.id = `graph-${graphId}`;
    graphDiv.className = 'plotly-graph';
    container.appendChild(graphDiv);
    
    // Parse graph data if it's a string
    const plotData = typeof graphData === 'string' ? JSON.parse(graphData) : graphData;
    
    // Configure layout
    const layout = {
        ...plotData.layout,
        autosize: true,
        margin: { t: 50, r: 50, b: 50, l: 50 },
        hovermode: 'closest',
        showlegend: true,
        legend: {
            x: 1,
            xanchor: 'right',
            y: 1
        }
    };
    
    // Configure options
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToAdd: ['drawline', 'drawopenpath', 'eraseshape'],
        toImageButtonOptions: {
            format: 'png',
            filename: 'graph_export',
            height: 600,
            width: 800,
            scale: 1
        }
    };
    
    // Plot the graph
    Plotly.newPlot(graphDiv.id, plotData.data, layout, config);
    
    // Store reference
    plotlyGraphs[graphId] = {
        div: graphDiv.id,
        data: plotData.data,
        layout: layout
    };
}

// Compare multiple graphs
function compareGraphs() {
    const selectedGraphs = Array.from(document.querySelectorAll('.graph-checkbox:checked'))
                               .map(cb => cb.value);
    
    if (selectedGraphs.length < 2) {
        showNotification('Please select at least 2 graphs to compare', 'warning');
        return;
    }
    
    // Create comparison modal
    const modal = createComparisonModal();
    document.body.appendChild(modal);
    
    // Render selected graphs in grid
    const gridContainer = modal.querySelector('.comparison-grid');
    selectedGraphs.forEach((graphId, index) => {
        const graph = currentGraphs.find(g => g.id === graphId);
        if (graph) {
            const gridItem = document.createElement('div');
            gridItem.className = 'comparison-grid-item';
            gridItem.id = `compare-graph-${index}`;
            gridContainer.appendChild(gridItem);
            
            // Render graph in comparison view
            renderGraph(graph.data, `compare-${graphId}`, gridItem.id);
        }
    });
    
    // Show modal
    modal.style.display = 'block';
}

// Export graph
async function exportGraph(format) {
    const activeGraphId = getActiveGraphId();
    if (!activeGraphId) {
        showNotification('No graph to export', 'warning');
        return;
    }
    
    showLoading(true);
    
    try {
        const graphDiv = plotlyGraphs[activeGraphId].div;
        
        if (format === 'pdf') {
            // Export as PDF using Plotly and jsPDF
            Plotly.toImage(graphDiv, { format: 'png', width: 800, height: 600 })
                .then(function(dataUrl) {
                    const pdf = new jsPDF('l', 'mm', 'a4');
                    pdf.addImage(dataUrl, 'PNG', 10, 10, 280, 180);
                    pdf.save('graph_export.pdf');
                    showNotification('Graph exported as PDF', 'success');
                });
        } else if (format === 'jpg') {
            // Export as JPG
            Plotly.toImage(graphDiv, { format: 'jpeg', width: 800, height: 600 })
                .then(function(dataUrl) {
                    const link = document.createElement('a');
                    link.download = 'graph_export.jpg';
                    link.href = dataUrl;
                    link.click();
                    showNotification('Graph exported as JPG', 'success');
                });
        }
    } catch (error) {
        console.error('Export error:', error);
        showNotification('Export failed', 'error');
    } finally {
        showLoading(false);
    }
}

// Helper Functions

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Show loading indicator
function showLoading(show) {
    const loader = document.getElementById('loading-indicator');
    if (loader) {
        loader.style.display = show ? 'block' : 'none';
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Update file list display
function updateFileList() {
    const fileList = document.getElementById('file-list');
    if (!fileList) return;
    
    fileList.innerHTML = uploadedFiles.map(file => `
        <div class="file-item">
            <span class="file-name">${file.name}</span>
            <span class="file-date">${new Date(file.uploaded_at).toLocaleDateString()}</span>
            <button class="delete-btn" onclick="deleteFile(${file.id})">Delete</button>
        </div>
    `).join('');
}

// Populate dropdowns
function populateFileSelect() {
    const select = document.getElementById('file-select');
    select.innerHTML = '<option value="">Select a file</option>' +
        uploadedFiles.map(file => `<option value="${file.id}">${file.name}</option>`).join('');
}

function populateSheetSelect(sheets) {
    const select = document.getElementById('sheet-select');
    select.innerHTML = '<option value="">Select a sheet</option>' +
        sheets.map(sheet => `<option value="${sheet}">${sheet}</option>`).join('');
}

function populateColumnSelects(columns) {
    const xSelect = document.getElementById('x-column');
    const ySelect = document.getElementById('y-columns');
    
    const options = columns.map(col => `<option value="${col}">${col}</option>`).join('');
    
    xSelect.innerHTML = '<option value="">Select X axis</option>' + options;
    ySelect.innerHTML = options;
}

// Clear selections
function clearSheetAndColumnSelects() {
    document.getElementById('sheet-select').innerHTML = '<option value="">Select a sheet</option>';
    document.getElementById('x-column').innerHTML = '<option value="">Select X axis</option>';
    document.getElementById('y-columns').innerHTML = '';
}

// Get active graph ID
function getActiveGraphId() {
    return currentGraphs.length > 0 ? currentGraphs[currentGraphs.length - 1].id : null;
}

// Create comparison modal
function createComparisonModal() {
    const modal = document.createElement('div');
    modal.className = 'comparison-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close-modal" onclick="this.parentElement.parentElement.remove()">&times;</span>
            <h2>Graph Comparison</h2>
            <div class="comparison-grid"></div>
        </div>
    `;
    return modal;
}

// Update graph options based on type
function updateGraphOptions() {
    const graphType = document.getElementById('graph-type').value;
    const yColumnsSelect = document.getElementById('y-columns');
    
    // Enable/disable multiple selection based on graph type
    if (graphType === 'pie' || graphType === 'histogram') {
        yColumnsSelect.multiple