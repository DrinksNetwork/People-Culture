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
    var fonts = ['400 120px Anton', '700 40px "Archivo Narrow"', 'italic 400 60px "Source Serif 4"', '600 40px "Source Serif 4"', 'italic 600 60px "Source Serif 4"'];
    var ready = document.fonts && document.fonts.load ? Promise.all(fonts.map(function (f) { return document.fonts.load(f).catch(function () {}); })) : Promise.resolve();
    return Promise.all([ready, img(asset('/media/logos/drinks-network-script-red.png')), img(asset('/media/courses/cert-band.png'))]).then(function (r) {
      var logo = r[1], band = r[2];
      var c = cv.getContext('2d'), W = cv.width, H = cv.height;
      var TAN = '#EEE1CB', TAN2 = '#E0CDAE', LINE = '#CDB592', RED = '#D3221B', NAVY = '#1E2552', INK = '#2A2320', MUTED = '#7A6A55';
      var ANTON = 'Anton, Impact, sans-serif', NARROW = '"Archivo Narrow", "Arial Narrow", sans-serif', SERIF = '"Source Serif 4", Georgia, serif';
      c.clearRect(0, 0, W, H);
      // paper: light tan with a soft warm glow
      c.fillStyle = TAN; c.fillRect(0, 0, W, H);
      var g = c.createRadialGradient(W * 0.35, H * 0.3, 100, W * 0.35, H * 0.3, W * 0.8);
      g.addColorStop(0, 'rgba(255,250,240,.6)'); g.addColorStop(1, 'rgba(255,252,246,0)');
      c.fillStyle = g; c.fillRect(0, 0, W, H);
      // base: crew on ice, finishing in the style-guide wave
      if (band) c.drawImage(band, 0, H - band.height * (W / band.width), W, band.height * (W / band.width));
      // frame
      c.strokeStyle = LINE; c.lineWidth = 3; c.strokeRect(48, 48, W - 96, H - 96);
      c.lineWidth = 1; c.strokeRect(64, 64, W - 128, H - 128);
      // masthead
      var X = 170;
      if (logo) { var lw = 430, lh = lw * logo.height / logo.width; c.drawImage(logo, X - 10, 120, lw, lh); }
      c.fillStyle = LINE; c.fillRect(X + 450, 150, 3, 96);
      c.fillStyle = NAVY; c.font = '700 30px ' + NARROW; spaced(c, 'EDUCATION', X + 485, 192, 9, 'left');
      c.fillStyle = MUTED; c.font = '700 22px ' + NARROW; spaced(c, 'COURSES FOR THE DRINKS TRADE', X + 485, 232, 5, 'left');
      c.textAlign = 'right';
      c.fillStyle = MUTED; c.font = '700 22px ' + NARROW; spaced(c, 'CERTIFICATE NO.', W - 170, 172, 5, 'right');
      c.fillStyle = NAVY; c.font = '700 34px ' + NARROW; spaced(c, d.id || '', W - 170, 216, 4, 'right');
      c.textAlign = 'left';
      // seal
      seal(c, W - 420, 560, 196, d.date.getFullYear(), { NAVY: NAVY, RED: RED, TAN: TAN, ANTON: ANTON, NARROW: NARROW });
      // body
      var maxW = W - 170 - 520 - X;
      c.fillStyle = RED; c.font = '700 34px ' + NARROW; spaced(c, 'CERTIFICATE OF COMPLETION', X, 400, 11, 'left');
      c.fillStyle = INK; c.font = 'italic 400 52px ' + SERIF; c.fillText('This certifies that', X, 490);
      // name: 140px at most, shrinking to 76px; very long names wrap onto two lines
      var name = d.name.toUpperCase(), size = 140;
      c.font = '400 ' + size + 'px ' + ANTON;
      while (c.measureText(name).width > maxW && size > 76) { size -= 4; c.font = '400 ' + size + 'px ' + ANTON; }
      var nameLines = [name];
      if (c.measureText(name).width > maxW) { size = 76; c.font = '400 ' + size + 'px ' + ANTON; nameLines = lineWrap(c, name, maxW).slice(0, 2); }
      var ny = 490 + size * 0.92 + 26;
      c.fillStyle = NAVY;
      nameLines.forEach(function (ln, k) { c.fillText(ln, X, ny + k * size * 1.04); });
      var rw = Math.max(520, Math.min(maxW, Math.max.apply(null, nameLines.map(function (ln) { return c.measureText(ln).width; }))));
      ny += (nameLines.length - 1) * size * 1.04;
      c.fillStyle = RED; c.fillRect(X, ny + 34, rw, 8);
      c.fillStyle = TAN2; c.fillRect(X + rw + 18, ny + 34, 8, 8); c.fillRect(X + rw + 38, ny + 34, 8, 8);
      c.fillStyle = INK; c.font = 'italic 400 44px ' + SERIF; c.fillText('has successfully completed the Drinks Network course', X, ny + 126);
      // course title: one line if it fits (shrinking down to 64px), otherwise two lines
      var title = d.course.toUpperCase(), ts = 100;
      c.font = '400 ' + ts + 'px ' + ANTON;
      while (c.measureText(title).width > maxW && ts > 64) { ts -= 4; c.font = '400 ' + ts + 'px ' + ANTON; }
      var lines = [title];
      if (c.measureText(title).width > maxW) { ts = 70; c.font = '400 ' + ts + 'px ' + ANTON; lines = lineWrap(c, title, maxW).slice(0, 2); }
      var cy = ny + 140 + ts * 0.92;
      c.fillStyle = RED; lines.forEach(function (ln, k) { c.fillText(ln, X, cy + k * ts * 1.04); });
      cy += (lines.length - 1) * ts * 1.04;
      c.fillStyle = MUTED; c.font = '700 26px ' + NARROW;
      spaced(c, d.lessons + ' VIDEO LESSONS   ·   EVERY KNOWLEDGE CHECK PASSED AT 80% OR MORE', X, cy + 72, 4, 'left');
      c.fillStyle = INK; c.font = 'italic 400 34px ' + SERIF;
      lineWrap(c, 'Drinks Network courses are written and developed by drinks industry leaders to build awareness and confidence in the fundamentals of each category and subject.', maxW - 120).forEach(function (ln, k) { c.fillText(ln, X, cy + 140 + k * 46); });
      // sign-off, sitting on the tan to the left of the crew
      var sy = H - 450;
      // pen-scribble signature in navy ink
      scribble(c, X + 24, sy - 28, 1.18, NAVY);
      c.fillStyle = INK; c.fillRect(X, sy + 24, 560, 2);
      c.fillStyle = MUTED; c.font = '700 22px ' + NARROW; spaced(c, 'HAYDEN WOOD  ·  FOUNDER, DRINKS NETWORK', X, sy + 64, 4, 'left');
      stamp(c, X + 920, sy + 10, 158, { RED: '#C21F27', ANTON: ANTON, NARROW: NARROW, date: d.date.toLocaleDateString('en-AU', { day: '2-digit', month: '2-digit', year: 'numeric' }).replace(/\//g, '.') });
      var dy = sy + 170;
      c.fillStyle = INK; c.font = '600 44px ' + SERIF;
      c.fillText(d.date.toLocaleDateString('en-AU', { day: 'numeric', month: 'long', year: 'numeric' }), X + 6, dy);
      c.fillRect(X, dy + 24, 560, 2);
      c.fillStyle = MUTED; c.font = '700 22px ' + NARROW; spaced(c, 'DATE OF COMPLETION  ·  SITE.DRINKSNETWORK.COM.AU/COURSES', X, dy + 64, 4, 'left');
    });
  }
  window.DNCertificate = { draw: function (cv, d) { return drawCertificate(cv, d); } };
  function scribble(c, x, y, k, col) {
    // a quick looping signature: tall initial strokes, a run of uneven loops, an underline flourish
    var pts = [], seed = 7;
    function rnd() { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; }
    function add(sg, step) { for (var t = 0; t <= 1.0001; t += step || 0.03) pts.push(bez(sg, t)); }
    add([[0, 26], [6, -40], [18, -112], [26, -104]]);
    add([[26, -104], [34, -96], [12, 10], [10, 46]]);
    add([[10, 46], [14, 4], [44, -30], [66, -34]]);
    add([[66, -34], [74, -80], [92, -118], [98, -98]]);
    add([[98, -98], [104, -78], [80, 0], [84, 30]]);
    add([[84, 30], [92, 10], [104, -6], [118, -4]]);
    // uneven cursive loops, getting smaller and quicker
    var xs = 118, base = 0;
    for (var i = 0; i < 7; i++) {
      var w = 34 + rnd() * 14, h = (58 - i * 5) * (0.8 + rnd() * 0.45), d = 9 + rnd() * 6;
      for (var t = 0; t <= Math.PI * 2; t += 0.12) pts.push([xs + w * t / (Math.PI * 2) - d * Math.sin(t), base - h * (1 - Math.cos(t)) / 2 + t * 0.4]);
      xs += w; base += 1.5;
    }
    // flick up, then the long underline sweeping back under the name
    add([[xs, base], [xs + 30, base - 20], [xs + 70, base - 60], [xs + 64, base - 40]]);
    add([[xs + 64, base - 40], [xs + 40, base + 20], [xs - 60, base + 40], [xs - 180, base + 44]], 0.02);
    add([[xs - 180, base + 44], [xs - 300, base + 48], [60, base + 36], [-20, base + 58]], 0.02);
    c.save(); c.translate(x, y); c.rotate(-0.07); c.scale(k, k);
    c.strokeStyle = col; c.lineCap = 'round'; c.lineJoin = 'round';
    for (var j = 1; j < pts.length; j++) {
      var p0 = pts[j - 1], p1 = pts[j], dx = p1[0] - p0[0], dy = p1[1] - p0[1], sp = Math.sqrt(dx * dx + dy * dy);
      var taper = Math.min(1, j / 12, (pts.length - j) / 40);
      // pressure: heavier on down-strokes, lighter on fast or rising strokes
      var press = 5.2 + (dy > 0 ? 1.6 : -0.8) - Math.min(sp, 14) * 0.18;
      c.lineWidth = Math.max(1.2, press * taper);
      c.beginPath(); c.moveTo(p0[0], p0[1]); c.lineTo(p1[0], p1[1]); c.stroke();
    }
    c.restore();
  }
  function bez(p, t) {
    var u = 1 - t;
    return [u * u * u * p[0][0] + 3 * u * u * t * p[1][0] + 3 * u * t * t * p[2][0] + t * t * t * p[3][0],
            u * u * u * p[0][1] + 3 * u * u * t * p[1][1] + 3 * u * t * t * p[2][1] + t * t * t * p[3][1]];
  }
  function lineWrap(c, t, max) {
    var words = t.split(' '), line = '', out = [];
    words.forEach(function (w) { var test = line ? line + ' ' + w : w; if (c.measureText(test).width > max && line) { out.push(line); line = w; } else line = test; });
    out.push(line); return out;
  }
  function seal(c, x, y, R, year, k) {
    c.save();
    // ribbon tails
    c.fillStyle = k.RED;
    [[-1, -0.32], [1, 0.32]].forEach(function (s) {
      c.save(); c.translate(x + s[0] * R * 0.38, y + R * 0.62); c.rotate(s[1]);
      c.beginPath(); c.moveTo(-58, 0); c.lineTo(58, 0); c.lineTo(58, 250); c.lineTo(0, 205); c.lineTo(-58, 250); c.closePath(); c.fill();
      c.restore();
    });
    // scalloped rim
    c.beginPath();
    for (var i = 0; i <= 72; i++) { var a = i / 72 * Math.PI * 2, rr = R + (i % 2 ? 0 : 12); c.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); }
    c.closePath(); c.fillStyle = k.NAVY; c.fill();
    c.lineWidth = 4; c.strokeStyle = k.TAN; c.beginPath(); c.arc(x, y, R - 26, 0, Math.PI * 2); c.stroke();
    c.lineWidth = 2; c.beginPath(); c.arc(x, y, R - 92, 0, Math.PI * 2); c.stroke();
    // ring text
    c.fillStyle = k.TAN; c.font = '700 30px ' + k.NARROW;
    ringText(c, '★  DRINKS NETWORK EDUCATION  ★  COURSE COMPLETE  ', x, y, R - 60);
    // centre
    c.textAlign = 'center'; c.fillStyle = '#fff';
    c.font = '400 92px ' + k.ANTON; c.fillText(String(year), x, y + 30);
    c.font = '700 22px ' + k.NARROW; c.fillStyle = k.TAN;
    spaced(c, 'CERTIFIED', x, y + 72, 6);
    star5(c, x, y - 74, 22, 9, k.RED);
    c.restore();
  }
  function stamp(c, x, y, R, k) {
    // official rubber stamp, drawn off-screen then roughed up so the ink looks pressed
    var S = R * 2 + 60, o = document.createElement('canvas'); o.width = S; o.height = S;
    var s = o.getContext('2d'), m = S / 2, inner = R - 50;
    s.strokeStyle = k.RED; s.fillStyle = k.RED;
    s.lineWidth = 10; s.beginPath(); s.arc(m, m, R, 0, Math.PI * 2); s.stroke();
    s.lineWidth = 3; s.beginPath(); s.arc(m, m, R - 14, 0, Math.PI * 2); s.stroke();
    s.lineWidth = 4; s.beginPath(); s.arc(m, m, inner, 0, Math.PI * 2); s.stroke();
    s.font = '700 25px ' + k.NARROW; ringText(s, '★ DRINKS NETWORK ★ OFFICIAL EDUCATION ', m, m, R - 32);
    s.textAlign = 'center';
    s.font = '400 44px ' + k.ANTON; s.fillText('100%', m, m - 50);
    // PASSED band, knocked out of solid ink
    s.fillRect(m - R - 18, m - 40, 2 * R + 36, 80);
    s.globalCompositeOperation = 'destination-out';
    s.font = '400 68px ' + k.ANTON; s.fillText('PASSED', m, m + 25);
    s.globalCompositeOperation = 'source-over';
    s.font = '700 22px ' + k.NARROW; spaced(s, k.date, m, m + 70, 3);
    // wear
    s.globalCompositeOperation = 'destination-out';
    var seed = 11; function rnd() { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; }
    for (var i = 0; i < 520; i++) { s.globalAlpha = 0.2 + rnd() * 0.55; s.beginPath(); s.arc(rnd() * S, rnd() * S, 0.6 + rnd() * 2.2, 0, Math.PI * 2); s.fill(); }
    var gr = s.createLinearGradient(0, 0, S, S); gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(0.72, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,0,.55)');
    s.globalAlpha = 1; s.fillStyle = gr; s.fillRect(0, 0, S, S);
    s.globalCompositeOperation = 'source-over';
    c.save(); c.translate(x, y); c.rotate(-0.2); c.globalAlpha = 0.9; c.globalCompositeOperation = 'multiply'; c.drawImage(o, -m, -m); c.restore();
  }
  function ringText(c, t, x, y, r) {
    var total = 0, i, ws = [];
    for (i = 0; i < t.length; i++) { ws.push(c.measureText(t[i]).width + 3); total += ws[i]; }
    var scale = (Math.PI * 2 * r) / total, a = -Math.PI / 2;
    c.textAlign = 'center';
    for (i = 0; i < t.length; i++) {
      var step = ws[i] * scale / r, mid = a + step / 2;
      c.save(); c.translate(x + Math.cos(mid) * r, y + Math.sin(mid) * r); c.rotate(mid + Math.PI / 2);
      c.fillText(t[i], 0, 10); c.restore(); a += step;
    }
    c.textAlign = 'left';
  }
  function star5(c, x, y, R, r, col) {
    c.beginPath();
    for (var k = 0; k < 10; k++) { var a = -Math.PI / 2 + k * Math.PI / 5, rad = k % 2 ? r : R; c.lineTo(x + Math.cos(a) * rad, y + Math.sin(a) * rad); }
    c.closePath(); c.fillStyle = col; c.fill();
  }
  function spaced(c, t, x, y, sp, align) {
    var w = 0, i; for (i = 0; i < t.length; i++) w += c.measureText(t[i]).width + sp; w -= sp;
    var sx = align === 'left' ? x : align === 'right' ? x - w : x - w / 2, keep = c.textAlign; c.textAlign = 'left';
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
