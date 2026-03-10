// Functions for counting usecases with a given attribute:
import {countUsecases, sortEntriesByNumericValue, countDatasets} from './counting.js';

/*****************/
/*** FUNCTIONS ***/
/*****************/

// Load JSON data from hard-coded location:
async function loadUsecases() {
    // dataSrc = 'assets/data/usecases_current.json';
    const dataSrc = 'https://raw.githubusercontent.com/cewebbr/cordata/refs/heads/main/dados/limpos/usecases_current.json';
    const response = await fetch(dataSrc);
    const data = await response.json();
    usecases = data['data'];
    // TODO: apply Fundamental filter (remove non usecases)
  }


/****************/
/*** Plotting ***/
/****************/

function genCountsPlot(counts, elementId, chart, label) {
    const ctx = document.getElementById(elementId);
    chart = new Chart(ctx, {type: 'bar',
        data: {
            labels: Object.keys(counts),
            datasets: [{label: label, data: Object.values(counts), borderWidth: 2, tension: 0.3}]
        },
        options: {
            responsive: true,
            interaction: {mode: 'nearest', intersect: false},
            plugins: {tooltip: {enabled: true}, legend: {display: true}},
            scales: {y: {beginAtZero: true}}
        }
    });
    return chart;
}

function updateCountsPlot(counts, chart) {
    chart.data.labels = Object.keys(counts);
    chart.data.datasets[0].data = Object.values(counts);
    chart.update();
    return chart;
}

function plotCounts(counts, elementId, chart, label) {
    if (!chart) chart = genCountsPlot(counts, elementId, chart, label);
    else chart = updateCountsPlot(counts, chart);
    return chart;
}


function gen1DUsecaseChart() {
    let counts = {};
    if (UcDim1 == 'datasets') counts = countDatasets(usecases);
    else counts = sortEntriesByNumericValue(countUsecases(usecases, UcDim1));
    console.log(counts);
    chart = plotCounts(counts, 'usecases-chart-1d', chart, 'Casos cobrindo a categoria');
}


/************/
/*** INIT ***/
/************/

// HTML elements:
const selectorUcDim1 = document.getElementById('usecases-dimension-1')

// Global variables:
let usecases = [];
let UcDim1 = selectorUcDim1.value
let chart = null;

// Page load process:
(async function init() {
    // Fetch data once:
    await loadUsecases();
    // Initial render of plots:  
    gen1DUsecaseChart();

    
  })();


/*****************/
/*** BEHAVIOUR ***/
/*****************/

// Listen to Dimension selectorUcDim1:
selectorUcDim1.addEventListener('change', (event) => {
  UcDim1 = event.target.value;
  console.log('Selected:', UcDim1);
  gen1DUsecaseChart();
});
