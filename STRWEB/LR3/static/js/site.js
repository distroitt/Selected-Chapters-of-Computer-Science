'use strict';
const themeButton = document.querySelector('#theme-toggle');
function themeLabel() {
  const dark = document.documentElement.dataset.theme === 'dark';
  themeButton.setAttribute('aria-pressed', String(dark));
  themeButton.textContent = dark ? 'Светлая тема' : 'Тёмная тема';
}
if (themeButton) {
  themeLabel();
  themeButton.addEventListener('click', () => {
    const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem('petcare.theme', theme); } catch (_) { /* Тема работает и без хранилища. */ }
    themeLabel();
    document.dispatchEvent(new Event('themechange'));
  });
}

// Параллакс карточек: мышь и клавиатура; на touch обычная карточка.
if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
  document.querySelectorAll('.item').forEach(card => {
    card.addEventListener('pointermove', event => {
      if (event.pointerType !== 'mouse') return;
      const box = card.getBoundingClientRect();
      const x = (event.clientX - box.left) / box.width - 0.5;
      const y = (event.clientY - box.top) / box.height - 0.5;
      card.style.transform = `perspective(800px) rotateX(${-y * 8}deg) rotateY(${x * 8}deg)`;
    });
    card.addEventListener('pointerleave', () => { card.style.transform = ''; });
  });
}

// Положение зависит от текущего scroll, поэтому движение обратимо.
const flight = document.querySelector('.pet-flight');
if (flight && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  let scheduled = false;
  const update = () => {
    scheduled = false;
    const rect = flight.getBoundingClientRect();
    const progress = Math.max(0, Math.min(1, (innerHeight - rect.top) / (innerHeight + rect.height)));
    flight.querySelectorAll('img').forEach((image, index) => {
      const direction = index % 2 ? -1 : 1;
      image.style.transform = `translate(${direction * (progress - .5) * 220}px, ${Math.sin(progress * Math.PI * 2 + index) * 32}px) rotate(${direction * (progress - .5) * 35}deg)`;
    });
  };
  addEventListener('scroll', () => { if (!scheduled) { scheduled = true; requestAnimationFrame(update); } }, {passive: true});
  addEventListener('resize', update);
  update();
}
