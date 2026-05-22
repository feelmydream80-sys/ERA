(function () {
  'use strict';

  function isInView(el) {
    var rect = el.getBoundingClientRect();
    var vh = window.innerHeight || document.documentElement.clientHeight;
    return rect.top < vh - 100 && rect.bottom > 0;
  }

  var sections = document.querySelectorAll('.about-section');
  var counted = {};

  function checkVisibility() {
    sections.forEach(function (sec) {
      if (isInView(sec)) {
        sec.classList.add('visible');
        var nums = sec.querySelectorAll('.stat-number, .status-number');
        nums.forEach(function (el) {
          var key = el.dataset.target;
          if (key && !counted[key]) {
            counted[key] = true;
            countUp(el, parseInt(el.dataset.target, 10));
          }
        });
      }
    });
  }

  function countUp(el, target) {
    var duration = 1200;
    var start = performance.now();

    function step(now) {
      var elapsed = now - start;
      var progress = Math.min(elapsed / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(eased * target);
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        el.textContent = target;
      }
    }
    requestAnimationFrame(step);
  }

  window.addEventListener('scroll', checkVisibility, { passive: true });
  window.addEventListener('resize', checkVisibility, { passive: true });
  checkVisibility();

  var crawlerCards = document.querySelectorAll('.crawler-card');
  crawlerCards.forEach(function (card) {
    var header = card.querySelector('.crawler-header');
    var targetId = header.getAttribute('data-bs-target');
    var collapseEl = document.querySelector(targetId);
    if (!collapseEl) return;

    collapseEl.addEventListener('show.bs.collapse', function () {
      card.style.borderColor = '#0d6efd';
    });
    collapseEl.addEventListener('hide.bs.collapse', function () {
      card.style.borderColor = '#333';
    });
  });

})();
