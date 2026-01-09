// Global variables:
let usecases = []
let selDimension = 'topics'; // default


// Load JSON data from hard-coded location:
async function loadUsecases() {
    // data_src = 'assets/data/usecases_current.json';
    const data_src = 'https://raw.githubusercontent.com/cewebbr/cordata/refs/heads/main/dados/limpos/usecases_current.json';
    const response = await fetch(data_src);
    const data = await response.json();
    usecases = data['data'];
    // TODO: apply Fundamental filter (remove non usecases)
  }


// Increment by one the object `counter` under key `bucket`:
function addOneInBucket(counter, bucket) {
    counter[bucket] = (counter[bucket] || 0) + 1;
    return counter;    
}

// Analogous to pandas Series.value_counts():
function valueCounts(array) {
    if (array === null) { return {}; }
    const counts = array.reduce(addOneInBucket, {});
    return counts;
}

// Increment counters `acc` by adding the values counted under a key in the object:
function addCounts(acc, obj, key) {
    const entry_counts = valueCounts(obj[key])
    for (const [key, value] of Object.entries(entry_counts)) {
        acc[key] = (acc[key] || 0) + value;
    }
    return acc;
}

// Create a incrementor function for counting occurences under a given object key over a list of such objects:
function makeIncrementor(key, value_is_str) {
    // If values in the usecases are strings:
    if (value_is_str == true) {
        return function incrementor(acc, obj) {
            return addCounts(acc, obj, key);
        }
    }
    // If values in the usecases are not strings (i.e., lists):  
    else {
        return function incrementor(acc, obj) {
            return addCounts(acc, obj, key);
        }
    }
}

// Count the number of usecases that feature each value under a given key:
function countUsecases(list, key) {
    const is_str = (typeof list[0][key] === 'string')
    const totals = list.reduce(makeIncrementor(key, is_str), {});
    return totals;
};

// Listen to Dimension dropdown:
const dropdown = document.getElementById('dimension');
dropdown.addEventListener('change', (event) => {
  selDimension = event.target.value;
  console.log('Selected:', selDimension);
  run();
});


async function run() {
    const counts = countUsecases(usecases, selDimension);
    console.log(counts);
}


async function init() {
    await loadUsecases();  // FETCH ONCE.
    //console.log(usecases);
    run();                 // INITIAL RENDER.
  };
init();



/*************/
/*** Plots ***/
/*************/

const ctx = document.getElementById('myChart');

const myChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
      label: 'Visitors',
      data: [120, 190, 300, 250, 220, 310],
      borderWidth: 2,
      tension: 0.3
    }]
  },
  options: {
    responsive: true,
    interaction: {
      mode: 'nearest',
      intersect: false
    },
    plugins: {
      tooltip: {
        enabled: true
      },
      legend: {
        display: true
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});
