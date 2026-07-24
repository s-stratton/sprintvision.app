/* SprintVision launch waitlist.
   Progressively enhances any <form data-waitlist> to POST the email to the
   Supabase `join-waitlist` Edge Function. The publishable key is safe to expose
   in the browser (it only permits calling public endpoints). */
(function () {
  var ENDPOINT =
    'https://eespgchilqpbmtzrxacd.supabase.co/functions/v1/join-waitlist';
  var PUBLISHABLE_KEY = 'sb_publishable_cKn_qZ_YbBvfZX0vOdTUVQ_nFJbJ2Nr';

  function isValidEmail(v) {
    return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v);
  }

  function setMsg(el, text, kind) {
    if (!el) return;
    el.textContent = text;
    el.className = 'waitlist-msg' + (kind ? ' ' + kind : '');
  }

  function attach(form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var input = form.querySelector('input[type="email"]');
      var button = form.querySelector('button[type="submit"]');
      var msg = form.querySelector('.waitlist-msg');
      var email = ((input && input.value) || '').trim();

      if (!isValidEmail(email)) {
        setMsg(msg, 'Please enter a valid email address.', 'error');
        if (input) input.focus();
        return;
      }

      var originalLabel = button ? button.textContent : '';
      if (button) {
        button.disabled = true;
        button.textContent = 'Joining…';
      }
      setMsg(msg, '', '');

      fetch(ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          apikey: PUBLISHABLE_KEY,
          Authorization: 'Bearer ' + PUBLISHABLE_KEY,
        },
        body: JSON.stringify({
          email: email,
        }),
      })
        .then(function (res) {
          return res
            .json()
            .catch(function () {
              return {};
            })
            .then(function (data) {
              return { ok: res.ok, data: data };
            });
        })
        .then(function (result) {
          if (result.ok) {
            form.reset();
            setMsg(
              msg,
              "You're on the list! We'll email you the moment we launch.",
              'success'
            );
          } else {
            setMsg(
              msg,
              (result.data && result.data.error) ||
                'Something went wrong. Please try again.',
              'error'
            );
          }
        })
        .catch(function () {
          setMsg(msg, 'Network error. Please try again.', 'error');
        })
        .then(function () {
          if (button) {
            button.disabled = false;
            button.textContent = originalLabel;
          }
        });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var forms = document.querySelectorAll('form[data-waitlist]');
    Array.prototype.forEach.call(forms, attach);
  });
})();
