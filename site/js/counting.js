// Increment by one the object `counter` under key `bucket`:
function addOneInBucket(counter, bucket) {
    counter[bucket] = (counter[bucket] || 0) + 1;
    return counter;    
}

// Increment by one the object `counter` under key `buc[ket]`:
// (to be applied to objects where the bucket is specified by an attribute of the object).
function addObjInBucket(counter, buc, ket) {
    counter[buc[ket]] = (counter[buc[ket]] || 0) + 1;
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
            return addObjInBucket(acc, obj, key);
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
export function countUsecases(list, key) {
    const is_str = (typeof list[0][key] === 'string')
    const totals = list.reduce(makeIncrementor(key, is_str), {});
    return totals;
};


// Sort object by its numeric values:
export function sortEntriesByNumericValue(obj, order = 'desc') {
    const factor = order === 'asc' ? 1 : -1;
    return Object.fromEntries(Object.entries(obj).sort(([, a], [, b]) => factor * (a - b)));
  }


// Count the number of datasets used by usecase `uc` (obj):
function countDatasetsInUc(uc) {
    return uc['datasets'].length;
}

// Increment by one the object `counter` under the number of datasets used by `uc` (obj):
function addOneInNDatasets(counter, uc) {
    counter[countDatasetsInUc(uc)] = (counter[countDatasetsInUc(uc)] || 0) + 1;
    return counter;    
}

// Compute the histogram of number of datasets used by usecases:
export function countDatasets(usecases) {
    if (usecases === null) return {};
    const counts = usecases.reduce(addOneInNDatasets, {});
    return counts;
}