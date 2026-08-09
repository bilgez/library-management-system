// Auto-dismiss flash messages after a few seconds
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .4s ease';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 400);
  }, 4000);
});

// Confirm before returning a book
document.querySelectorAll('form[action*="/return"]').forEach(form => {
  form.addEventListener('submit', (e) => {
    if (!confirm('Bu kitabı iade ediyor musun?')) e.preventDefault();
  });
});