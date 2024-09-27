var chart;
var lastClickedFilter = null;

window.onload = function () {
    chart = new CanvasJS.Chart("chartContainer", {
        animationEnabled: true,
        animationDuration: 1000,
        title: {
            text: "Resultados de la Campaña",
            fontFamily: "Arial, sans-serif"
        },
        data: [{
            type: "funnel",
            toolTipContent: "<b>{label}</b>: {y} <b>({percentage}%)</b>",
            indexLabel: "{label} - {y}",
            valueRepresents: "area",
            dataPoints: chartData, // Asumimos que chartData se define en el HTML
            explodeOnClick: true,
            click: function(e) {
                filterTableAndAnimate(e.dataPoint.filter);
            }
        }]
    });
    calculatePercentage();
    chart.render();
}

function calculatePercentage() {
    var dataPoint = chart.options.data[0].dataPoints;
    var total = dataPoint[0].y;
    for (var i = 0; i < dataPoint.length; i++) {
        if (i == 0) {
            chart.options.data[0].dataPoints[i].percentage = 100;
        } else {
            chart.options.data[0].dataPoints[i].percentage = ((dataPoint[i].y / total) * 100).toFixed(2);
        }
    }
}

function filterTableAndAnimate(filter) {
    if (lastClickedFilter === filter) {
        filterTable('all');
        animateChart(null);
    } else {
        filterTable(filter);
        animateChart(filter);
    }
}

function filterTable(filter) {
    var rows = document.querySelectorAll("#resultsTable tbody tr");
    rows.forEach(function(row) {
        if (filter === 'all') {
            row.style.display = "";
        } else {
            var cell = row.querySelector(`td[data-filter="${filter}"]`);
            row.style.display = cell && cell.textContent === "Sí" ? "" : "none";
        }
    });
}

function animateChart(filter) {
    var dataPoints = chart.options.data[0].dataPoints;
    
    if (lastClickedFilter === filter) {
        // Si se hace clic en la misma sección, resetear todo
        dataPoints.forEach(dp => {
            dp.exploded = false;
            dp.color = null;
        });
        lastClickedFilter = null;
    } else {
        // Resetear el estado de explosión y color de todos los dataPoints
        dataPoints.forEach(dp => {
            dp.exploded = false;
            dp.color = null;
        });
        
        // Explotar y cambiar el color solo del dataPoint seleccionado
        var selectedDataPoint = dataPoints.find(dp => dp.filter === filter);
        if (selectedDataPoint) {
            selectedDataPoint.exploded = true;
            selectedDataPoint.color = "#FF9900"; // Color destacado
        }
        
        lastClickedFilter = filter;
    }
    
    chart.options.animationEnabled = true;
    chart.options.animationDuration = 1000; // Duración de la animación en milisegundos
    chart.render();
}

function toggleDetails(resultId) {
    var detailsRow = document.getElementById('details-' + resultId);
    if (detailsRow.style.display === "none") {
        detailsRow.style.display = "table-row";
    } else {
        detailsRow.style.display = "none";
    }
}
