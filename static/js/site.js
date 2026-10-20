// Content remains visible if JavaScript is unavailable.
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if ('IntersectionObserver' in window && !reducedMotion) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, {threshold: 0.08});
  document.querySelectorAll('.reveal').forEach(element => {
    element.classList.add('will-reveal');
    observer.observe(element);
  });
}
document.querySelectorAll('.navbar-nav a').forEach(link => {
  link.addEventListener('click', () => {
    const navigation = document.getElementById('navigation');
    if (navigation.classList.contains('show') && window.bootstrap) {
      bootstrap.Collapse.getOrCreateInstance(navigation).hide();
    }
  });
});
