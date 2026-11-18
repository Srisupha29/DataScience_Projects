(function () {
  'use strict';

  var AREAS = {
    stats:   { name: 'Statistics',       color: '#2F6BFF', on: '#FFFFFF' },
    ml:      { name: 'Machine learning', color: '#7B4DFF', on: '#FFFFFF' },
    sql:     { name: 'SQL',              color: '#0B7F77', on: '#FFFFFF' },
    llm:     { name: 'LLMs and AI',      color: '#D6303A', on: '#FFFFFF' },
    python:  { name: 'Python',           color: '#F2B01E', on: '#1A1405' },
    powerbi: { name: 'Power BI',         color: '#1F7A4D', on: '#FFFFFF' },
    mlmath:  { name: 'Math for ML',      color: '#E8590C', on: '#FFFFFF' }
  };
  var ORDER = ['ml', 'stats', 'sql', 'llm', 'python', 'powerbi', 'mlmath'];
  var LEVELS = { 1: 'Easier', 2: 'Medium', 3: 'Harder' };
  var MAX_SWAPS = 2;
  var RETRY_UNSURE_DAYS = 2;
  var RETRY_FAIL_DAYS = 3;
  var KEY = 'studyhub.v1';

  var TOPICS = window.TOPICS || [];
  var byId = {};
  TOPICS.forEach(function (t) { byId[t.id] = t; });

  /* ---------- storage (falls back to memory if the browser blocks it) ---------- */
  var memoryStore = null;
  function load() {
    try {
      var raw = window.localStorage.getItem(KEY);
      if (raw) return JSON.parse(raw);
    } catch (e) { /* ignore */ }
    return memoryStore;
  }
  function save() {
    memoryStore = state;
    try { window.localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* ignore */ }
  }

  var state = load() || {
    v: 1, topics: {}, day: null, rot: 0, todayId: null, shown: [],
    swaps: 0, lowEnergy: false, done: false, lastResult: '', history: [], flags: []
  };

  var view = 'card';   // 'card' | 'quiz' | 'result'
  var quiz = null;
  var resultInfo = null;

  /* ---------- helpers ---------- */
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function ymd(d) {
    var m = d.getMonth() + 1, day = d.getDate();
    return d.getFullYear() + '-' + (m < 10 ? '0' : '') + m + '-' + (day < 10 ? '0' : '') + day;
  }
  function today() { return ymd(new Date()); }
  function addDays(s, n) {
    var p = s.split('-');
    return ymd(new Date(+p[0], +p[1] - 1, +p[2] + n));
  }
  function niceDate(s) {
    var p = s.split('-');
    return new Date(+p[0], +p[1] - 1, +p[2]).toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'short' });
  }
  function shuffle(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }
  function notify(msg) {
    var el = document.getElementById('notice');
    el.textContent = msg || '';
  }

  /* ---------- picking a topic ---------- */
  function isEligible(t, day) {
    var s = state.topics[t.id];
    if (!s) return true;
    if (s.status === 'mastered') return false;
    if (s.status === 'retry') return s.due <= day;
    return true;
  }

  function pickTopic(exclude) {
    var day = today();
    var ex = exclude || [];
    var pool = TOPICS.filter(function (t) { return ex.indexOf(t.id) < 0 && !t.deep && isEligible(t, day); });
    if (!pool.length) return null;

    if (state.lowEnergy) {
      var light = pool.filter(function (t) { return t.light; });
      if (light.length) pool = light;
    }

    // Topics that are due for another try come first.
    var due = pool.filter(function (t) {
      var s = state.topics[t.id];
      return s && s.status === 'retry';
    }).sort(function (a, b) { return state.topics[a.id].due < state.topics[b.id].due ? -1 : 1; });
    if (due.length) return due[0];

    // Otherwise rotate through the subject areas.
    for (var i = 0; i < ORDER.length; i++) {
      var idx = (state.rot + i) % ORDER.length;
      var items = pool.filter(function (t) { return t.area === ORDER[idx]; });
      if (items.length) {
        state.rot = (idx + 1) % ORDER.length;
        return items[0];
      }
    }
    return pool[0];
  }

  function pickDeep(exclude) {
    var day = today();
    var ex = exclude || [];
    var pool = TOPICS.filter(function (t) { return t.deep && ex.indexOf(t.id) < 0 && isEligible(t, day); });
    if (!pool.length) return null;
    var due = pool.filter(function (t) {
      var s = state.topics[t.id];
      return s && s.status === 'retry';
    });
    if (due.length) return due[0];
    var start = state.deepRot || 0;
    for (var i = 0; i < ORDER.length; i++) {
      var idx = (start + i) % ORDER.length;
      var items = pool.filter(function (t) { return t.area === ORDER[idx]; });
      if (items.length) {
        state.deepRot = (idx + 1) % ORDER.length;
        return items[0];
      }
    }
    return pool[0];
  }

  function setToday(t) {
    state.todayId = t ? t.id : null;
    if (t && state.shown.indexOf(t.id) < 0) state.shown.push(t.id);
    state.done = false;
    state.lastResult = '';
  }

  function startDay() {
    var d = today();
    if (state.day === d && (state.todayId || !TOPICS.length)) return;
    if (state.day !== d) {
      state.day = d;
      state.swaps = 0;
      state.lowEnergy = false;
      state.shown = [];
    }
    setToday(pickTopic([]));
    save();
  }

  /* ---------- rendering ---------- */
  function renderHeader() {
    document.getElementById('date').textContent = niceDate(today());
    var chip = document.getElementById('lowEnergy');
    chip.setAttribute('aria-pressed', state.lowEnergy ? 'true' : 'false');
    chip.textContent = state.lowEnergy ? 'Low energy: on' : 'Low energy';
    var n = state.flags.length;
    document.getElementById('flagBtn').textContent = 'Copy flagged questions' + (n ? ' (' + n + ')' : '');
  }

  function bandStyle(area) {
    var a = AREAS[area];
    return 'style="--area:' + a.color + ';--on:' + a.on + '"';
  }

  function renderCard() {
    var t = byId[state.todayId];
    if (!t && TOPICS.some(function (x) { return x.deep && isEligible(x, today()); })) {
      return '<section class="card empty"><h2>Regular topics are done</h2><p>Press Deep dive for a longer topic.</p></section>';
    }
    if (!t) {
      return '<section class="card empty"><h2>Every topic is mastered</h2>' +
        '<p>You have passed all the topics in this set. Add more topics in the data folder and they will show up here.</p></section>';
    }
    var a = AREAS[t.area];
    var left = MAX_SWAPS - state.swaps;
    var src = t.res.src === 'datacamp' ? 'DataCamp' : 'Free';
    var html = '<article class="card" ' + bandStyle(t.area) + '>' +
      '<div class="band"><p class="area">' + esc(a.name) + '</p><h2>' + esc(t.title) + '</h2>' +
      '<ul class="meta"><li>' + t.mins + ' min</li><li>' + LEVELS[t.level] + '</li>' + (t.light ? '<li>Light</li>' : '') + (t.deep ? '<li>Deep dive</li>' : '') + '</ul></div>' +
      '<div class="body">' +
      '<div class="block"><h3>Study this</h3><a class="res" href="' + esc(t.res.url) + '" target="_blank" rel="noopener">' + esc(t.res.label) + '</a><span class="src">' + src + '</span></div>' +
      '<div class="block"><h3>Say it aloud in 2 minutes</h3><p>' + esc(t.aloud) + '</p></div>' +
      '<div class="block"><h3>Interview question</h3><p>' + esc(t.interviewQ) + '</p></div>';

    if (state.done) {
      html += '<div class="block"><h3>Today</h3><p>' + esc(state.lastResult) + '</p></div>' +
        '<div class="actions"><button class="btn primary" data-action="another">Take another topic</button></div>';
    } else {
      html += '<div class="actions">' +
        '<button class="btn primary" data-action="done">Done, check me</button>' +
        '<button class="btn" data-action="unsure">Not sure yet</button>' +
        '<button class="btn" data-action="swap"' + (left <= 0 ? ' disabled' : '') + '>Give me another (' + Math.max(left, 0) + ' left today)</button>' +
        '</div>';
    }
    return html + '</div></article>';
  }

  function renderQuiz() {
    var t = quiz.topic;
    var item = quiz.items[quiz.i];
    var html = '<article class="card" ' + bandStyle(t.area) + '>' +
      '<div class="band"><p class="area">Check: ' + esc(t.title) + '</p>' +
      '<h2>Question ' + (quiz.i + 1) + ' of ' + quiz.items.length + '</h2></div>' +
      '<div class="body"><p class="qtext">' + esc(item.q) + '</p><div class="opts">';
    item.options.forEach(function (o, idx) {
      var cls = 'opt';
      if (quiz.answered) {
        if (o.correct) cls += ' right';
        else if (idx === quiz.picked) cls += ' wrong';
      }
      html += '<button class="' + cls + '" data-action="pick" data-i="' + idx + '"' + (quiz.answered ? ' disabled' : '') + '>' + esc(o.text) + '</button>';
    });
    html += '</div>';
    if (quiz.answered) {
      var ok = item.options[quiz.picked].correct;
      var flagged = isFlagged(t.id, quiz.i);
      html += '<div class="feedback" aria-live="polite"><p class="verdict ' + (ok ? 'good' : 'bad') + '">' + (ok ? 'Correct' : 'Not quite') + '</p>' +
        '<p>' + esc(item.why) + '</p>' +
        '<div class="actions"><button class="btn primary" data-action="next">' + (quiz.i + 1 < quiz.items.length ? 'Next question' : 'See result') + '</button>' +
        '<button class="btn" data-action="flag"' + (flagged ? ' disabled' : '') + '>' + (flagged ? 'Flagged as wrong' : 'This question is wrong') + '</button></div></div>';
    }
    return html + '</div></article>';
  }

  function renderResult() {
    var r = resultInfo;
    var t = r.topic;
    return '<article class="card" ' + bandStyle(t.area) + '>' +
      '<div class="band"><p class="area">' + esc(t.title) + '</p><h2>' + (r.passed ? 'Passed' : 'Not yet') + '</h2></div>' +
      '<div class="body"><p class="score">' + r.score + '/' + r.total + '</p>' +
      '<p>' + esc(r.message) + '</p>' +
      '<div class="actions"><button class="btn primary" data-action="another">Take another topic</button>' +
      '<button class="btn" data-action="back">Back to today</button></div></div></article>';
  }

  function renderProgress() {
    var html = '<h2>Progress</h2>';
    ORDER.forEach(function (id) {
      var all = TOPICS.filter(function (t) { return t.area === id; });
      var got = all.filter(function (t) { var s = state.topics[t.id]; return s && s.status === 'mastered'; });
      var pct = all.length ? Math.round(100 * got.length / all.length) : 0;
      html += '<div class="row"><span>' + esc(AREAS[id].name) + '</span>' +
        '<div class="bar" role="img" aria-label="' + pct + ' percent mastered"><span style="width:' + pct + '%;--c:' + AREAS[id].color + '"></span></div>' +
        '<span class="count">' + got.length + '/' + all.length + '</span></div>';
    });
    var recent = state.history.slice(-6).reverse();
    if (recent.length) {
      html += '<ul class="recent">';
      recent.forEach(function (h) {
        var t = byId[h.id];
        var label = h.result === 'unsure' ? 'Not sure yet' : (h.result === 'passed' ? 'Passed ' : 'Missed ') + h.score + '/' + h.total;
        html += '<li><span>' + esc(t ? t.title : h.id) + '</span><span>' + esc(label) + '</span></li>';
      });
      html += '</ul>';
    }
    return html;
  }

  function render() {
    renderHeader();
    var main = document.getElementById('main');
    if (view === 'quiz') main.innerHTML = renderQuiz();
    else if (view === 'result') main.innerHTML = renderResult();
    else main.innerHTML = renderCard();
    document.getElementById('progress').innerHTML = renderProgress();
  }

  /* ---------- actions ---------- */
  function isFlagged(id, qi) {
    return state.flags.some(function (f) { return f.id === id && f.qi === qi; });
  }

  function record(topic, result, score, total) {
    state.history.push({ date: today(), id: topic.id, area: topic.area, result: result, score: score, total: total });
    if (state.history.length > 300) state.history = state.history.slice(-300);
  }

  function startQuiz() {
    var t = byId[state.todayId];
    if (!t) return;
    quiz = {
      topic: t, i: 0, score: 0, answered: false, picked: null,
      items: t.quiz.map(function (q) {
        return {
          q: q.q,
          why: q.why,
          options: shuffle(q.options.map(function (text, idx) { return { text: text, correct: idx === q.answer }; }))
        };
      })
    };
    view = 'quiz';
  }

  function finishQuiz() {
    var t = quiz.topic;
    var total = quiz.items.length;
    var score = quiz.score;
    var passed = score >= Math.ceil(total * 2 / 3);
    var message;
    if (passed) {
      state.topics[t.id] = { status: 'mastered', date: today() };
      message = 'This topic is marked as mastered.';
      record(t, 'passed', score, total);
    } else {
      var due = addDays(today(), RETRY_FAIL_DAYS);
      state.topics[t.id] = { status: 'retry', due: due };
      message = 'It will come back on ' + niceDate(due) + '. Read the resource again before then.';
      record(t, 'missed', score, total);
    }
    state.done = true;
    state.lastResult = passed ? 'Passed ' + score + '/' + total + '.' : 'Missed ' + score + '/' + total + '. It comes back later.';
    resultInfo = { topic: t, score: score, total: total, passed: passed, message: message };
    view = 'result';
    quiz = null;
    save();
  }

  function download(name, text) {
    var blob = new Blob([text], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url; a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  function copyFlags() {
    if (!state.flags.length) { notify('No flagged questions yet.'); return; }
    var text = state.flags.map(function (f) {
      return f.id + ' (question ' + (f.qi + 1) + '): ' + f.q;
    }).join('\n');
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        notify('Copied ' + state.flags.length + ' flagged question(s). Paste them to Claude to fix.');
      }, function () { window.prompt('Copy this text:', text); });
    } else {
      window.prompt('Copy this text:', text);
    }
  }

  document.addEventListener('click', function (e) {
    var el = e.target.closest('[data-action]');
    if (!el || el.disabled) return;
    var action = el.getAttribute('data-action');
    notify('');

    if (action === 'low-energy') {
      state.lowEnergy = !state.lowEnergy;
      if (state.lowEnergy && !state.done && view === 'card') {
        var cur = byId[state.todayId];
        if (!cur || !cur.light) {
          var t = pickTopic(state.shown);
          if (t) setToday(t); else notify('No lighter topic left. Keeping today’s topic.');
        }
      }
    } else if (action === 'deep') {
      var dt = pickDeep(state.shown);
      view = 'card';
      if (dt) setToday(dt); else notify('No other deep dive is available right now.');
    } else if (action === 'done') {
      startQuiz();
    } else if (action === 'unsure') {
      var cur2 = byId[state.todayId];
      var due = addDays(today(), RETRY_UNSURE_DAYS);
      state.topics[cur2.id] = { status: 'retry', due: due };
      record(cur2, 'unsure', 0, 0);
      state.done = true;
      state.lastResult = 'Marked not sure yet. It comes back on ' + niceDate(due) + '.';
    } else if (action === 'swap') {
      if (state.swaps >= MAX_SWAPS) { notify('No swaps left today.'); }
      else {
        var t2 = pickTopic(state.shown);
        if (t2) { state.swaps += 1; setToday(t2); }
        else notify('No other topic is available right now.');
      }
    } else if (action === 'another') {
      var t3 = pickTopic(state.shown);
      view = 'card';
      if (t3) setToday(t3); else notify('No other topic is available right now.');
    } else if (action === 'back') {
      view = 'card';
    } else if (action === 'pick') {
      if (quiz && !quiz.answered) {
        quiz.picked = +el.getAttribute('data-i');
        quiz.answered = true;
        if (quiz.items[quiz.i].options[quiz.picked].correct) quiz.score += 1;
      }
    } else if (action === 'next') {
      if (quiz.i + 1 < quiz.items.length) {
        quiz.i += 1; quiz.answered = false; quiz.picked = null;
      } else {
        finishQuiz();
      }
    } else if (action === 'flag') {
      var q = quiz.items[quiz.i];
      if (!isFlagged(quiz.topic.id, quiz.i)) {
        state.flags.push({ id: quiz.topic.id, qi: quiz.i, q: q.q, date: today() });
      }
    } else if (action === 'export') {
      download('study-hub-backup.json', JSON.stringify(state, null, 2));
    } else if (action === 'import') {
      document.getElementById('importFile').click();
      return;
    } else if (action === 'copy-flags') {
      copyFlags();
      return;
    }
    save();
    render();
  });

  document.getElementById('importFile').addEventListener('change', function (e) {
    var file = e.target.files && e.target.files[0];
    if (!file) return;
    var reader = new FileReader();
    reader.onload = function () {
      try {
        var data = JSON.parse(reader.result);
        if (!data || typeof data.topics !== 'object' || !Array.isArray(data.history)) throw new Error('bad file');
        state = data;
        if (!Array.isArray(state.flags)) state.flags = [];
        if (!Array.isArray(state.shown)) state.shown = [];
        state.day = null;       // pick today's topic again with the imported progress
        state.todayId = null;
        view = 'card';
        startDay();
        render();
        notify('Backup imported.');
      } catch (err) {
        notify('That file is not a valid backup.');
      }
    };
    reader.readAsText(file);
    e.target.value = '';
  });

  /* ---------- start ---------- */
  if (!TOPICS.length) {
    document.getElementById('main').innerHTML = '<section class="card empty"><h2>No topics found</h2><p>Check that the files in the data folder are uploaded next to this page.</p></section>';
    renderHeader();
  } else {
    startDay();
    render();
  }
})();
