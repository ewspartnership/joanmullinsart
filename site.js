// A page opened from a link starts at the top. Some viewers (including the Claude preview) keep the
// previous page's scroll position, which left people looking at "More from" instead of the painting.
// Going Back still returns to where you were, and links to a #section still jump to it.
(function () {
  try {
    var nav = performance.getEntriesByType && performance.getEntriesByType('navigation')[0];
    var type = nav ? nav.type : (performance.navigation && performance.navigation.type === 2 ? 'back_forward' : 'navigate');
    if (type === 'navigate' && !location.hash) {
      window.scrollTo(0, 0);
      window.addEventListener('load', function () { window.scrollTo(0, 0); });
    }
  } catch (e) { /* leave the scroll position alone */ }
})();

// Larger picture on a painting's page: opens over the page, closes with the Close button,
// the Escape key, or a tap anywhere on the dark background or the picture.
(function () {
  var dialog = document.getElementById('zoom');
  if (!dialog || typeof dialog.showModal !== 'function') return; // older browsers just open the picture file
  var big = dialog.querySelector('img');
  document.querySelectorAll('a[data-zoom]').forEach(function (link) {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      big.src = link.getAttribute('href');
      var small = link.querySelector('img');
      big.alt = small ? small.alt : '';
      dialog.showModal();
      dialog.querySelector('.zoom-close').focus();
    });
  });
  dialog.querySelector('.zoom-close').addEventListener('click', function () { dialog.close(); });
  dialog.addEventListener('click', function (event) {
    if (event.target === dialog || event.target === big) dialog.close();
  });
})();
