/* Drinks Network course player.
   Each lesson is Watch -> Review -> Answer; passing the questions unlocks the next lesson.
   Every course is free. Finishing a course issues a named Drinks Network certificate (PNG download / print).
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
  function asset(p) { return /^\//.test(p) ? new URL('..' + p, location.href).href : p; }
  function ytId(l) { var m = l && l.listen; return m && m.type === 'youtube' && m.id ? m.id : null; }
  function fullName() { var L = state.learner || {}; return (L.fullName || [L.firstName, L.lastName].filter(Boolean).join(' ')).trim(); }

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
    state.heard = state.heard || {};
    if (state.stage === 'listen') state.stage = 'watch'; // older saved progress
    screen();
    outline();
    if (state.learner) startPlayer(); else showStart();
  }

  /* ---------- Video player: poster + play button, swaps in the YouTube embed and reports when it ends ---------- */
  var ytListeners = [];
  window.addEventListener('message', function (e) {
    if (!/youtube(-nocookie)?\.com$/.test(new URL(e.origin).hostname)) return;
    var d; try { d = typeof e.data === 'string' ? JSON.parse(e.data) : e.data; } catch (x) { return; }
    if (!d || !d.info) return;
    ytListeners.forEach(function (h) { if (h.frame.contentWindow === e.source) h.fn(d.info); });
  });

  function videoHTML(l, n, opts) {
    var id = ytId(l);
    if (!id) return '';
    return '<div class="dn-video' + (opts && opts.big ? ' big' : '') + '" data-video="' + esc(id) + '" data-lesson="' + esc(l.id) + '">' +
      '<img class="dn-video-poster" src="' + esc(l.thumb ? asset(l.thumb) : 'https://i.ytimg.com/vi/' + id + '/hqdefault.jpg') + '" alt="">' +
      '<button type="button" class="dn-video-play" aria-label="Play lesson ' + n + ': ' + esc(l.title) + '"><svg viewBox="0 0 24 24" width="38" height="38" aria-hidden="true"><path d="M8 5v14l11-7z" fill="currentColor"/></svg></button>' +
      '<div class="dn-video-meta"><span class="dn-video-n">Lesson ' + n + '</span><span class="dn-video-t">' + esc(l.title) + '</span></div>' +
      '</div>';
  }

  function wireVideo(box, onEnd) {
    if (!box) return;
    var go = function () {
      var id = box.dataset.video;
      var src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) + '?autoplay=1&rel=0&modestbranding=1&playsinline=1&enablejsapi=1&origin=' + encodeURIComponent(location.origin);
      box.classList.add('playing');
      box.innerHTML = '<iframe src="' + src + '" title="Video lesson" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>';
      var f = box.querySelector('iframe');
      f.addEventListener('load', function () {
        var ping = function () { try { f.contentWindow.postMessage(JSON.stringify({ event: 'listening', id: id }), '*'); } catch (e) {} };
        ping(); setTimeout(ping, 1200);
      });
      ytListeners.push({ frame: f, fn: function (info) { if (info.playerState === 0 && onEnd) onEnd(); } });
    };
    box.querySelector('.dn-video-play').addEventListener('click', go);
    box.querySelector('.dn-video-poster').addEventListener('click', go);
  }

  // The "screen" in the page header: now-playing window plus a playlist strip of every lesson
  function screen() {
    var slot = document.querySelector('[data-course-screen]');
    if (!slot) return;
    var vids = course.lessons.map(function (l, i) { return { l: l, i: i }; }).filter(function (x) { return ytId(x.l); });
    if (!vids.length) return;
    var show = function (k) {
      var x = vids[k];
      slot.querySelector('.dn-screen-now').innerHTML = '<span class="dn-dot"></span>Now showing · ' + (x.i + 1) + ' of ' + course.lessons.length;
      var stage = slot.querySelector('.dn-screen-stage');
      stage.innerHTML = videoHTML(x.l, x.i + 1, { big: true });
      wireVideo(stage.firstChild, function () { state.heard[x.l.id] = true; save(); });
      slot.querySelectorAll('.dn-strip button').forEach(function (b, j) { b.setAttribute('aria-pressed', j === k ? 'true' : 'false'); });
    };
    slot.innerHTML = '<div class="dn-screen"><div class="dn-screen-bar"><span class="dn-screen-now"></span><span class="dn-screen-ch">' + esc(course.videoSeries ? course.videoSeries.replace(/\s*\(YouTube\)/, '') : 'Drinks Network Explained') + '</span></div>' +
      '<div class="dn-screen-stage"></div>' +
      '<div class="dn-strip" role="list">' + vids.map(function (x, k) {
        return '<button type="button" role="listitem" data-k="' + k + '" aria-pressed="false"><img src="' + esc(asset(x.l.thumb || '')) + '" alt="" loading="lazy"><span>' + (x.i + 1) + ' · ' + esc(x.l.title) + '</span></button>';
      }).join('') + '</div></div>';
    slot.querySelectorAll('.dn-strip button').forEach(function (b) { b.addEventListener('click', function () { show(Number(b.dataset.k)); }); });
    show(0);
  }

  function outline() {
    var box = document.createElement('div');
    box.className = 'course-outline';
    box.innerHTML = '<div class="kick" style="color:var(--red)">' + course.lessons.length + ' lessons · free · certificate on completion</div>' +
      '<ol>' + course.lessons.map(function (l, i) {
        return '<li>' + (l.thumb ? '<img class="course-outline-thumb" src="' + esc(asset(l.thumb)) + '" alt="" loading="lazy" onerror="this.remove()">' : '') +
          '<span class="course-outline-n">' + (i + 1) + '</span><span class="course-outline-t">' + esc(l.title) + '</span></li>';
      }).join('') + '</ol>';
    root.appendChild(box);
  }

  function showStart() {
    var form = $('[data-start] form');
    $('[data-start]').hidden = false;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var d = {}; new FormData(form).forEach(function (v, k) { d[k] = String(v).trim(); });
      state.learner = { firstName: d.firstName, lastName: d.lastName || '', email: d.email };
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
    if (current() >= course.lessons.length) return finish();
    var i = state.lesson != null && unlocked(state.lesson) ? state.lesson : current();
    open(i, state.stage || 'watch', true);
  }

  function nav(active) {
    return '<ol class="course-nav">' + course.lessons.map(function (l, i) {
      var done = state.done[l.id], open_ = unlocked(i);
      var mark = done ? '✓' : open_ ? (i + 1) : '🔒';
      return '<li><button type="button" data-goto="' + i + '"' + (open_ ? '' : ' disabled') + (i === active ? ' aria-current="step"' : '') + '>' +
        '<span class="course-mark' + (done ? ' done' : '') + '">' + mark + '</span><span>' + esc(l.title) + '</span></button></li>';
    }).join('') + '</ol>';
  }

  function stages(stage, l) {
    return '<div class="course-stages" role="list">' + [['watch', ytId(l) ? '1 · Watch' : '1 · Listen'], ['review', '2 · Review'], ['answer', '3 · Answer']].map(function (s) {
      return '<span role="listitem" class="' + (s[0] === stage ? 'on' : '') + '">' + s[1] + '</span>';
    }).join('') + '</div>';
  }

  function open(i, stage, quiet) {
    stopSpeech();
    state.lesson = i; state.stage = stage; save();
    var l = course.lessons[i];
    var html = '<div class="course-layout"><aside>' + nav(i) + '</aside><section class="course-main">' +
      '<div class="kick" style="color:var(--red)">Lesson ' + (i + 1) + ' of ' + course.lessons.length + '</div>' +
      '<h2 class="display" style="font-size:clamp(36px,4.5vw,64px);margin:8px 0 16px">' + esc(l.title) + '</h2>' + stages(stage, l) + '<div class="course-stage">';
    if (stage === 'watch') {
      html += watchBlock(l, i) + '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:20px">' +
        '<button type="button" class="btn btn-red" data-next="review" data-needs-watch disabled>Read the lesson notes →</button></div>' +
        '<p class="cap" data-watch-hint>' + (ytId(l) ? 'Watch to the end (or tick the box) to unlock the notes.' : 'Listen to the end to unlock the notes.') + '</p>';
    } else if (stage === 'review') {
      html += '<div class="prose">' + (l.review || '') + '</div>' +
        '<div style="display:flex;gap:12px;flex-wrap:wrap"><button type="button" class="btn btn-line" data-next="watch">← Back to the video</button>' +
        '<button type="button" class="btn btn-red" data-next="answer">Answer the questions →</button></div>';
    } else {
      html += quizBlock(l);
    }
    html += '</div></section></div>';
    $('[data-player]').innerHTML = html;
    wire(i, stage);
    if (!quiet) $('[data-player]').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function watchBlock(l, i) {
    if (ytId(l)) {
      return videoHTML(l, i + 1) + '<label class="check" style="margin-top:14px"><input type="checkbox" data-heard> <span>I\'ve watched this video to the end</span></label>';
    }
    var m = l.listen || {};
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
    }).join('') + '<div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center"><button type="button" class="btn btn-line" data-next="review">← Back</button>' +
      '<button type="submit" class="btn btn-red">Check my answers</button><p class="form-status" role="status"></p></div></form>';
  }

  function wire(i, stage) {
    var l = course.lessons[i];
    root.querySelectorAll('[data-goto]').forEach(function (b) { b.addEventListener('click', function () { open(Number(b.dataset.goto), 'watch'); }); });
    root.querySelectorAll('[data-next]').forEach(function (b) { b.addEventListener('click', function () { open(i, b.dataset.next); }); });
    if (stage === 'watch') {
      var gate = $('[data-needs-watch]');
      var heard = $('[data-heard]');
      var unlock = function () { gate.disabled = false; var h = $('[data-watch-hint]'); if (h) h.hidden = true; if (heard) heard.checked = true; state.heard[l.id] = true; save(); };
      if (state.heard[l.id]) unlock();
      wireVideo($('.course-stage .dn-video'), unlock);
      var media = $('[data-media]');
      if (media) media.addEventListener('ended', unlock);
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
    state.done[course.lessons[i].id] = true; state.stage = 'watch'; save();
    if (i + 1 < course.lessons.length) open(i + 1, 'watch'); else finish();
  }

  /* ---------- Finish + certificate ---------- */
  function finish() {
    stopSpeech();
    state.lesson = null;
    if (!state.completedAt) state.completedAt = new Date().toISOString();
    if (!state.certId) state.certId = 'DN-' + slug.split('-').map(function (w) { return w[0]; }).join('').toUpperCase() + '-' + Date.now().toString(36).toUpperCase().slice(-6);
    save();
    $('[data-player]').innerHTML = '<div class="course-layout"><aside>' + nav(-1) + '</aside><section class="course-main course-finish">' +
      '<span class="kick" style="background:var(--red);color:#fff;padding:6px 10px">Course complete</span>' +
      '<h2 class="display" style="font-size:clamp(48px,6vw,96px);margin:18px 0 12px">Nice work' + (state.learner && state.learner.firstName ? ', ' + esc(state.learner.firstName) : '') + '.</h2>' +
      '<p class="prose">You\'ve finished <strong>' + esc(course.title) + '</strong>. Here\'s your certificate. Check how your name reads, then download or print it.</p>' +
      '<form class="cert-name" data-cert-form><label class="fld">Name on your certificate<input name="fullName" required maxlength="60" autocomplete="name" value="' + esc(fullName()) + '"></label><button class="btn btn-line" type="submit">Update certificate</button></form>' +
      '<div class="cert-wrap"><canvas class="cert" width="2400" height="1697" data-cert aria-label="Certificate of completion"></canvas></div>' +
      '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:20px"><a class="btn btn-red" data-cert-download download="drinks-network-certificate.png" href="#">Download certificate (PNG)</a>' +
      '<button type="button" class="btn btn-line" data-cert-print>Print / save as PDF</button>' +
      '<a class="btn btn-line" href="/courses">More free courses</a><button type="button" class="btn btn-line" data-restart>Start again</button></div></section></div>';
    root.querySelectorAll('[data-goto]').forEach(function (b) { b.addEventListener('click', function () { open(Number(b.dataset.goto), 'watch'); }); });
    $('[data-restart]').addEventListener('click', function () { state.done = {}; state.heard = {}; state.completedAt = null; state.certId = null; save(); open(0, 'watch'); });
    var cv = $('[data-cert]');
    var draw = function () {
      drawCertificate(cv, { name: fullName() || 'Drinks Network Learner', course: course.title, lessons: course.lessons.length, date: new Date(state.completedAt), id: state.certId }).then(function () {
        var a = $('[data-cert-download]');
        try { a.href = cv.toDataURL('image/png'); a.download = 'drinks-network-' + slug + '-certificate.png'; } catch (e) {}
      });
    };
    $('[data-cert-form]').addEventListener('submit', function (e) {
      e.preventDefault();
      var v = e.target.fullName.value.replace(/\s+/g, ' ').trim();
      if (!v) return;
      state.learner = Object.assign({}, state.learner, { fullName: v }); save(); draw();
    });
    $('[data-cert-print]').addEventListener('click', function () {
      var w = window.open('', '_blank');
      if (!w) return;
      w.document.write('<!doctype html><title>' + esc(course.title) + ' certificate</title><style>@page{size:A4 landscape;margin:0}html,body{margin:0}img{width:100%;height:auto;display:block}</style><img src="' + cv.toDataURL('image/png') + '" onload="setTimeout(function(){print()},300)">');
      w.document.close();
    });
    draw();
    try { fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ form: 'course-complete', campaign: 'course:' + slug, tags: ['Trade'], email: state.learner && state.learner.email, firstName: state.learner && state.learner.firstName, lastName: state.learner && state.learner.lastName, message: 'Certificate ' + state.certId + ' issued to ' + fullName(), pageUrl: location.href }) }).catch(function () {}); } catch (e) {}
  }

  function img(src) { return new Promise(function (res) { var i = new Image(); i.onload = function () { res(i); }; i.onerror = function () { res(null); }; i.src = src; }); }

  function drawCertificate(cv, d) {
    var fonts = ['400 120px Anton', '700 40px "Archivo Narrow"', 'italic 400 60px "Source Serif 4"', '600 40px "Source Serif 4"'];
    var ready = document.fonts && document.fonts.load ? Promise.all(fonts.map(function (f) { return document.fonts.load(f).catch(function () {}); })) : Promise.resolve();
    return Promise.all([ready, img(asset('/media/logos/drinks-network-script-white.png')), img(asset('/media/people/ice-divider.png')), img(asset('/media/people/wave-full.png')), img(asset('/media/logos/drinks-network-script-red.png'))]).then(function (r) {
      var logoW = r[1], ice = r[2], wave = r[3], logoR = r[4];
      var c = cv.getContext('2d'), W = cv.width, H = cv.height;
      var RED = '#E42E2E', NAVY = '#1E2552', PAPER = '#FBF7F0', INK = '#111', PINK = '#FF7AA2';
      c.clearRect(0, 0, W, H);
      c.fillStyle = PAPER; c.fillRect(0, 0, W, H);
      // left red panel
      var P = 720;
      c.fillStyle = RED; c.fillRect(0, 0, P, H);
      if (logoW) { var lw = 520, lh = lw * logoW.height / logoW.width; c.drawImage(logoW, (P - lw) / 2, 150, lw, lh); }
      c.fillStyle = '#fff'; c.textAlign = 'center';
      c.font = '700 30px "Archivo Narrow", sans-serif'; spaced(c, 'DRINKS NETWORK EDUCATION', P / 2, 470, 7);
      c.fillStyle = 'rgba(255,255,255,.6)'; c.fillRect(P / 2 - 60, 510, 120, 4);
      c.fillStyle = '#fff'; c.font = '400 92px Anton, Impact, sans-serif';
      wrap(c, d.course.toUpperCase(), P / 2, 640, P - 140, 96);
      c.font = '700 28px "Archivo Narrow", sans-serif'; c.fillStyle = '#FFE3E0';
      spaced(c, d.lessons + ' VIDEO LESSONS', P / 2, 960, 4);
      spaced(c, 'KNOWLEDGE CHECKS PASSED', P / 2, 1004, 4);
      // seal
      var sx = P / 2, sy = 1200;
      c.beginPath(); c.arc(sx, sy, 120, 0, Math.PI * 2); c.fillStyle = NAVY; c.fill();
      c.lineWidth = 6; c.strokeStyle = '#fff'; c.beginPath(); c.arc(sx, sy, 104, 0, Math.PI * 2); c.stroke();
      star(c, sx, sy, 62, 26, '#fff');
      c.fillStyle = '#fff'; c.font = '700 24px "Archivo Narrow", sans-serif'; spaced(c, 'CERTIFIED · ' + d.date.getFullYear(), sx, sy + 168, 5);
      if (ice) { var ih = 120; c.save(); c.beginPath(); c.rect(0, H - ih, P, ih); c.clip(); c.drawImage(ice, 0, H - ih, ice.width * ih / ice.height, ih); c.restore(); }
      // right panel
      var X = P + 140, R = W - 140;
      c.textAlign = 'left';
      c.strokeStyle = INK; c.lineWidth = 4; c.strokeRect(P + 60, 60, W - P - 120, H - 120);
      c.fillStyle = RED; c.font = '700 34px "Archivo Narrow", sans-serif'; spaced(c, 'CERTIFICATE OF COMPLETION', X, 230, 9, 'left');
      c.fillStyle = INK; c.font = 'italic 400 52px "Source Serif 4", Georgia, serif'; c.fillText('This certifies that', X, 340);
      var name = d.name, size = 190;
      c.font = '400 ' + size + 'px Anton, Impact, sans-serif';
      while (c.measureText(name.toUpperCase()).width > R - X && size > 80) { size -= 6; c.font = '400 ' + size + 'px Anton, Impact, sans-serif'; }
      c.fillStyle = NAVY; c.fillText(name.toUpperCase(), X, 340 + size * 0.95 + 20);
      var ly = 340 + size + 70;
      c.fillStyle = RED; c.fillRect(X, ly, R - X, 8);
      c.fillStyle = INK; c.font = 'italic 400 46px "Source Serif 4", Georgia, serif';
      c.fillText('has completed the Drinks Network course', X, ly + 100);
      c.font = '400 96px Anton, Impact, sans-serif'; c.fillStyle = RED; c.fillText(d.course.toUpperCase(), X, ly + 215);
      c.fillStyle = '#3A3631'; c.font = '400 36px "Source Serif 4", Georgia, serif';
      c.fillText('Every lesson watched, reviewed and passed with at least 80% on the knowledge checks.', X, ly + 290);
      // signature + details
      var by = H - 270;
      c.strokeStyle = INK; c.lineWidth = 2;
      c.beginPath(); c.moveTo(X, by); c.lineTo(X + 560, by); c.stroke();
      c.beginPath(); c.moveTo(X + 700, by); c.lineTo(X + 1120, by); c.stroke();
      c.fillStyle = INK; c.font = 'italic 600 54px "Source Serif 4", Georgia, serif'; c.fillText('Hayden Wood', X + 10, by - 22);
      c.font = '600 44px "Source Serif 4", Georgia, serif';
      c.fillText(d.date.toLocaleDateString('en-AU', { day: 'numeric', month: 'long', year: 'numeric' }), X + 710, by - 22);
      c.fillStyle = '#5A554D'; c.font = '700 24px "Archivo Narrow", sans-serif';
      spaced(c, 'HAYDEN WOOD · FOUNDER, DRINKS NETWORK', X, by + 44, 3, 'left');
      spaced(c, 'DATE OF COMPLETION', X + 700, by + 44, 3, 'left');
      c.fillStyle = '#8A8378'; c.font = '700 22px "Archivo Narrow", sans-serif';
      spaced(c, 'CERTIFICATE NO. ' + d.id + '  ·  SITE.DRINKSNETWORK.COM.AU/COURSES', X, H - 120, 3, 'left');
      if (logoR) { var rw = 260, rh = rw * logoR.height / logoR.width; c.drawImage(logoR, R - rw, H - 120 - rh + 10, rw, rh); }
      if (wave) { var ww = 560, wh = ww * wave.height / wave.width; c.globalAlpha = .9; c.drawImage(wave, W - ww - 64, 64, ww, wh); c.globalAlpha = 1; }
    });
  }
  function spaced(c, t, x, y, sp, align) {
    var w = 0, i; for (i = 0; i < t.length; i++) w += c.measureText(t[i]).width + sp; w -= sp;
    var sx = align === 'left' ? x : x - w / 2, keep = c.textAlign; c.textAlign = 'left';
    for (i = 0; i < t.length; i++) { c.fillText(t[i], sx, y); sx += c.measureText(t[i]).width + sp; }
    c.textAlign = keep;
  }
  function wrap(c, t, x, y, max, lh) {
    var words = t.split(' '), line = '', lines = [];
    words.forEach(function (w) { var test = line ? line + ' ' + w : w; if (c.measureText(test).width > max && line) { lines.push(line); line = w; } else line = test; });
    lines.push(line);
    lines.forEach(function (ln, k) { c.fillText(ln, x, y + k * lh); });
  }
  function star(c, x, y, R, r, col) {
    c.beginPath();
    for (var k = 0; k < 10; k++) { var a = -Math.PI / 2 + k * Math.PI / 5, rad = k % 2 ? r : R; c.lineTo(x + Math.cos(a) * rad, y + Math.sin(a) * rad); }
    c.closePath(); c.fillStyle = col; c.fill();
  }

  function stopSpeech() { if ('speechSynthesis' in window) speechSynthesis.cancel(); }
})();
