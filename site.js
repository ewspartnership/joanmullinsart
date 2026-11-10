document.documentElement.classList.add('js');

// A page opened from a link starts at the top. Some viewers (including the Claude preview) keep the
// previous page's scroll position. Going Back still returns to where you were, and #links still jump.
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

// Switch between the painting and the wall view, on a painting's page and in each gallery row.
(function () {
  document.querySelectorAll('.viewer').forEach(function (viewer) {
    var buttons = viewer.querySelectorAll('.view-btn');
    if (!buttons.length) return;
    function show(name) {
      viewer.querySelectorAll('.pane').forEach(function (p) { p.hidden = p.getAttribute('data-pane') !== name; });
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-view') === name)); });
    }
    buttons.forEach(function (b) { b.addEventListener('click', function () { show(b.getAttribute('data-view')); }); });
    show('painting');
  });
})();

// Larger picture: opens over the page; closes with Close, Escape, or a tap on the picture or background.
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

// Gallery pages: "Show only paintings for sale".
(function () {
  document.querySelectorAll('.only-sale').forEach(function (box) {
    var list = box.closest('section').querySelector('.exhibition');
    box.addEventListener('change', function () { list.classList.toggle('only-sale-on', box.checked); });
  });
})();

// Enquiry form: choose the painting from the link (#w-117); without a form service, open the
// visitor's email program with the message filled in, and show the message to copy as well.
(function () {
  var form = document.getElementById('enq');
  if (!form) return;
  var select = document.getElementById('f-painting');
  var id = (location.hash || '').slice(1);
  if (id && select.querySelector('option[value="' + id + '"]')) {
    select.value = id;
    form.scrollIntoView();
  }
  var to = form.getAttribute('data-mailto');
  if (!to) return; // a form service is set up: the form posts normally
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    if (!form.reportValidity()) return;
    var opt = select.options[select.selectedIndex];
    var about = select.value ? opt.textContent : 'A general question';
    var subject = 'Enquiry: ' + about;
    var body = document.getElementById('f-message').value + '\n\n' + document.getElementById('f-name').value +
      '\n' + document.getElementById('f-email').value + '\n\n(Sent from joanmullinsart.co.uk about: ' + about + ')';
    var copy = document.getElementById('enq-copy');
    copy.value = 'To: ' + to + '\nSubject: ' + subject + '\n\n' + body;
    document.getElementById('enq-fallback').hidden = false;
    window.location.href = 'mailto:' + to + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  });
  document.getElementById('enq-copy-btn').addEventListener('click', function () {
    var copy = document.getElementById('enq-copy'), btn = this;
    function done() { btn.textContent = 'Copied'; }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(copy.value).then(done, function () { copy.select(); });
    } else { copy.select(); }
  });
})();
