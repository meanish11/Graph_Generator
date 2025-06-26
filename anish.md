document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const el = id => document.getElementById(id);

    const fileSelect = el('fileSelect');
    const sheetSelect = el('sheetSelect');
    const xAxisSelect = el('xAxisSelect');
    const yAxisContainer = el('yAxisContainer');
    const graphType = el('graphType');
    const plotBtn = el('plotBtn');
    const addToComparisonBtn = el('addToComparisonBtn');
    const compareBtn = el('compareBtn');
    const clearComparisonBtn = el('clearComparisonBtn');
    const comparisonCount = el('comparisonCount');
    const comparisonListCard = el('comparisonListCard');
    const comparisonList = el('comparisonList');
    const exportCard = el('exportCard');
    const exportPDF = el('exportPDF');
    const exportJPG = el('exportJPG');
    const graphContainer = el('graphContainer');

    let currentFigure = null, currentGraphData = null, comparisonGraphs = [];

    // Helper: fetch & JSON
    async function fetchJSON(url, options) {
        const res = await fetch(url, options);
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    // Helper: create element
    function create(tag, props = {}, ...children) {
        const elem = document.createElement(tag);
        Object.entries(props).forEach(([k, v]) => {
            if (k === "class") elem.className = v;
            else if (k.startsWith("on")) elem.addEventListener(k.slice(2).toLowerCase(), v);
            else elem[k] = v;
        });
        children.forEach(child => elem.append(child));
        return elem;
    }

    // UI: show alert
    function showAlert(message, type) {
        document.querySelectorAll('.alert').forEach(a => a.remove());
        const icon = type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : 'times-circle';
        const alertDiv = create('div', { class: `alert alert-${type} alert-dismissible fade show`, style: 'animation: fadeIn 0.5s' },
            create('i', { class: `fas fa-${icon}` }), ' ', message,
            create('button', { type: 'button', class: 'btn-close', 'data-bs-dismiss': 'alert' })
        );
        document.querySelector('main').prepend(alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
    }

    // UI: reset form
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
            </div>`;
    }

    // UI: check form validity
    function checkFormValidity() {
        const xSelected = xAxisSelect.value;
        const ySelected = yAxisContainer.querySelectorAll('input:checked').length > 0;
        plotBtn.disabled = addToComparisonBtn.disabled = !(xSelected && ySelected);
    }

    // UI: update comparison list
    function updateComparisonUI() {
        comparisonCount.textContent = comparisonGraphs.length;
        compareBtn.disabled = comparisonGraphs.length < 2;
        comparisonListCard.style.display = comparisonGraphs.length ? 'block' : 'none';
        clearComparisonBtn.style.display = comparisonGraphs.length ? 'inline-block' : 'none';
        comparisonList.innerHTML = '';
        comparisonGraphs.forEach((g, i) => {
            comparisonList.append(
                create('div', { class: 'd-flex justify-content-between align-items-center mb-2 p-2 border rounded' },
                    create('div', {},
                        create('strong', {}, `${i + 1}. `), `${g.file_name} - ${g.sheet_name}`,
                        create('br'), create('small', { class: 'text-muted' }, `X: ${g.x_column}, Y: ${g.y_columns.join(', ')}`)
                    ),
                    create('button', {
                        class: 'btn btn-sm btn-danger',
                        'data-id': g.id,
                        onclick: () => {
                            comparisonGraphs = comparisonGraphs.filter(x => x.id !== g.id);
                            updateComparisonUI();
                            showAlert('Graph removed from comparison', 'info');
                        }
                    }, create('i', { class: 'fas fa-times' }))
                )
            );
        });
    }

    // Populate sheet and column selectors
    fileSelect.addEventListener('change', async function() {
        const fileId = this.value;
        if (!fileId) return resetForm();
        sheetSelect.innerHTML = '<option>Loading sheets...</option>';
        sheetSelect.disabled = false;
        xAxisSelect.innerHTML = '<option>Select sheet first</option>';
        xAxisSelect.disabled = true;
        yAxisContainer.innerHTML = '<p class="text-muted small">Select sheet first</p>';
        plotBtn.disabled = addToComparisonBtn.disabled = true;
        exportCard.style.display = 'none';
        try {
            const data = await fetchJSON(`/api/sheets/?file_id=${fileId}`);
            sheetSelect.innerHTML = '<option value="">Choose sheet...</option>' +
                data.sheets.map(s => `<option value="${s}">${s}</option>`).join('');
        } catch (err) {
            showAlert('Error loading sheets', 'danger');
        }
    });

    sheetSelect.addEventListener('change', async function() {
        const fileId = fileSelect.value, sheetName = this.value;
        if (!(fileId && sheetName)) return;
        try {
            const data = await fetchJSON(`/api/columns/?file_id=${fileId}&sheet_name=${sheetName}`);
            xAxisSelect.disabled = false;
            xAxisSelect.innerHTML = '<option value="">Select X-axis parameter...</option>' +
                (data.x_columns || []).map(c => `<option value="${c}">${c}</option>`).join('');
            yAxisContainer.innerHTML = '';
            if (data.y_columns && data.y_columns.length) {
                yAxisContainer.append(create('p', { class: 'text-muted small mb-2' }, 'Select Y-axis parameters:'));
                data.y_columns.forEach(col => {
                    yAxisContainer.append(
                        create('div', { class: 'form-check' },
                            create('input', {
                                class: 'form-check-input',
                                type: 'checkbox',
                                value: col,
                                id: `y_${col}`,
                                onchange: checkFormValidity
                            }),
                            create('label', { class: 'form-check-label', htmlFor: `y_${col}` }, col)
                        )
                    );
                });
            } else {
                yAxisContainer.innerHTML = '<p class="text-muted small">No Y-axis columns available</p>';
            }
            plotBtn.disabled = addToComparisonBtn.disabled = true;
        } catch (err) {
            showAlert('Error loading columns', 'danger');
        }
    });

    xAxisSelect.addEventListener('change', checkFormValidity);

    // Plot & compare logic
    async function plotGraph(addToComparison = false) {
        const fileId = fileSelect.value,
            fileName = fileSelect.options[fileSelect.selectedIndex].text,
            sheetName = sheetSelect.value,
            xColumn = xAxisSelect.value,
            yColumns = Array.from(yAxisContainer.querySelectorAll('input:checked')).map(i => i.value),
            plotType = graphType.value;

        currentGraphData = { file_id: fileId, file_name: fileName, sheet_name: sheetName, x_column: xColumn, y_columns: yColumns, plot_type: plotType };

        graphContainer.innerHTML = `<div class="text-center py-5"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-3">Generating graph...</p></div>`;
        try {
            const data = await fetchJSON('/api/plot/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(currentGraphData) });
            if (data.figure) {
                currentFigure = data.figure;
                const fig = JSON.parse(data.figure);
                Plotly.newPlot('graphContainer', fig.data, fig.layout, {
                    responsive: true, displayModeBar: true, displaylogo: false,
                    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
                });
                exportCard.style.display = 'block';
                if (addToComparison) {
                    comparisonGraphs.push({ id: Date.now(), ...currentGraphData, figure: data.figure });
                    updateComparisonUI();
                    showAlert('Graph added to comparison!', 'success');
                } else {
                    showAlert('Graph generated successfully!', 'success');
                }
            }
        } catch (err) {
            showAlert('Error generating graph', 'danger');
            graphContainer.innerHTML = `<div class="text-center text-muted py-5"><i class="fas fa-exclamation-triangle fa-5x mb-3"></i><p>Error generating graph. Please try again.</p></div>`;
        }
    }

    plotBtn.addEventListener('click', () => plotGraph(false));
    addToComparisonBtn.addEventListener('click', () => plotGraph(true));

    // Comparison graph
    compareBtn.addEventListener('click', function() {
        if (comparisonGraphs.length < 2) return showAlert('Please add at least 2 graphs to compare', 'warning');
        graphContainer.innerHTML = `<div class="text-center py-5"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-3">Generating comparison graph...</p></div>`;
        try {
            const traces = [];
            const colorPalettes = [
                ['#FF6B35', '#FF8C61', '#FFAD8D'], ['#00A9E0', '#33BAE8', '#66CBF0'], ['#84BD00', '#A3CC33', '#C2DB66'],
                ['#FFD100', '#FFDB33', '#FFE566'], ['#7C878E', '#969FA5', '#B0B8BC']
            ];
            comparisonGraphs.forEach((graph, gi) => {
                const fig = JSON.parse(graph.figure), colors = colorPalettes[gi % colorPalettes.length];
                fig.data.forEach((trace, ti) => {
                    trace.name = `${graph.file_name} (${graph.sheet_name}) - ${trace.name || graph.y_columns[ti]}`;
                    const color = colors[ti % colors.length];
                    if (trace.line) Object.assign(trace.line, { color, width: 2 });
                    if (trace.marker) Object.assign(trace.marker, { color, opacity: 0.8 });
                    traces.push(trace);
                });
            });
            const layout = {
                title: `Comparison of ${comparisonGraphs.length} Graphs`,
                xaxis: { title: 'X-Axis', showgrid: true, gridcolor: '#E0E0E0' },
                yaxis: { title: 'Values', showgrid: true, gridcolor: '#E0E0E0' },
                hovermode: 'x unified', template: 'plotly_white', showlegend: true,
                legend: { orientation: 'v', yanchor: 'top', y: 0.99, xanchor: 'left', x: 1.01, bgcolor: 'rgba(255,255,255,0.8)', bordercolor: '#E0E0E0', borderwidth: 1, font: { size: 10 } },
                margin: { l: 80, r: 250, t: 80, b: 80 }
            };
            Plotly.newPlot('graphContainer', traces, layout, { responsive: true, displayModeBar: true, displaylogo: false, modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'] });
            currentFigure = JSON.stringify({ data: traces, layout });
            exportCard.style.display = 'block';
            showAlert(`Comparison graph with ${comparisonGraphs.length} datasets generated successfully!`, 'success');
        } catch (err) {
            showAlert('Error generating comparison graph', 'danger');
            graphContainer.innerHTML = `<div class="text-center text-muted py-5"><i class="fas fa-exclamation-triangle fa-5x mb-3"></i><p>Error generating comparison. Please try again.</p></div>`;
        }
    });

    // Export (PDF/JPG)
    function exportGraph(format, btn, icon, filename) {
        if (!currentFigure) return;
        btn.disabled = true;
        btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Exporting...`;
        fetch('/api/export/', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ figure: currentFigure, format })
        })
        .then(res => {
            if (!res.ok) throw new Error('Export failed');
            return res.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob), a = document.createElement('a');
            a.href = url; a.download = filename;
            a.click(); window.URL.revokeObjectURL(url);
            showAlert(`${format.toUpperCase()} exported successfully!`, 'success');
        })
        .catch(() => showAlert(`Error exporting ${format.toUpperCase()}`, 'danger'))
        .finally(() => {
            btn.disabled = false;
            btn.innerHTML = `<i class="fas fa-file-${icon}"></i> Export as ${format.toUpperCase()}`;
        });
    }
    exportPDF.addEventListener('click', function() { exportGraph('pdf', this, 'pdf', 'graph.pdf'); });
    exportJPG.addEventListener('click', function() { exportGraph('jpg', this, 'image', 'graph.jpg'); });

    clearComparisonBtn.addEventListener('click', function() {
        if (confirm('Clear all graphs from comparison?')) {
            comparisonGraphs = [];
            updateComparisonUI();
            showAlert('Comparison cleared', 'info');
        }
    });

    // Initialize if file_id is in URL
    if (fileSelect.value) fileSelect.dispatchEvent(new Event('change'));
    [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]')).map(el => new bootstrap.Tooltip(el));
});