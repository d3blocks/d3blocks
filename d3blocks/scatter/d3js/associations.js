// ============================================================
// associations.js — reusable statistical enrichment engine
// (ported from hnet's Python enrichment() / _compute_significance())
//
// Categorical columns -> hypergeometric test per category.
// Numeric columns    -> Wilcoxon rank-sum (normal approximation).
// Multiple testing   -> Holm step-down or Bonferroni.
//
// Pure data API (no DOM). Host charts supply:
//   columns: { name: [values length n], ... }
//   yBits:   [0|1, ...] length n  (1 = in selection / class of interest)
//
// Embed via Jinja include (same pattern as scatter.css). Keep this file free
// of Jinja delimiters so the include is not re-parsed as a template.
// ============================================================

// Lanczos approximation of ln(Gamma(x)), x > 0.
function logGamma(x) {
  var g = 7;
  var c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028,
            771.32342877765313, -176.61502916214059, 12.507343278686905,
            -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
  if (x < 0.5) {
    return Math.log(Math.PI / Math.sin(Math.PI * x)) - logGamma(1 - x);
  }
  x -= 1;
  var a = c[0];
  var t = x + g + 0.5;
  for (var i = 1; i < g + 2; i++) a += c[i] / (x + i);
  return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(a);
}
function logChoose(n, k) {
  if (k < 0 || k > n) return -Infinity;
  return logGamma(n + 1) - logGamma(k + 1) - logGamma(n - k + 1);
}
// Hypergeometric log-pmf: P(X=k) drawing N from population M containing n successes.
function hypergeomLogPmf(k, M, n, N) {
  return logChoose(n, k) + logChoose(M - n, N - k) - logChoose(M, N);
}
// Hypergeometric survival function P(X > k) -- one-sided enrichment (over-representation) test.
function hypergeomSf(k, M, n, N) {
  var lo = Math.max(0, N - (M - n)), hi = Math.min(n, N);
  if (k >= hi) return 0;
  var start = Math.max(k + 1, lo);
  var sum = 0;
  for (var j = start; j <= hi; j++) {
    var lp = hypergeomLogPmf(j, M, n, N);
    if (Number.isFinite(lp)) sum += Math.exp(lp);
  }
  return Math.min(1, Math.max(0, sum));
}
// Hypergeometric enrichment test between a binary feature indicator and a
// binary y indicator. Mirrors hnet's _prob_hypergeo: X = overlap-1 so the
// p-value answers "P(overlap >= observed)", i.e. one-sided over-representation.
function probHypergeo(featureBits, yBits) {
  var M = featureBits.length;
  var n = 0, N = 0, overlap = 0;
  for (var i = 0; i < M; i++) {
    if (featureBits[i]) n++;
    if (yBits[i]) { N++; if (featureBits[i]) overlap++; }
  }
  var X = overlap - 1;
  var P = (n === 0 || N === 0) ? 1 : hypergeomSf(X, M, n, N);
  return { P: P, popsize_M: M, nr_succes_pop_n: n, samplesize_N: N, overlap_X: overlap };
}
// Standard normal CDF via erf approximation (Abramowitz & Stegun 7.1.26).
function normalCdf(z) {
  var sign = z < 0 ? -1 : 1;
  z = Math.abs(z) / Math.SQRT2;
  var a1=0.254829592,a2=-0.284496736,a3=1.421413741,a4=-1.453152027,a5=1.061405429,p=0.3275911;
  var t = 1 / (1 + p * z);
  var y = 1 - (((((a5*t+a4)*t)+a3)*t+a2)*t+a1)*t*Math.exp(-z*z);
  return 0.5 * (1 + sign * y);
}
// Descriptive stats for a finite-number array: mean, sample std, median.
function numericSummary(arr) {
  var n = arr.length;
  if (n === 0) return { n: 0, mean: NaN, std: NaN, median: NaN };
  var sum = 0;
  for (var i = 0; i < n; i++) sum += arr[i];
  var mean = sum / n;
  var ss = 0;
  for (var j = 0; j < n; j++) {
    var d = arr[j] - mean;
    ss += d * d;
  }
  var std = n > 1 ? Math.sqrt(ss / (n - 1)) : 0;
  var sorted = arr.slice().sort(function(a, b){ return a - b; });
  var median = (n % 2 === 1)
    ? sorted[(n - 1) / 2]
    : (sorted[n / 2 - 1] + sorted[n / 2]) / 2;
  return { n: n, mean: mean, std: std, median: median };
}
function formatStatNum(x) {
  if (!Number.isFinite(x)) return '—';
  var ax = Math.abs(x);
  if (ax !== 0 && (ax < 0.001 || ax >= 10000)) return x.toExponential(2);
  if (ax >= 100) return x.toFixed(1);
  return x.toFixed(2);
}

