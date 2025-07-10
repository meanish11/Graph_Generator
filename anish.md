Sure! Here's the complete and clean version of both files:


---

✅ index.html

Path: data_analyzer/templates/data_analyzer/index.html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Graph Comparator</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{% static 'data_analyzer/style.css' %}" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-4">
        <h2 class="text-center mb-4">Graph Comparator</h2>

        <button id="add-block" class="btn btn-primary mb-3">➕ Add Comparison</button>
        <div id="blocks-container"></div>

        <div class="row mb-3">
            <div class="col-md-4">
                <label class="form-label">Graph Type</label>
                <select id="graph-type" class="form-select">
                    <option value="line">Line</option>
                    <option value="bar">Bar</option>
                    <option value="scatter">Scatter</option>
                </select>
            </div>
            <div class="col-md-4">
                <label class="form-label">Y-axis Scale</label><br>
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="yaxis" value="linear" checked> Linear
                </div>
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="yaxis" value="log"> Logarithmic
                </div>
            </div>
            <div class="col-md-4 text-end">
                <label class="form-label">Export Options</label><br>
                <div class="btn-group">
                    <button class="btn btn-secondary" onclick="exportGraph('png')">Export PNG</button>
                    <button class="btn btn-dark" onclick="exportGraph('pdf')">Export PDF</button>
                    <button class="btn btn-info" onclick="exportData()">Export Data</button>
                </div>
            </div>
        </div>

        <button class="btn btn-success mb-3" onclick="plotGraph()">📊 Plot Graph</button>
        <div id="plot" class="mb-4"></div>
        <div id="status" class="text-success fw-bold"></div>
    </div>

    <script>
        let counter = 0;
        const files = {{ files|safe }};

        document.getElementById("add-block").addEventListener("click", () => addBlock(counter++));

        function addBlock(id) {
            const block = document.createElement("div");
            block.className = "graph-block";
            block.id = `block-${id}`;
            block.innerHTML = `
                <div class="row mb-2">
                    <div class="col-md-5">
                        <label class="form-label">File</label>
                        <select class="form-select file-select" data-id="${id}" onchange="loadColumns(${id})">
                            <option value="">Select</option>
                            ${files.map(f => `<option value="${f}">${f}</option>`).join('')}
                        </select>
                    </div>
                    <div class="col-md-5">
                        <label class="form-label">Y-axis Column</label>
                        <select class="form-select y-col" data-id="${id}"></select>
                    </div>
                    <div class="col-md-2 d-flex align-items-end">
                        <button class="btn btn-danger" onclick="removeBlock(${id})">❌</button>
                    </div>
                </div>
                <div class="mb-2">
                    <label class="form-label">Graph Label</label>
                    <input class="form-control label-input" data-id="${id}" value="Graph ${id + 1}">
                    <div class="form-text" id="info-${id}"></div>
                </div>
            `;
            document.getElementById("blocks-container").appendChild(block);
        }

        function removeBlock(id) {
            document.getElementById(`block-${id}`)?.remove();
        }

        function loadColumns(id) {
            const file = document.querySelector(`.file-select[data-id="${id}"]`).value;
            fetch(`/get_columns/?file=${file}`)
                .then(res => res.json())
                .then(data => {
                    const select = document.querySelector(`.y-col[data-id="${id}"]`);
                    select.innerHTML = data.columns.map(col => `<option value="${col}">${col}</option>`).join('');
                    document.getElementById(`info-${id}`).innerText = `Size computed from: ${data.size_info}`;
                });
        }

        function plotGraph() {
            const graphType = document.getElementById("graph-type").value;
            const yaxisScale = document.querySelector('input[name="yaxis"]:checked').value;
            const blocks = document.querySelectorAll(".graph-block");

            const files = [], y_cols = [], labels = [];

            blocks.forEach(block => {
                const id = block.id.split("-")[1];
                files.push(block.querySelector(`.file-select[data-id="${id}"]`).value);
                y_cols.push(block.querySelector(`.y-col[data-id="${id}"]`).value);
                labels.push(block.querySelector(`.label-input[data-id="${id}"]`).value);
            });

            fetch("/plot/", {
                method: "POST",
                body: JSON.stringify({ files, y_cols, labels, graph_type: graphType, yaxis_scale: yaxisScale }),
                headers: { "Content-Type": "application/json" }
            })
            .then(res => res.json())
            .then(data => {
                Plotly.newPlot("plot", JSON.parse(data.plot).data, JSON.parse(data.plot).layout);
                window.lastFigJson = JSON.parse(data.plot); // Save for export
            });
        }

        function exportGraph(format) {
            fetch(`/export/?format=${format}`, {
                method: "POST",
                body: JSON.stringify(window.lastFigJson),
                headers: { "Content-Type": "application/json" }
            })
            .then(res => res.text())
            .then(txt => {
                document.getElementById("status").innerText = txt;
            });
        }

        function exportData() {
            const blocks = document.querySelectorAll(".graph-block");
            const files = [], y_cols = [];

            blocks.forEach(block => {
                const id = block.id.split("-")[1];
                files.push(block.querySelector(`.file-select[data-id="${id}"]`).value);
                y_cols.push(block.querySelector(`.y-col[data-id="${id}"]`).value);
            });

            fetch("/export_data/", {
                method: "POST",
                body: JSON.stringify({ files, y_cols }),
                headers: { "Content-Type": "application/json" }
            })
            .then(res => res.text())
            .then(txt => {
                document.getElementById("status").innerText = txt;
            });
        }

        // Add initial block
        addBlock(counter++);
    </script>
</body>
</html>


---

🎨 style.css

Path: data_analyzer/static/data_analyzer/style.css

.graph-block {
    border: 1px solid #dee2e6;
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 10px;
    background-color: #ffffff;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.05);
}

.form-label {
    font-weight: 500;
}

#plot {
    background-color: #fff;
    padding: 10px;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0,0,0,0.08);
}

#status {
    min-height: 20px;
}


---

✅ Summary

index.html gives you the full frontend UI with all interactive buttons and dropdowns.

style.css gives you clean layout, shadows, and styling for each block and the graph area.

All scripts use native JavaScript for AJAX and Plotly for visualization.



---

Would you like me to help you:

Add X-axis selection like Y-axis?

Bundle this into a ready-to-run GitHub repo?


Let me know!

