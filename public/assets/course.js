/* Drinks Network course player: each lesson is Review -> Listen -> Answer; passing the questions unlocks the next lesson.
   Course content lives in /courses/<slug>.json (see README: "Course data"). Progress is kept in this browser. */
(function () {
  'use strict';
  var root = document.querySelector('[data-course]');
  if (!root) return;
  var slug = root.dataset.course;
  var KEY = 'dn-course-' + slug;
  var ENDPOINT = window.DN_ENQUIRY_ENDPOINT || '/api/enquiries';
  var PASS = 0.8; // share of questions that must be right to move on
  var state = load();
  var course = null;

  function load() { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }
  function $(s) { return root.querySelector(s); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  // /courses/<slug> -> /courses/<slug>.json (relative, so it also works from a static copy)
  fetch(new URL(slug + '.json', location.href).href).then(function (r) { if (!r.ok) throw new Error(); return r.json(); })
    .then(function (c) { course = c; init(); })
    .catch(function () { $('[data-player]').innerHTML = '<p class="prose">This course could not be loaded. Please try again shortly.</p>'; });

  function init() {
    if (!course.lessons || !course.lessons.length) {
      $('[data-start]').hidden = true;
      $('[data-player]').hidden = false;
      $('[data-player]').innerHTML = '<div class="course-empty"><p class="display" style="font-size:36px">Lessons are on their way.</p>' +
        '<p class="prose">We\'re moving this course across from our previous site.' + (course.legacyUrl ? ' Until then you can take it <a href="' + esc(course.legacyUrl) + '">on the previous site</a>.' : '') + '</p></div>';
      return;
    }
    state.done = state.done || {};
    if (state.learner) startPlayer(); else showStart();
  }

  function showStart() {
    var form = $('[data-start] form');
    $('[data-start]').hidden = false;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var d = {}; new FormData(form).forEach(function (v, k) { d[k] = v; });
      state.learner = { firstName: d.firstName, email: d.email };
      save();
      var consent = form.querySelector('[name=consent]');
      fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.assign({}, d, {
        form: 'course-start', campaign: 'course:' + slug, tags: ['Trade'], pageUrl: location.href,
        consent: consent && consent.checked ? { status: 'subscribed', wording: consent.closest('label').textContent.replace(/\s+/g, ' ').trim() } : null
      })) }).catch(function () {});
      startPlayer();
    });
  }

  function unlocked(i) { return i === 0 || !!state.done[course.lessons[i - 1].id]; }
  function current() {
    for (var i = 0; i < course.lessons.length; i++) if (!state.done[course.lessons[i].id]) return i;
    return course.lessons.length; // all done
  }

  function startPlayer() {
    $('[data-start]').hidden = true;
    $('[data-player]').hidden = false;
    var i = state.lesson != null && unlocked(state.lesson) ? state.lesson : current();
    if (i >= course.lessons.length) return finish();
    open(i, state.stage || 'review');
  }

  function nav(active) {
    return '<ol class="course-nav">' + course.lessons.map(function (l, i) {
      var done = state.done[l.id], open_ = unlocked(i);
      var mark = done ? '✓' : open_ ? (i + 1) : '🔒';
      return '<li><button type="button" data-goto="' + i + '"' + (open_ ? '' : ' disabled') + (i === active ? ' aria-current="step"' : '') + '>' +
        '<span class="course-mark' + (done ? ' done' : '') + '">' + mark + '</span><span>' + esc(l.title) + '</span></button></li>';
    }).join('') + '</ol>';
  }

  function stages(stage) {
    return '<div class="course-stages" role="list">' + [['review', '1 · Review'], ['listen', '2 · Listen'], ['answer', '3 · Answer']].map(function (s) {
      return '<span role="listitem" class="' + (s[0] === stage ? 'on' : '') + '">' + s[1] + '</span>';
    }).join('') + '</div>';
  }

  function open(i, stage) {
    stopSpeech();
    state.lesson = i; state.stage = stage; save();
    var l = course.lessons[i];
    var html = '<div class="course-layout"><aside>' + nav(i) + '</aside><section class="course-main">' +
      '<div class="kick" style="color:var(--red)">Lesson ' + (i + 1) + ' of ' + course.lessons.length + '</div>' +
      '<h2 class="display" style="font-size:clamp(36px,4.5vw,64px);margin:8px 0 16px">' + esc(l.title) + '</h2>' + stages(stage) + '<div class="course-stage">';
    if (stage === 'review') {
      html += '<div class="prose">' + (l.review || '') + '</div>' +
        '<button type="button" class="btn btn-red" data-next="listen">I\'ve read this — listen →</button>';
    } else if (stage === 'listen') {
      html += listenBlock(l) + '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:20px">' +
        '<button type="button" class="btn btn-line" data-next="review">← Back to review</button>' +
        '<button type="button" class="btn btn-red" data-next="answer" data-needs-listen disabled>Answer the questions →</button></div>' +
        '<p class="cap" data-listen-hint>Listen to the end to unlock the questions.</p>';
    } else {
      html += quizBlock(l);
    }
    html += '</div></section></div>';
    $('[data-player]').innerHTML = html;
    wire(i, stage);
    $('[data-player]').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function listenBlock(l) {
    var m = l.listen || {};
    if (m.type === 'youtube' && m.id) {
      return '<div class="course-media"><iframe src="https://www.youtube-nocookie.com/embed/' + esc(m.id) + '" title="' + esc(l.title) + '" allow="encrypted-media; picture-in-picture" allowfullscreen></iframe></div>' +
        '<label class="check" style="margin-top:14px"><input type="checkbox" data-heard> <span>I\'ve watched this video to the end</span></label>';
    }
    if ((m.type === 'audio' || m.type === 'video') && m.src) {
      var tag = m.type === 'audio' ? 'audio' : 'video';
      return '<div class="course-media ' + tag + '"><' + tag + ' controls preload="metadata" src="' + esc(m.src) + '" data-media></' + tag + '></div>';
    }
    return '<div class="course-tts"><p class="prose" style="margin:0 0 14px">Press play to hear this lesson read aloud.</p>' +
      '<button type="button" class="btn btn-red" data-speak>▶ Play lesson</button> <button type="button" class="btn btn-line" data-stop hidden>■ Stop</button></div>';
  }

  function quizBlock(l) {
    var qs = l.questions || [];
    if (!qs.length) return '<p class="prose">No questions for this lesson.</p><button type="button" class="btn btn-red" data-complete>Complete lesson →</button>';
    return '<form class="course-quiz" novalidate>' + qs.map(function (q, qi) {
      return '<fieldset><legend>' + (qi + 1) + '. ' + esc(q.q) + '</legend>' + q.options.map(function (o, oi) {
        return '<label class="course-opt"><input type="radio" name="q' + qi + '" value="' + oi + '" required> <span>' + esc(o) + '</span></label>';
      }).join('') + '<p class="course-explain" hidden></p></fieldset>';
    }).join('') + '<div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center"><button type="button" class="btn btn-line" data-next="listen">← Back</button>' +
      '<button type="submit" class="btn btn-red">Check my answers</button><p class="form-status" role="status"></p></div></form>';
  }

  function wire(i, stage) {
    var l = course.lessons[i];
    root.querySelectorAll('[data-goto]').forEach(function (b) { b.addEventListener('click', function () { open(Number(b.dataset.goto), 'review'); }); });
    root.querySelectorAll('[data-next]').forEach(function (b) { b.addEventListener('click', function () { open(i, b.dataset.next); }); });
    if (stage === 'listen') {
      var gate = $('[data-needs-listen]');
      var unlock = function () { gate.disabled = false; var h = $('[data-listen-hint]'); if (h) h.hidden = true; state.heard = state.heard || {}; state.heard[l.id] = true; save(); };
      if (state.heard && state.heard[l.id]) unlock();
      var media = $('[data-media]');
      if (media) media.addEventListener('ended', unlock);
      var heard = $('[data-heard]');
      if (heard) heard.addEventListener('change', function () { if (heard.checked) unlock(); });
      var speak = $('[data-speak]'), stop = $('[data-stop]');
      if (speak) {
        if (!('speechSynthesis' in window)) { speak.disabled = true; speak.textContent = 'Read-aloud not supported in this browser'; unlock(); }
        speak.addEventListener('click', function () {
          var tmp = document.createElement('div'); tmp.innerHTML = l.review || '';
          var u = new SpeechSynthesisUtterance(l.title + '. ' + tmp.textContent.replace(/\s+/g, ' ').trim());
          u.lang = 'en-AU'; u.rate = 1;
          u.onend = function () { stop.hidden = true; speak.hidden = false; unlock(); };
          speechSynthesis.cancel(); speechSynthesis.speak(u);
          // some browsers never fire onend: unlock once the lesson would have finished reading (~2.6 words a second)
          var words = (l.title + ' ' + tmp.textContent).split(/\s+/).length;
          setTimeout(unlock, Math.ceil(words / 2.6) * 1000);
          speak.hidden = true; stop.hidden = false;
        });
        stop.addEventListener('click', function () { stopSpeech(); stop.hidden = true; speak.hidden = false; });
      }
    }
    if (stage === 'answer') {
      var done = $('[data-complete]');
      if (done) done.addEventListener('click', function () { complete(i); });
      var form = $('.course-quiz');
      if (form) form.addEventListener('submit', function (e) {
        e.preventDefault();
        var qs = l.questions, right = 0, answered = 0;
        qs.forEach(function (q, qi) {
          var pick = form.querySelector('[name=q' + qi + ']:checked');
          var fs = form.querySelectorAll('fieldset')[qi], ex = fs.querySelector('.course-explain');
          if (!pick) { fs.classList.remove('ok', 'no'); ex.hidden = true; return; }
          answered++;
          var ok = Number(pick.value) === q.answer;
          if (ok) right++;
          fs.classList.toggle('ok', ok); fs.classList.toggle('no', !ok);
          ex.hidden = false; ex.textContent = ok ? 'Correct.' + (q.explain ? ' ' + q.explain : '') : 'Not quite.' + (q.explain ? ' ' + q.explain : ' Have another look at the lesson.');
        });
        var st = form.querySelector('.form-status');
        if (answered < qs.length) { st.textContent = 'Answer every question to continue.'; return; }
        if (right / qs.length >= PASS) { st.textContent = right + ' of ' + qs.length + ' right. Lesson complete!'; setTimeout(function () { complete(i); }, 900); }
        else st.textContent = right + ' of ' + qs.length + ' right. You need ' + Math.ceil(qs.length * PASS) + ' to move on — have another go.';
      });
    }
  }

  function complete(i) {
    state.done[course.lessons[i].id] = true; state.stage = 'review'; save();
    if (i + 1 < course.lessons.length) open(i + 1, 'review'); else finish();
  }

  function finish() {
    stopSpeech();
    state.lesson = null; save();
    $('[data-player]').innerHTML = '<div class="course-layout"><aside>' + nav(-1) + '</aside><section class="course-main course-finish">' +
      '<span class="kick" style="background:var(--red);color:#fff;padding:6px 10px">Course complete</span>' +
      '<h2 class="display" style="font-size:clamp(48px,6vw,96px);margin:18px 0 12px">Nice work' + (state.learner ? ', ' + esc(state.learner.firstName) : '') + '.</h2>' +
      '<p class="prose">You\'ve finished <strong>' + esc(course.title) + '</strong>.</p>' +
      '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:20px"><a class="btn btn-red" href="/courses">More courses</a><button type="button" class="btn btn-line" data-restart>Start again</button></div></section></div>';
    root.querySelectorAll('[data-goto]').forEach(function (b) { b.addEventListener('click', function () { open(Number(b.dataset.goto), 'review'); }); });
    $('[data-restart]').addEventListener('click', function () { state.done = {}; state.heard = {}; save(); open(0, 'review'); });
    try { fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ form: 'course-complete', campaign: 'course:' + slug, tags: ['Trade'], email: state.learner && state.learner.email, firstName: state.learner && state.learner.firstName, pageUrl: location.href }) }).catch(function () {}); } catch (e) {}
  }

  function stopSpeech() { if ('speechSynthesis' in window) speechSynthesis.cancel(); }
})();