// Wilcoxon rank-sum (Mann-Whitney) test via normal approximation, two-sided.
// Mirrors hnet's _prob_ranksums: compares numeric values between the y==1
// and y==0 groups. Also returns mean/std/median for selection vs rest so the
// UI can show interpretable effect summaries instead of only a z-score.
function probRanksums(values, yBits) {
  var n = values.length;
  var idx = values.map(function(_, i){ return i; }).filter(function(i){ return Number.isFinite(values[i]); });
  var selVals = [], restVals = [];
  for (var s = 0; s < idx.length; s++) {
    var si = idx[s];
    if (yBits[si]) selVals.push(values[si]);
    else restVals.push(values[si]);
  }
  var selStats = numericSummary(selVals);
  var restStats = numericSummary(restVals);

  var sorted = idx.slice().sort(function(a,b){ return values[a]-values[b]; });
  var ranks = new Array(n);
  var i = 0;
  while (i < sorted.length) {
    var j = i;
    while (j + 1 < sorted.length && values[sorted[j+1]] === values[sorted[i]]) j++;
    var avgRank = (i + j) / 2 + 1; // average rank for ties, 1-indexed
    for (var k = i; k <= j; k++) ranks[sorted[k]] = avgRank;
    i = j + 1;
  }
  var n1 = selStats.n, n2 = restStats.n, R1 = 0;
  for (var t = 0; t < idx.length; t++) {
    var ii = idx[t];
    if (yBits[ii]) R1 += ranks[ii];
  }
  if (n1 === 0 || n2 === 0) {
    return { P: 1, zscore: 0, sel: selStats, rest: restStats };
  }
  var muU = n1 * n2 / 2;
  var U1 = R1 - n1 * (n1 + 1) / 2;
  var sigmaU = Math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12);
  var z = sigmaU === 0 ? 0 : (U1 - muU) / sigmaU;
  var P = 2 * (1 - normalCdf(Math.abs(z)));
  return {
    P: Math.min(1, Math.max(0, P)),
    zscore: z,
    sel: selStats,
    rest: restStats
  };
}
// Holm-Bonferroni step-down multiple-testing correction.
function holmCorrection(pvalues) {
  var m = pvalues.length;
  var order = pvalues.map(function(_, i){ return i; }).sort(function(a,b){ return pvalues[a]-pvalues[b]; });
  var adj = new Array(m);
  var runningMax = 0;
  for (var rank = 0; rank < m; rank++) {
    var i = order[rank];
    var val = Math.min(1, (m - rank) * pvalues[i]);
    runningMax = Math.max(runningMax, val);
    adj[i] = runningMax;
  }
  return adj;
}
// Bonferroni correction: simply scales each p-value by the number of tests.
function bonferroniCorrection(pvalues) {
  var m = pvalues.length;
  return pvalues.map(function(p){ return Math.min(1, p * m); });
}

// dtype detection for a property column.
// 1) Must be "really numeric": every non-missing value parses as a finite
//    number (booleans / non-numeric strings → category).
// 2) Among present values, if the unique-value ratio is > 60%, treat as
//    numeric; otherwise treat as category (e.g. coded 0/1/2 labels).
// Missing / undefined / empty strings are skipped for both checks.
function detectColumnDtype(values) {
  var present = 0;
  var unique = {};
  var uniqueCount = 0;
  for (var i = 0; i < values.length; i++) {
    var v = values[i];
    if (v === undefined || v === null || v === '') continue;
    if (typeof v === 'boolean') return 'cat';
    var num = typeof v === 'number' ? v : parseFloat(v);
    if (!Number.isFinite(num) || (typeof v === 'string' && v.trim() !== '' && isNaN(Number(v)))) return 'cat';
    present++;
    var key = String(num);
    if (!Object.prototype.hasOwnProperty.call(unique, key)) {
      unique[key] = true;
      uniqueCount++;
    }
  }
  if (present === 0) return 'cat';
  // > 60% unique and truly numeric → numeric; otherwise category
  if (uniqueCount / present > 0.6) return 'num';
  return 'cat';
}

