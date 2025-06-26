// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const fileSelect = document.getElementById('fileSelect');
    const sheetSelect = document.getElementById('sheetSelect');
    const xAxisSelect = document.getElementById('xAxisSelect');
    const yAxisContainer = document.getElementById('yAxisContainer');
    const graphType = document.getElementById('graphType');
    const plotBtn = document.getElementById('plotBtn');
    const addToComparisonBtn = document.getElementById('addToComparisonBtn');
    const compareBtn = document.getElementById('compareBtn');
    const clearComparisonBtn = document.getElementById('clearComparisonBtn');
    const comparisonCount = document.getElementById('comparisonCount');
    const comparisonListCard = document.getElementById('comparisonListCard');
    const comparisonList = document.getElementById('comparisonList');
    const exportCard = document.getElementById('exportCard');
    const exportPDF = document.getElementById('exportPDF');
    const exportJPG = document.getElementById('exportJPG');
    const graphContainer = document.getElementById('graphContainer');

    let currentFigure = null;
    let currentGraphData = null;
    let comparisonGraphs = [];

    // Utility: Show alert
    function showAlert(message, type) {
        document.querySelectorAll('.alert').forEach(a => a.remove());
        const icon = type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : 'times-circle';
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.style.animation = 'fadeIn 0.5s';
        alertDiv.innerHTML = `
            <i class="fas fa-${icon}"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('main').prepend(alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
    }

    // Utility: Reset form
    function resetForm() {
        sheetSelect.innerHTML = '<option value="">Choose sheet...</option>';
        sheetSelect.disabled = true;
        xAxisSelect.innerHTML = '<option value="">Select X-axis parameter...</option>';
        xAxisSelect.disabled = true;
        yAxisContainer.innerHTML = '<p class="text-muted small">Select sheet first</p>';
        plotBtn.disabled = true;
        addToComparisonBtn.disabled = true;
        exportCard.style.display = 'none';
        graphContainer.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="fas fa-chart-bar fa-5x mb-3"></i>
                <p>Select data parameters to generate graph</p>
            </div>
        `;
    }

    // Utility: Check form validity and enable/disable buttons
    function checkFormValidity() {
        const xSelected = xAxisSelect.value;
        const ySelected = yAxisContainer.querySelectorAll('input:checked').length > 0;
        const isValid = xSelected && ySelected;
        plotBtn.disabled = !isValid;
        addToComparisonBtn.disabled = !isValid;
    }

    // File selection change
    fileSelect.addEventListener('change', async function() {
        const fileId = this.value;
        if (fileId) {
            sheetSelect.innerHTML = '<option value="">Loading sheets...</option>';
            sheetSelect.disabled = false;
            xAxisSelect.innerHTML = '<option value="">Select sheet first</option>';
            xAxisSelect.disabled = true;
            yAxisContainer.innerHTML = '<p class="text-muted small">Select sheet first</p>';
            plotBtn.disabled = true;
            addToComparisonBtn.disabled = true;
            exportCard.style.display = 'none';
            try {
                const response = await fetch(`/api/sheets/?file_id=${fileId}`);
                if (!response.ok) throw new Error('Could not load sheets');
                const data = await response.json();
                sheetSelect.innerHTML = '<option value="">Choose sheet...</option>';
                (data.sheets || []).forEach(sheet => {
                    const option = document.createElement('option');
                    option.value = sheet;
                    option.textContent = sheet;
                    sheetSelect.appendChild(option);
                });
            } catch (error) {
                showAlert('Error loading sheets', 'danger');
                resetForm();
            }
        } else {
            resetForm();
        }
    });

    // Sheet selection change
    sheetSelect.addEventListener('change', async function() {
        const fileId = fileSelect.value;
        const sheetName = this.value;
        if (fileId && sheetName) {
            try {
                const response = await fetch(`/api/columns/?file_id=${fileId}&sheet_name=${sheetName}`);
                if (!response.ok) throw new Error('Could not load columns');
                const data = await response.json();
                xAxisSelect.disabled = false;
                xAxisSelect.innerHTML = '<option value="">Select X-axis parameter...</option>';
                (data.x_columns || []).forEach(col => {
                    const option = document.createElement('option');
                    option.value = col;
                    option.textContent = col;
                    xAxisSelect.appendChild(option);
                });
                yAxisContainer.innerHTML = '';
                if (data.y_columns && data.y_columns.length > 0) {
                    yAxisContainer.innerHTML = '<p class="text-muted small mb-2">Select Y-axis parameters:</p>';
                    data.y_columns.forEach(col => {
                        const checkDiv = document.createElement('div');
                        checkDiv.className = 'form-check';
                        checkDiv.innerHTML = `
                            <input class="form-check-input" type="checkbox" value="${col}" id="y_${col}">
                            <label class="form-check-label" for="y_${col}">${col}</label>
                        `;
                        yAxisContainer.appendChild(checkDiv);
                    });
                } else {
                    yAxisContainer.innerHTML = '<p class="text-muted small">No Y-axis columns available</p>';
                }
                plotBtn.disabled = true;
                addToComparisonBtn.disabled = true;
            } catch (error) {
                showAlert('Error loading columns', 'danger');
                xAxisSelect.disabled = true;
                yAxisContainer.innerHTML = '<p class="text-muted small">No columns available</p>';
            }
        }
    });

    // X-axis change
    xAxisSelect.addEventListener('change', checkFormValidity);

    // Y-axis checkbox change (event delegation)
    yAxisContainer.addEventListener('change', function(e) {
        if (e.target.matches('input[type="checkbox"]')) {
            checkFormValidity();
        }
    });

    // Plot button click
    plotBtn.addEventListener('click', function() {
        plotGraph(false);
    });

    // Add to comparison button click
    addToComparisonBtn.addEventListener('click', function() {
        plotGraph(true);
    });

    // Plot graph function
    async function plotGraph(addToComparison = false) {
        const fileId = fileSelect.value;
        const fileName = fileSelect.options[fileSelect.selectedIndex].text;
        const sheetName = sheetSelect.value;
        const xColumn = xAxisSelect.value;
        const yColumns = Array.from(yAxisContainer.querySelectorAll('input:checked')).map(input => input.value);
        const plotType = graphType.value;

        if (!fileId || !sheetName || !xColumn || yColumns.length === 0) {
            showAlert('Please select all parameters.', 'warning');
            return;
        }

        currentGraphData = {
            file_id: fileId,
            file_name: fileName,
            sheet_name: sheetName,
            x_column: xColumn,
            y_columns: yColumns,
            plot_type: plotType
        };

        graphContainer.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3">Generating graph...</p>
            </div>
        `;

        try {
            const response = await fetch('/api/plot/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(currentGraphData)
            });
            const data = await response.json();

            if (data.figure) {
                currentFigure = data.figure;
                const fig = JSON.parse(data.figure);
                Plotly.newPlot('graphContainer', fig.data, fig.layout, {
                    responsive: true,
                    displayModeBar: true,
                    displaylogo: false,
                    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
                });
                exportCard.style.display = 'block';

                if (addToComparison) {
                    const graphId = Date.now();
                    comparisonGraphs.push({
                        id: graphId,
                        ...currentGraphData,
                        figure: data.figure
                    });
                    updateComparisonUI();
                    showAlert('Graph added to comparison!', 'success');
                } else {
                    showAlert('Graph generated successfully!', 'success');
                }
            } else {
                showAlert('No figure received from server!', 'danger');
            }
        } catch (error) {
            showAlert('Error generating graph', 'danger');
            graphContainer.innerHTML = `<div class="text-center text-muted py-5">
                <i class="fas fa-exclamation-triangle fa-5x mb-3"></i>
                <p>Error generating graph. Please try again.</p>
            </div>`;
        }
    }

    // Update comparison UI
    function updateComparisonUI() {
        comparisonCount.textContent = comparisonGraphs.length;
        compareBtn.disabled = comparisonGraphs.length < 2;
        if (comparisonGraphs.length > 0) {
            comparisonListCard.style.display = 'block';
            clearComparisonBtn.style.display = 'inline-block';
            comparisonList.innerHTML = '';
            comparisonGraphs.forEach((graph, index) => {
                const graphDiv = document.createElement('div');
                graphDiv.className = 'd-flex justify-content-between align-items-center mb-2 p-2 border rounded';
                graphDiv.innerHTML = `
                    <div>
                        <strong>${index + 1}.</strong> ${graph.file_name} - ${graph.sheet_name}
                        <br>
                        <small class="text-muted">X: ${graph.x_column}, Y: ${graph.y_columns.join(', ')}</small>
                    </div>
                    <button class="btn btn-sm btn-danger remove-comp-graph" data-id="${graph.id}">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                comparisonList.appendChild(graphDiv);
            });
        } else {
            comparisonListCard.style.display = 'none';
            clearComparisonBtn.style.display = 'none';
        }
    }

    // Remove from comparison (event delegation)
    comparisonList.addEventListener('click', function(e) {
        if (e.target.closest('.remove-comp-graph')) {
            const id = Number(e.target.closest('.remove-comp-graph').getAttribute('data-id'));
            comparisonGraphs = comparisonGraphs.filter(g => g.id !== id);
            updateComparisonUI();
            showAlert('Graph removed from comparison', 'info');
        }
    });

    // Clear comparison
    clearComparisonBtn.addEventListener('click', function() {
        if (confirm('Clear all graphs from comparison?')) {
            comparisonGraphs = [];
            updateComparisonUI();
            showAlert('Comparison cleared', 'info');
        }
    });

    // Compare button click
    compareBtn.addEventListener('click', function() {
        if (comparisonGraphs.length < 2) {
            showAlert('Please add at least 2 graphs to compare', 'warning');
            return;
        }
        graphContainer.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3">Generating comparison graph...</p>
            </div>
        `;
        try {
            const traces = [];
            const colorPalettes = [
                ['#FF6B35', '#FF8C61', '#FFAD8D'],
                ['#00A9E0', '#33BAE8', '#66CBF0'],
                ['#84BD00', '#A3CC33', '#C2DB66'],
                ['#FFD100', '#FFDB33', '#FFE566'],
                ['#7C878E', '#969FA5', '#B0B8BC']
            ];
            comparisonGraphs.forEach((graph, graphIndex) => {
                const fig = JSON.parse(graph.figure);
                const colors = colorPalettes[graphIndex % colorPalettes.length];
                fig.data.forEach((trace, traceIndex) => {
                    trace.name = `${graph.file_name} (${graph.sheet_name}) - ${trace.name || graph.y_columns[traceIndex]}`;
                    const color = colors[traceIndex % colors.length];
                    if (trace.line) trace.line.color = color;
                    if (trace.marker) Object.assign(trace.marker, { color, opacity: 0.8 });
                    if (trace.line) trace.line.width = 2;
                    traces.push(trace);
                });
            });
            const layout = {
                title: `Comparison of ${comparisonGraphs.length} Graphs`,
                xaxis: { title: 'X-Axis', showgrid: true, gridcolor: '#E0E0E0' },
                yaxis: { title: 'Values', showgrid: true, gridcolor: '#E0E0E0' },
                hovermode: 'x unified',
                template: 'plotly_white',
                showlegend: true,
                legend: {
                    orientation: 'v',
                    yanchor: 'top',
                    y: 0.99,
                    xanchor: 'left',
                    x: 1.01,
                    bgcolor: 'rgba(255,255,255,0.8)',
                    bordercolor: '#E0E0E0',
                    borderwidth: 1,
                    font: { size: 10 }
                },
                margin: { l: 80, r: 250, t: 80, b: 80 }
            };
            const config = {
                responsive: true,
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
            };
            Plotly.newPlot('graphContainer', traces, layout, config);
            currentFigure = JSON.stringify({data: traces, layout: layout});
            exportCard.style.display = 'block';
            showAlert(`Comparison graph with ${comparisonGraphs.length} datasets generated successfully!`, 'success');
        } catch (error) {
            showAlert('Error generating comparison graph', 'danger');
            graphContainer.innerHTML = `<div class="text-center text-muted py-5">
                <i class="fas fa-exclamation-triangle fa-5x mb-3"></i>
                <p>Error generating comparison. Please try again.</p>
            </div>`;
        }
    });

    // Export PDF
    exportPDF.addEventListener('click', async function() {
        if (!currentFigure) return;
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exporting...';
        try {
            const response = await fetch('/api/export/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ figure: currentFigure, format: 'pdf' })
            });
            if (!response.ok) throw new Error('Export failed');
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'graph.pdf';
            a.click();
            window.URL.revokeObjectURL(url);
            showAlert('PDF exported successfully!', 'success');
        } catch (error) {
            showAlert('Error exporting PDF', 'danger');
        } finally {
            this.disabled = false;
            this.innerHTML = '<i class="fas fa-file-pdf"></i> Export as PDF';
        }
    });

    // Export JPG
    exportJPG.addEventListener('click', async function() {
        if (!currentFigure) return;
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exporting...';
        try {
            const response = await fetch('/api/export/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ figure: currentFigure, format: 'jpg' })
            });
            if (!response.ok) throw new Error('Export failed');
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'graph.jpg';
            a.click();
            window.URL.revokeObjectURL(url);
            showAlert('JPG exported successfully!', 'success');
        } catch (error) {
            showAlert('Error exporting JPG', 'danger');
        } finally {
            this.disabled = false;
            this.innerHTML = '<i class="fas fa-file-image"></i> Export as JPG';
        }
    });

    // Initialize if file_id is in URL
    if (fileSelect.value) {
        fileSelect.dispatchEvent(new Event('change'));
    }

    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});