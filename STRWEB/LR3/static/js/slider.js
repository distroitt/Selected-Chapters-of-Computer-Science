'use strict';
class Slider {
  constructor(root, options = {}) {
    this.root = root;
    this.options = {loop: true, navs: true, pags: true, auto: true, stopMouseHover: true, delay: 5, ...options};
    this.slides = [...root.querySelectorAll('[data-slide]')];
    this.index = 0;
    this.hovered = false;
    this.focused = false;
    this.paused = false;
    this.previous = root.querySelector('[data-prev]');
    this.next = root.querySelector('[data-next]');
    this.pages = root.querySelector('[data-pages]');
    this.counter = root.querySelector('[data-counter]');
    this.pauseButton = root.querySelector('[data-pause]');
    this.pauseButton.addEventListener('click', () => {
      this.paused = !this.paused;
      this.pauseButton.textContent = this.paused ? 'Продолжить' : 'Пауза';
      this.pauseButton.setAttribute('aria-pressed', String(this.paused));
      this.schedule();
    });
    this.previous.addEventListener('click', () => this.go(this.index - 1));
    this.next.addEventListener('click', () => this.go(this.index + 1));
    this.slides.forEach((_, index) => {
      const button = PetCare.node('button', String(index + 1), {type: 'button', 'aria-label': `Слайд ${index + 1}`});
      button.addEventListener('click', () => this.go(index));
      this.pages.append(button);
    });
    root.addEventListener('mouseenter', () => { this.hovered = true; this.schedule(); });
    root.addEventListener('mouseleave', () => { this.hovered = false; this.schedule(); });
    root.addEventListener('focusin', () => { this.focused = true; this.schedule(); });
    root.addEventListener('focusout', event => {
      if (!root.contains(event.relatedTarget)) { this.focused = false; this.schedule(); }
    });
    document.addEventListener('visibilitychange', () => this.schedule());
    this.go(0);
  }
  configure(options) {
    Object.assign(this.options, options);
    this.go(this.index);
  }
  go(index) {
    const total = this.slides.length;
    if (!total) return;
    this.index = this.options.loop ? (index + total) % total : Math.max(0, Math.min(index, total - 1));
    this.slides.forEach((slide, i) => { slide.hidden = i !== this.index; });
    this.counter.textContent = `${this.index + 1}/${total}`;
    [...this.pages.children].forEach((page, i) => {
      if (i === this.index) page.setAttribute('aria-current', 'true'); else page.removeAttribute('aria-current');
    });
    this.previous.hidden = this.next.hidden = !this.options.navs;
    this.pages.hidden = !this.options.pags;
    this.pauseButton.hidden = !this.options.auto;
    this.previous.disabled = !this.options.loop && this.index === 0;
    this.next.disabled = !this.options.loop && this.index === total - 1;
    this.schedule();
  }
  schedule() {
    clearTimeout(this.timer);
    if (!this.options.auto || this.paused || this.focused || document.hidden ||
        (this.options.stopMouseHover && this.hovered) || matchMedia('(prefers-reduced-motion: reduce)').matches ||
        (!this.options.loop && this.index === this.slides.length - 1)) return;
    this.timer = setTimeout(() => this.go(this.index + 1), Math.max(1, Number(this.options.delay) || 5) * 1000);
  }
}
window.Slider = Slider;
const sliderRoot = document.querySelector('[data-slider]');
if (sliderRoot) {
  const options = JSON.parse(document.querySelector('#slider-options').textContent);
  const slider = new Slider(sliderRoot, options);
  const form = document.querySelector('#slider-form');
  if (form) form.addEventListener('submit', async event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const button = form.querySelector('button');
    const status = document.querySelector('#slider-status');
    button.disabled = true;
    status.textContent = 'Сохраняем…';
    try {
      const settings = await PetCare.request(form.action, {method: 'POST', body: new FormData(form)});
      slider.configure(settings);
      status.textContent = 'Настройки сохранены для всех посетителей.';
    } catch (error) { status.textContent = error.message; }
    finally { button.disabled = false; }
  });
}