// Port of hnet's _compute_significance(): for each property column, run the
// appropriate test (categorical -> hypergeometric per category, numeric ->
// ranksum) between that column and y. y is binary (1 = selected); per the
// original algorithm's two-class handling, category '0' (not selected) is
// the negative/background class and is not tested on its own.
function computeSignificance(columns, yBits, dtypeOverrides) {
  dtypeOverrides = dtypeOverrides || {};
  var out = [];
  Object.keys(columns).forEach(function(colname) {
    var values = columns[colname];
    var dtype = dtypeOverrides[colname] || detectColumnDtype(values);
    if (dtype === 'num') {
      var nums = values.map(function(v){ return (v===undefined||v===null||v==='') ? NaN : (typeof v==='number'?v:parseFloat(v)); });
      var res = probRanksums(nums, yBits);
      out.push({
        category_label: colname,
        category_name: colname,
        y: '1',
        dtype: 'num',
        P: res.P,
        zscore: res.zscore,
        sel: res.sel,
        rest: res.rest
      });
    } else {
      // Build category -> indicator bits, skipping missing values.
      var cats = {};
      for (var i = 0; i < values.length; i++) {
        var v = values[i];
        if (v === undefined || v === null || v === '') continue;
        var key = String(v);
        if (!cats[key]) cats[key] = new Array(values.length).fill(0);
        cats[key][i] = 1;
      }
      var keys = Object.keys(cats);
      // Two-category case (e.g. true/false): drop the "0"/"false" background class.
      if (keys.length === 2 && keys.some(function(k){ return k==='0'||k==='false'||k==='False'; })) {
        keys = keys.filter(function(k){ return !(k==='0'||k==='false'||k==='False'); });
      }
      keys.forEach(function(key) {
        var occ = cats[key].reduce(function(a,b){return a+b;}, 0);
        if (occ < 2) return; // skip singleton categories (too small to test meaningfully)
        var res = probHypergeo(cats[key], yBits);
        out.push(Object.assign({ category_label: colname + ' = ' + key, category_name: colname, y: '1', dtype: 'cat', value: key }, res));
      });
    }
  });
  return out;
}

// Port of hnet's enrichment(): orchestrates significance computation,
// multiple-test correction (Holm or Bonferroni), and alpha filtering.
//
// @param {Object} columns        map of columnName -> values array (length n)
// @param {Array}  yBits          binary selection mask (length n)
// @param {number} [alpha=0.05]
// @param {Object} [dtypeOverrides] optional { col: 'num'|'cat' }
// @param {string} [multtest='holm']  'holm' | 'bonferroni'
// @returns {Array} significant results sorted by Padj
function enrichment(columns, yBits, alpha, dtypeOverrides, multtest) {
  alpha = alpha || 0.05;
  multtest = multtest || 'holm';
  var out = computeSignificance(columns, yBits, dtypeOverrides);
  var pvals = out.map(function(r){ return r.P; });
  var padj = multtest === 'bonferroni' ? bonferroniCorrection(pvals) : holmCorrection(pvals);
  out.forEach(function(r, i){ r.Padj = padj[i]; });
  out = out.filter(function(r){ return r.Padj <= alpha; });
  out.sort(function(a,b){ return a.Padj - b.Padj; });
  return out;
}

// Namespace for reuse from other visualizations without relying on globals alone.
var D3BlocksAssociations = {
  enrichment: enrichment,
  computeSignificance: computeSignificance,
  detectColumnDtype: detectColumnDtype,
  holmCorrection: holmCorrection,
  bonferroniCorrection: bonferroniCorrection,
  probHypergeo: probHypergeo,
  probRanksums: probRanksums,
  numericSummary: numericSummary,
  formatStatNum: formatStatNum
};
if (typeof window !== 'undefined') {
  window.D3BlocksAssociations = D3BlocksAssociations;
}
