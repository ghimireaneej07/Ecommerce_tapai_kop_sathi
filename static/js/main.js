// Tapai Ko Sathi - Interactive Frontend Logic
document.addEventListener('DOMContentLoaded', function () {
  const header = document.querySelector('.tks-header');

  // Sticky Header Scroll Effect
  window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
      header.style.boxShadow = 'var(--shadow-md)';
      header.style.background = 'rgba(255, 255, 255, 0.97)';
    } else {
      header.style.boxShadow = 'none';
      header.style.background = 'rgba(255, 255, 255, 0.9)';
    }
  });

  // Mobile hamburger menu
  const hamburger = document.getElementById('tks-hamburger');
  const drawer = document.getElementById('tks-mobile-drawer');
  const overlay = document.getElementById('tks-mobile-overlay');
  const closeBtn = document.getElementById('tks-mobile-close');

  function openDrawer() {
    drawer.classList.add('is-open');
    overlay.classList.add('is-open');
    hamburger.classList.add('is-active');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    drawer.classList.remove('is-open');
    overlay.classList.remove('is-open');
    hamburger.classList.remove('is-active');
    document.body.style.overflow = '';
  }

  if (hamburger) hamburger.addEventListener('click', openDrawer);
  if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
  if (overlay) overlay.addEventListener('click', closeDrawer);

  // Close drawer on ESC
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeDrawer();
  });

  // Smooth scroll for anchors
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href === '#') return;
      e.preventDefault();
      const target = document.querySelector(href);
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
        closeDrawer();
      }
    });
  });
  // Cart interactions live in cart_ajax.js
});

