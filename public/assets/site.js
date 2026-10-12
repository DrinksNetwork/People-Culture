/* Drinks Network site behaviour: forms, package picker, earnings calculator, Start here funnel.
   Every form posts JSON to the RepShare secure enquiry endpoint. Set window.DN_ENQUIRY_ENDPOINT to override. */
(function () {
  'use strict';
  var ENDPOINT = window.DN_ENQUIRY_ENDPOINT || '/api/enquiries';
  var qs = new URLSearchParams(location.search);

  function utm() {
    return { utmSource: qs.get('utm_source'), utmMedium: qs.get('utm_medium'), utmCampaign: qs.get('utm_campaign') };
  }

  function collect(form) {
    var data = {};
    new FormData(form).forEach(function (v, k) {
      if (data[k] === undefined) data[k] = v;
      else data[k] = [].concat(data[k], v);
    });
    return data;
  }

  function send(payload) {
    return fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r; });
  }

  function consentWording(form) {
    var c = form.querySelector('[name=consent]');
    return c ? c.closest('label').textContent.replace(/\s+/g, ' ').trim() : null;
  }

  /* ---- Generic forms: <form data-dn-form="name" data-tags="Vendor,Trade" data-campaign="slug"> ---- */
  document.querySelectorAll('form[data-dn-form]').forEach(function (form) {
    var status = form.querySelector('.form-status');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var d = collect(form);
      var tags = (form.dataset.tags || '').split(',').filter(Boolean);
      if (d.role) tags = tags.concat(d.role);              // self-selected category
      if (d.buyer === 'yes') tags = ['Buyer'];
      var payload = Object.assign({}, d, utm(), {
        form: form.dataset.dnForm,
        campaign: form.dataset.campaign || null,
        tags: Array.from(new Set(tags)),
        pageUrl: location.href,
        consent: d.consent ? { status: 'subscribed', wording: consentWording(form) } : null
      });
      if (status) status.textContent = 'Sending…';
      send(payload).then(function () {
        form.reset();
        if (status) status.textContent = form.dataset.thanks || "Thanks. The Drinks Network team will be in touch within one business day.";
      }).catch(function () {
        if (status) status.textContent = 'Something went wrong. Please try again in a moment.';
      });
    });
  });

  /* ---- Package picker: container [data-packages], buttons [data-package="Roll Out"] ---- */
  document.querySelectorAll('[data-packages]').forEach(function (box) {
    var btns = box.querySelectorAll('[data-package]');
    function pick(name) {
      btns.forEach(function (b) {
        var on = b.dataset.package === name;
        b.setAttribute('aria-pressed', on ? 'true' : 'false');
        b.textContent = on ? 'Selected: ' + b.dataset.package : (b.dataset.label || 'Choose ' + b.dataset.package);
      });
      document.querySelectorAll('[data-selected-package]').forEach(function (el) { el.textContent = name; });
      document.querySelectorAll('input[name=package]').forEach(function (el) { el.value = name; });
    }
    btns.forEach(function (b) { b.addEventListener('click', function () { pick(b.dataset.package); }); });
    pick(box.dataset.packages || btns[0].dataset.package);
  });

  /* ---- Earnings calculator: [data-calc] containing input[type=range], [data-rate] buttons, [data-out] ---- */
  document.querySelectorAll('[data-calc]').forEach(function (box) {
    var range = box.querySelector('input[type=range]');
    var rates = box.querySelectorAll('[data-rate]');
    var rate = Number(box.dataset.calc) || 45;
    function render() {
      var h = Number(range.value);
      box.querySelectorAll('[data-hours]').forEach(function (el) { el.textContent = h; });
      box.querySelectorAll('[data-rate-out]').forEach(function (el) { el.textContent = rate; });
      box.querySelectorAll('[data-out]').forEach(function (el) { el.textContent = Math.round(h * rate * 4.33).toLocaleString('en-AU'); });
      rates.forEach(function (b) { b.setAttribute('aria-pressed', Number(b.dataset.rate) === rate ? 'true' : 'false'); });
    }
    range.addEventListener('input', render);
    rates.forEach(function (b) { b.addEventListener('click', function () { rate = Number(b.dataset.rate); render(); }); });
    render();
  });

  /* ---- Start here funnel: [data-funnel] with sections [data-step="who|details|circuit|done"] ---- */
  var funnel = document.querySelector('[data-funnel]');
  if (funnel) {
    var roles = {};
    var pre = (qs.get('role') || '').toLowerCase();
    var map = { vendor: 'Vendor', brand: 'Vendor', rep: 'Rep', partner: 'Partner' };
    if (map[pre]) roles[map[pre]] = true; else roles.Vendor = true;
    var order = ['who', 'details', 'circuit', 'done'];
    var step = 0;
    var rail = funnel.querySelectorAll('[data-rail]');

    // Funnel log: one anonymous event per step reached, linked to the final submission by sessionId.
    var FUNNEL = window.DN_FUNNEL_ENDPOINT || '/api/funnel-events';
    var sessionId;
    try { sessionId = sessionStorage.getItem('dn-start-session'); } catch (e) {}
    if (!sessionId) {
      sessionId = Date.now().toString(36) + Math.random().toString(36).slice(2, 10);
      try { sessionStorage.setItem('dn-start-session', sessionId); } catch (e) {}
    }
    var lastLogged = null;
    function logStep(name) {
      if (name === lastLogged) return;
      lastLogged = name;
      var ev = JSON.stringify(Object.assign({ sessionId: sessionId, step: name, roles: Object.keys(roles).filter(function (k) { return roles[k]; }), pageUrl: location.href, at: new Date().toISOString() }, utm()));
      try {
        if (navigator.sendBeacon) navigator.sendBeacon(FUNNEL, new Blob([ev], { type: 'application/json' }));
        else fetch(FUNNEL, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: ev, keepalive: true }).catch(function () {});
      } catch (e) {}
    }

    function show() {
      logStep(order[step]);
      funnel.querySelectorAll('[data-step]').forEach(function (s) { s.hidden = s.dataset.step !== order[step]; });
      rail.forEach(function (li, i) {
        li.style.borderBottomColor = i === step ? 'var(--red)' : 'transparent';
        li.style.color = i <= step ? 'var(--ink)' : '#8A8378';
      });
      var picked = Object.keys(roles).filter(function (k) { return roles[k]; });
      funnel.querySelectorAll('[data-role]').forEach(function (b) { b.setAttribute('aria-pressed', roles[b.dataset.role] ? 'true' : 'false'); });
      funnel.querySelectorAll('[data-role-summary]').forEach(function (el) { el.textContent = picked.length ? picked.join(' + ') : 'Choose at least one to continue.'; });
      funnel.querySelectorAll('[data-for-role]').forEach(function (el) {
        var on = el.dataset.forRole.split(',').some(function (r) { return roles[r]; });
        el.hidden = !on;
        el.querySelectorAll('input,select,textarea').forEach(function (i) { i.disabled = !on; });
      });
      var next = funnel.querySelector('[data-next-who]');
      if (next) next.disabled = picked.length === 0;
      window.scrollTo({ top: funnel.offsetTop - 10, behavior: 'smooth' });
    }

    funnel.querySelectorAll('[data-role]').forEach(function (b) {
      b.addEventListener('click', function () { roles[b.dataset.role] = !roles[b.dataset.role]; show(); });
    });
    funnel.querySelectorAll('[data-chip]').forEach(function (b) {
      b.addEventListener('click', function () { b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') === 'true' ? 'false' : 'true'); });
    });
    funnel.querySelectorAll('[data-go]').forEach(function (b) {
      b.addEventListener('click', function () {
        var dir = Number(b.dataset.go);
        if (dir > 0 && order[step] === 'details') {
          var f = funnel.querySelector('[data-step=details] form');
          if (!f.checkValidity()) { f.reportValidity(); return; }
        }
        step = Math.max(0, Math.min(order.length - 1, step + dir));
        show();
      });
    });

    var submit = funnel.querySelector('[data-submit]');
    if (submit) submit.addEventListener('click', function () {
      var f = funnel.querySelector('[data-step=details] form');
      var d = collect(f);
      var chips = function (group) {
        return Array.prototype.map.call(funnel.querySelectorAll('[data-chip="' + group + '"][aria-pressed=true]'), function (b) { return b.textContent.trim(); });
      };
      var payload = Object.assign({}, d, utm(), {
        form: 'start-here',
        sessionId: sessionId,
        tags: Object.keys(roles).filter(function (k) { return roles[k]; }),
        circuit: { city: (funnel.querySelector('[name=circuitCity]') || {}).value, venueTypes: chips('venue'), suburbs: (funnel.querySelector('[name=suburbs]') || {}).value },
        pageUrl: location.href,
        consent: d.consent ? { status: 'subscribed', wording: consentWording(f) } : null
      });
      var st = funnel.querySelector('[data-step=circuit] .form-status');
      st.textContent = 'Sending…';
      send(payload).then(function () { step = order.indexOf('done'); show(); })
        .catch(function () { st.textContent = 'Something went wrong. Please try again in a moment.'; });
    });

    show();
  }
})();
