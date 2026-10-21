/* Shared by every page: header border once scrolled, and fade-in on scroll. */
(function () {
  var top = document.querySelector('.top');
  if (top) {
    var onScroll = function () { top.classList.toggle('scrolled', window.scrollY > 8); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  var items = Array.prototype.slice.call(document.querySelectorAll('.reveal'));
  if (!items.length) return;
  if (!('IntersectionObserver' in window)) {
    items.forEach(function (el) { el.classList.add('in'); });
    return;
  }
  // Stagger siblings that come into view together.
  var fired = false;
  var io = new IntersectionObserver(function (entries) {
    var shown = 0;
    fired = true;
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.style.transitionDelay = Math.min(shown++ * 80, 320) + 'ms';
      e.target.classList.add('in');
      io.unobserve(e.target);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
  items.forEach(function (el) { io.observe(el); });
  // Never leave content hidden if the observer never fires.
  setTimeout(function () {
    if (!fired) items.forEach(function (el) { el.classList.add('in'); });
  }, 3000);
})();
