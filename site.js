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
