/* Homepage: the hero video with its step readout kept in sync, the step
   explorer, and the download bar on phones. Step data: js/run.js. */
(function () {
  var RUN = window.SV_RUN;
  if (!RUN) return;
  // Steps are numbered by the touchdown that ends them. Touchdown 1 out of the
  // blocks is step 1 and has no length or times yet; the line from it to the
  // next touchdown is step 2, drawn on the video the moment that foot lands.
  // (The analysis stores each step's values on the touchdown that starts it.)
  var touchdowns = RUN.steps;
  var steps = [];
  touchdowns.forEach(function (s) {
    var next = touchdowns.filter(function (x) { return x.n === s.n + 1; })[0];
    if (!s.regular || s.len == null || !next) return;
    steps.push({
      n: next.n, foot: next.foot,
      len: s.len, contact: s.contact, flight: s.flight, speed: s.speed,
      done: Math.ceil(next.td * 30 - 1e-6) / 30 + 0.001,   // first video frame showing its line
      img: 'assets/run/steps/step-' + (next.n < 10 ? '0' : '') + next.n + '.jpg'
    });
  });
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var SIDE = { L: 'Left', R: 'Right' };
  var COLOUR = { L: '#3aa8f0', R: '#ff6a3d' };
  var maxLen = Math.max.apply(null, steps.map(function (s) { return s.len; }));
  function $(sel, root) { return (root || document).querySelector(sel); }

  /* ---------------- Hero: video + live readout ---------------- */
  (function hero() {
    var player = $('#player');
    if (!player) return;
    var video = $('video', player);
    var chip = $('[data-chip]', player), chipDot = $('[data-chip-dot]', player);
    var head = $('[data-head]', player), time = $('[data-time]', player);
    var ticksEl = $('[data-ticks]', player), play = $('.player-play', player);
    var ro = {
      n: $('[data-ro-n]'), total: $('[data-ro-total]'), foot: $('[data-ro-foot]'), len: $('[data-ro-len]'),
      contact: $('[data-ro-contact]'), flight: $('[data-ro-flight]'), bars: $('[data-ro-bars]')
    };
    var dur = RUN.duration;
    var pushAt = (1.17 - RUN.videoStartRun) * RUN.slow;   // leaves the blocks

    ro.total.textContent = touchdowns.length;
    var ticks = touchdowns.map(function (s) {
      var i = document.createElement('i');
      i.style.left = (s.td / dur * 100) + '%';
      i.style.background = COLOUR[s.foot];
      ticksEl.appendChild(i);
      return i;
    });
    var bars = steps.map(function (s) {
      var i = document.createElement('i');
      i.style.setProperty('--h', Math.round(s.len / maxLen * 100));
      ro.bars.appendChild(i);
      return i;
    });

    var cur = null;
    function show(k) {
      cur = k;
      var s = steps[k];
      ro.n.textContent = s ? s.n : '–';
      ro.foot.textContent = s ? SIDE[s.foot] : '';
      if (s) ro.foot.setAttribute('data-side', s.foot); else ro.foot.removeAttribute('data-side');
      ro.len.textContent = s ? s.len.toFixed(2) : '–';
      ro.contact.textContent = s && s.contact ? '≈' + s.contact + ' ms' : '–';
      ro.flight.textContent = s && s.flight ? '≈' + s.flight + ' ms' : '–';
      bars.forEach(function (b, j) {
        b.className = j <= k ? steps[j].foot : '';
        if (j === k && !reduceMotion) { void b.offsetWidth; b.classList.add('on'); }
      });
    }
    function tick() {
      var t = video.currentTime || 0;
      var k = -1, land = -1, j;
      for (j = 0; j < steps.length; j++) if (steps[j].done <= t) k = j;          // its line is on the video
      for (j = 0; j < touchdowns.length; j++) if (touchdowns[j].td <= t) land = j; // the latest touchdown
      if (k !== cur) show(k);
      var s = touchdowns[land];
      chip.textContent = s
        ? 'Step ' + s.n + ' · ' + SIDE[s.foot] + (t - s.td < 0.5 ? ' · Touchdown' : '')
        : (t < pushAt ? 'Set position' : 'Out of the blocks');
      chipDot.style.background = s ? COLOUR[s.foot] : '#fff';
      ticks.forEach(function (el, j) { el.classList.toggle('on', j <= land); });
      head.style.left = Math.min(t / dur * 100, 100) + '%';
      time.textContent = (RUN.videoStartRun + t / RUN.slow).toFixed(2) + ' s';
    }
    var raf = 0;
    function loop() { tick(); raf = requestAnimationFrame(loop); }
    function start() { if (!raf) loop(); }
    function stop() { cancelAnimationFrame(raf); raf = 0; tick(); }

    var small = window.matchMedia('(max-width: 900px)').matches;
    video.src = small ? 'assets/run/hero-sm.mp4' : 'assets/run/hero.mp4';
    video.addEventListener('play', function () { play.hidden = true; start(); });
    video.addEventListener('pause', stop);
    video.addEventListener('seeked', tick);
    play.addEventListener('click', function () { video.play(); });
    show(-1); tick();

    function tryPlay() {
      var p = video.play();
      if (p && p.catch) p.catch(function () { play.hidden = false; });
    }
    if (reduceMotion) { play.hidden = false; return; }
    // Play only while the hero is on screen.
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) tryPlay(); else video.pause(); });
      }, { threshold: 0.2 }).observe(player);
    } else {
      tryPlay();
    }
  })();

  /* ---------------- Every step: tap a bar to see that step ---------------- */
  (function explorer() {
    var ex = $('[data-explorer]');
    if (!ex) return;
    var M = {
      len: { label: 'Step length', unit: 'm', fmt: function (v) { return v.toFixed(2); } },
      contact: { label: 'Ground contact', unit: 'ms', approx: true, fmt: function (v) { return String(Math.round(v)); } },
      flight: { label: 'Flight time', unit: 'ms', approx: true, fmt: function (v) { return String(Math.round(v)); } },
      speed: { label: 'Speed', unit: 'm/s', fmt: function (v) { return v.toFixed(1); } }
    };
    var img = $('[data-ex-img]', ex), chip = $('[data-ex-chip]', ex), dot = $('[data-ex-dot]', ex);
    var valueEl = $('[data-ex-value]', ex), unitEl = $('[data-ex-unit]', ex), labelEl = $('[data-ex-label]', ex);
    var barsEl = $('[data-ex-bars]', ex), axis = $('[data-ex-axis]', ex), stats = $('[data-ex-stats]', ex);
    var tabs = Array.prototype.slice.call(ex.querySelectorAll('[data-measure]'));
    var measure = 'len', sel = 3;
    function src(s) { return s.img; }

    var buttons = steps.map(function (s, k) {
      var b = document.createElement('button');
      b.type = 'button';
      b.style.setProperty('--c', COLOUR[s.foot]);
      b.appendChild(document.createElement('i'));
      b.addEventListener('click', function () { select(k); });
      barsEl.appendChild(b);
      var a = document.createElement('span');
      a.textContent = k % 4 === 0 ? s.n : '';
      axis.appendChild(a);
      return b;
    });
    barsEl.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
        e.preventDefault();
        select(Math.max(0, Math.min(steps.length - 1, sel + (e.key === 'ArrowRight' ? 1 : -1))));
        buttons[sel].focus();
      }
    });

    function fmt(key, v) { return v == null ? '–' : (M[key].approx ? '≈' : '') + M[key].fmt(v); }
    function heights() {
      var vals = steps.map(function (s) { return s[measure]; });
      var max = Math.max.apply(null, vals.filter(function (v) { return v != null; }));
      buttons.forEach(function (b, k) {
        var v = vals[k];
        b.firstChild.style.setProperty('--h', v == null ? 0 : Math.round(v / max * 100));
        b.setAttribute('aria-label', 'Step ' + steps[k].n + ', ' + SIDE[steps[k].foot] + ': ' + fmt(measure, v) + ' ' + M[measure].unit);
      });
    }
    function select(k) {
      sel = k;
      var s = steps[k];
      buttons.forEach(function (b, j) { b.setAttribute('aria-pressed', j === k ? 'true' : 'false'); });
      valueEl.textContent = fmt(measure, s[measure]);
      unitEl.textContent = M[measure].unit;
      labelEl.textContent = M[measure].label + ' · step ' + s.n;
      chip.textContent = 'Step ' + s.n + ' · ' + SIDE[s.foot];
      dot.style.background = COLOUR[s.foot];
      img.src = src(s);
      img.alt = 'Step ' + s.n + ', ' + SIDE[s.foot].toLowerCase() + ' foot: ' + s.len.toFixed(2) + ' m, shown on the video';
      stats.innerHTML = ['len', 'contact', 'flight', 'speed'].map(function (key) {
        return '<div><dt>' + M[key].label.replace('Step length', 'Length').replace('Ground contact', 'Contact').replace('Flight time', 'Flight') +
          '</dt><dd>' + fmt(key, s[key]) + ' ' + M[key].unit + '</dd></div>';
      }).join('');
    }
    tabs.forEach(function (t) {
      t.addEventListener('click', function () {
        measure = t.getAttribute('data-measure');
        tabs.forEach(function (o) { o.setAttribute('aria-selected', o === t ? 'true' : 'false'); });
        heights(); select(sel);
      });
    });
    heights(); select(sel);

    // Fetch every step's frame once the explorer is close, so taps are instant.
    function preload() { steps.forEach(function (s) { new Image().src = src(s); }); }
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (es) {
        if (es[0].isIntersecting) { preload(); io.disconnect(); }
      }, { rootMargin: '400px 0px' });
      io.observe(ex);
    } else {
      preload();
    }
  })();

  /* ---------------- Download bar on phones ---------------- */
  (function sticky() {
    var bar = $('[data-sticky]'), heroCta = $('[data-hero-cta]'), finish = $('#download');
    if (!bar || !heroCta || !finish) return;
    function update() {
      var show = heroCta.getBoundingClientRect().bottom < 0 &&
        finish.getBoundingClientRect().top > window.innerHeight * 0.9;
      bar.classList.toggle('show', show);
    }
    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  })();
})();
