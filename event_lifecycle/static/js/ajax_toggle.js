/**
 * ajax_toggle.js
 * Handles attendance toggle and transaction verification via fetch (no page refresh).
 * CO5: AJAX Integration
 */

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

function setupToggle(selector, labelSelector, trueText, falseText, trueClass, falseClass) {
  document.querySelectorAll(selector).forEach(btn => {
    btn.addEventListener('click', function () {
      const url = this.dataset.url;
      const label = this.querySelector(labelSelector);

      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json',
        },
      })
        .then(r => r.json())
        .then(data => {
          const isTrue = Object.values(data).find(v => typeof v === 'boolean');
          if (isTrue) {
            btn.classList.remove(falseClass);
            btn.classList.add(trueClass);
            label.textContent = trueText;
          } else {
            btn.classList.remove(trueClass);
            btn.classList.add(falseClass);
            label.textContent = falseText;
          }
        })
        .catch(err => console.error('Toggle failed:', err));
    });
  });
}

document.addEventListener('DOMContentLoaded', function () {
  setupToggle('.attend-btn', '.attend-label', '✅ Present', '⬜ Absent', 'btn-success', 'btn-outline-secondary');
  setupToggle('.verify-btn', '.verify-label', '✅ Verified', '⬜ Unverified', 'btn-success', 'btn-outline-secondary');
});
