'use strict';
function validateContactURL(value) {
  return /^https?:\/\/[^\s/?#]+\/[^\s?#]*\.(?:php|html)$/i.test(value.trim());
}
function validateContactPhone(value) {
  return /^(?:8\s*(?:\(0\d{2}\)|0\d{2})|\+375\s*(?:\(\d{2}\)|\d{2}))[\s-]*\d(?:[\s-]*\d){6}$/.test(value.trim());
}
window.validateContactURL = validateContactURL;
window.validateContactPhone = validateContactPhone;
class EmployeeTable {
  constructor(root) {
    this.root = root;
    this.rows = [];
    this.selected = new Set();
    this.page = 1;
    this.query = '';
    this.sort = 'full_name';
    this.direction = 1;
    this.body = root.querySelector('tbody');
    this.status = document.querySelector('#employees-status');
    this.loader = document.querySelector('#employees-loader');
    this.selection = document.querySelector('#selection-count');
    this.bonus = document.querySelector('#bonus-button');
    document.querySelector('#employee-search').addEventListener('submit', event => {
      event.preventDefault();
      this.query = document.querySelector('#employee-query').value.trim().toLocaleLowerCase('ru');
      this.page = 1;
      this.render();
    });
    root.querySelectorAll('[data-sort]').forEach(button => button.addEventListener('click', () => {
      const key = button.dataset.sort;
      this.direction = this.sort === key ? -this.direction : 1;
      this.sort = key;
      this.page = 1;
      this.render();
    }));
    this.bonus.addEventListener('click', () => {
      const names = this.rows.filter(row => this.selected.has(row.id)).map(row => row.full_name.split(/\s+/)[0]);
      document.querySelector('#bonus-result').textContent = names.length
        ? `За добросовестную работу премировать сотрудников: ${names.join(', ')}.` : 'Выберите сотрудников.';
    });
    document.querySelector('#employees-retry').addEventListener('click', () => this.load());
    this.bindForm();
    this.load();
  }
  busy(value) {
    this.loader.hidden = !value;
    this.root.setAttribute('aria-busy', String(value));
  }
  async load() {
    this.busy(true);
    const retry = document.querySelector('#employees-retry');
    retry.hidden = true;
    try {
      this.rows = (await PetCare.request(this.root.dataset.url)).employees;
      this.render();
    } catch (error) {
      this.status.textContent = 'Не удалось загрузить сотрудников. ' + error.message;
      retry.hidden = false;
    } finally { this.busy(false); }
  }
  showDetails(row) {
    const block = document.querySelector('#employee-details');
    block.replaceChildren(PetCare.node('h2', 'Карточка сотрудника'));
    block.append(this.photo(row));
    for (const [key, label] of Object.entries({full_name: 'ФИО', position: 'Выполняемые работы', phone: 'Телефон', email: 'Почта'})) {
      block.append(PetCare.node('p', `${label}: ${row[key]}`));
    }
  }
  photo(row) {
    const image = PetCare.node('img', null, {src: row.photo_url || '/static/images/logo.svg', alt: row.full_name, width: 72, height: 72});
    image.addEventListener('error', () => { image.src = '/static/images/logo.svg'; }, {once: true});
    return image;
  }
  updateSelection() {
    this.selection.textContent = `Выбрано: ${this.selected.size} (на всех страницах)`;
    this.bonus.disabled = !this.selected.size;
  }
  render() {
    const keys = ['full_name', 'position', 'phone', 'email', 'photo_url'];
    const rows = this.rows.filter(row => keys.some(key => String(row[key]).toLocaleLowerCase('ru').includes(this.query)))
      .sort((a, b) => String(a[this.sort]).localeCompare(String(b[this.sort]), 'ru', {numeric: true}) * this.direction);
    const count = Math.ceil(rows.length / 3);
    this.page = Math.max(1, Math.min(this.page, count || 1));
    this.body.replaceChildren();
    rows.slice((this.page - 1) * 3, this.page * 3).forEach(row => {
      const tr = document.createElement('tr');
      const selection = document.createElement('td');
      const checkbox = PetCare.node('input', null, {type: 'checkbox', 'aria-label': `Выбрать: ${row.full_name}`});
      checkbox.checked = this.selected.has(row.id);
      checkbox.addEventListener('change', () => {
        if (checkbox.checked) this.selected.add(row.id); else this.selected.delete(row.id);
        this.updateSelection();
      });
      selection.append(checkbox);
      tr.append(selection);
      for (const key of keys) {
        const cell = document.createElement('td');
        if (key === 'photo_url') cell.append(this.photo(row));
        else if (key === 'full_name') {
          const button = PetCare.node('button', row[key], {type: 'button', class: 'text-button'});
          button.addEventListener('click', () => this.showDetails(row));
          cell.append(button);
        } else cell.textContent = row[key];
        tr.append(cell);
      }
      tr.addEventListener('click', event => { if (!event.target.closest('input, button, a')) this.showDetails(row); });
      this.body.append(tr);
    });
    if (!rows.length) {
      this.body.append(PetCare.node('tr', null));
      this.body.firstChild.append(PetCare.node('td', 'Сотрудники не найдены. Измените запрос.', {colspan: 6}));
    }
    this.root.querySelectorAll('[data-sort]').forEach(button => {
      const active = button.dataset.sort === this.sort;
      const th = button.closest('th');
      if (active) th.setAttribute('aria-sort', this.direction === 1 ? 'ascending' : 'descending'); else th.removeAttribute('aria-sort');
      button.querySelector('span').textContent = active ? (this.direction === 1 ? ' ↑' : ' ↓') : '';
    });
    this.status.textContent = `Найдено: ${rows.length}. Страница ${this.page} из ${count || 1}.`;
    PetCare.pagination(document.querySelector('#employees-pages'), this.page, count, page => { this.page = page; this.render(); });
    this.updateSelection();
  }
  bindForm() {
    const form = document.querySelector('#employee-form');
    if (!form) return;
    const toggle = document.querySelector('#employee-add');
    const panel = document.querySelector('#employee-form-panel');
    toggle.addEventListener('click', () => {
      panel.hidden = !panel.hidden;
      toggle.setAttribute('aria-expanded', String(!panel.hidden));
      if (!panel.hidden) form.elements.full_name.focus();
    });
    const result = document.querySelector('#employee-validation');
    const submit = form.querySelector('[type=submit]');
    const validators = {photo_url: validateContactURL, phone: validateContactPhone};
    let pending = false;
    const validate = () => {
      const messages = [];
      for (const [name, validator] of Object.entries(validators)) {
        const input = form.elements[name];
        const valid = validator(input.value);
        input.classList.toggle('invalid', !!input.value && !valid);
        input.setAttribute('aria-invalid', String(!!input.value && !valid));
        input.setCustomValidity(valid ? '' : (name === 'phone' ? 'Неверный формат белорусского номера.' : 'Нужен http(s) URL с окончанием .php или .html.'));
        if (input.value) messages.push(`${name === 'phone' ? 'Телефон' : 'URL'}: ${valid ? 'корректен' : 'неверный формат'}`);
      }
      result.textContent = messages.join('. ');
      submit.disabled = pending || !form.checkValidity();
    };
    form.addEventListener('input', validate);
    form.addEventListener('submit', async event => {
      event.preventDefault();
      validate();
      if (pending || !form.reportValidity()) return;
      pending = true;
      submit.disabled = true;
      this.busy(true);
      result.textContent = 'Сохраняем сотрудника…';
      try {
        const {employee} = await PetCare.request(form.action, {method: 'POST', body: new FormData(form)});
        this.rows.push(employee);
        this.query = '';
        document.querySelector('#employee-query').value = '';
        const sorted = [...this.rows].sort((a, b) => String(a[this.sort]).localeCompare(String(b[this.sort]), 'ru', {numeric: true}) * this.direction);
        this.page = Math.floor(sorted.findIndex(row => row.id === employee.id) / 3) + 1;
        this.render();
        this.showDetails(employee);
        form.reset();
        validate();
        result.textContent = 'Сотрудник добавлен и сохранён в базе данных.';
      } catch (error) {
        result.textContent = error.fields ? Object.values(error.fields).flat().join(' ') : error.message;
      } finally {
        pending = false;
        submit.disabled = !form.checkValidity();
        this.busy(false);
      }
    });
    validate();
  }
}
const employeeRoot = document.querySelector('#employee-table');
if (employeeRoot) new EmployeeTable(employeeRoot);
