'use strict';
// Чистые вычисления: используются страницей и тестами Node.js.
function ageOnDate(iso, today = new Date()) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(iso)) throw new Error('Введите дату рождения.');
  const [year, month, day] = iso.split('-').map(Number);
  const birth = new Date(year, month - 1, day);
  if (birth.getFullYear() !== year || birth.getMonth() !== month - 1 || birth.getDate() !== day ||
      birth > today || year < 1900) throw new Error('Введите существующую дату с 1900 года, не позднее сегодняшней.');
  const age = today.getFullYear() - year - (today.getMonth() < month - 1 ||
    (today.getMonth() === month - 1 && today.getDate() < day) ? 1 : 0);
  return {age, weekday: birth.toLocaleDateString('ru-BY', {weekday: 'long'})};
}
function logarithmSeries(x, epsilon = 1e-8, maxTerms = 100000) {
  if (!Number.isFinite(x) || Math.abs(x) <= 1 || !Number.isFinite(epsilon) || epsilon <= 0)
    throw new Error('Нужны |x| > 1 и положительная точность.');
  let sum = 0;
  let power = 1 / x;
  const ratio = 1 / (x * x);
  for (let n = 0; n < maxTerms; n++) {
    sum += 2 * power / (2 * n + 1);
    power *= ratio;
    // Верхняя граница хвоста ряда (модули членов убывают быстрее геометрической прогрессии).
    const remainder = Math.abs(2 * power / (2 * n + 3)) / (1 - ratio);
    if (remainder <= epsilon) return {x, sum, n: n + 1, exact: Math.log((x + 1) / (x - 1)), remainder};
  }
  throw new Error('Ряд не сошёлся за 100000 членов. Отодвиньте x от ±1 или уменьшите точность.');
}
function namesakes(items) {
  const groups = new Map();
  for (const item of items) {
    const key = item.surname.trim().toLocaleLowerCase('ru');
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(item);
  }
  return [...groups.values()].filter(group => group.length > 1);
}
function pupilValues(form) {
  const data = Object.fromEntries(new FormData(form));
  return {name: data.name.trim(), surname: data.surname.trim(), schoolClass: data.schoolClass.trim()};
}
function writePupils(items, target, withClass = false) {
  target.replaceChildren();
  for (const pupil of items) {
    const li = document.createElement('li');
    li.textContent = `${pupil.surname} ${pupil.name}${withClass ? `, ${pupil.schoolClass}` : ''}`;
    target.append(li);
  }
}
function writeNamesakes(items, target) {
  const groups = namesakes(items);
  target.textContent = groups.length ? 'Однофамильцы: ' + groups.map(group =>
    group.map(pupil => `${pupil.surname} ${pupil.name} (${pupil.schoolClass})`).join(', ')).join('; ') + '.'
    : 'Однофамильцев нет.';
}

// Вариант 1: функции-конструкторы и прототипное наследование.
function PupilPrototype(name, surname) { this.name = name; this.surname = surname; }
Object.defineProperty(PupilPrototype.prototype, 'fullName', {
  get() { return `${this.surname} ${this.name}`; },
  set(value) { const [surname, ...name] = value.trim().split(/\s+/); this.surname = surname; this.name = name.join(' '); },
});
PupilPrototype.prototype.addFromForm = function(form, items) {
  const data = pupilValues(form);
  items.push(new PupilPrototype(data.name, data.surname));
};
PupilPrototype.prototype.renderAll = function(items, target) { writePupils(items, target); };
PupilPrototype.prototype.renderResult = function(items, target) { target.textContent = `Учеников: ${items.length}`; };
function SchoolPupilPrototype(name, surname, schoolClass) {
  PupilPrototype.call(this, name, surname);
  this._schoolClass = schoolClass;
}
SchoolPupilPrototype.prototype = Object.create(PupilPrototype.prototype);
SchoolPupilPrototype.prototype.constructor = SchoolPupilPrototype;
Object.defineProperty(SchoolPupilPrototype.prototype, 'schoolClass', {
  get() { return this._schoolClass; },
  set(value) { this._schoolClass = String(value).trim(); },
});
SchoolPupilPrototype.prototype.addFromForm = function(form, items) {
  const data = pupilValues(form);
  items.push(new SchoolPupilPrototype(data.name, data.surname, data.schoolClass));
};
SchoolPupilPrototype.prototype.renderAll = function(items, target) { writePupils(items, target, true); };
SchoolPupilPrototype.prototype.renderResult = function(items, target) { writeNamesakes(items, target); };

// Вариант 2: class / extends. У каждого класса геттер, сеттер и три метода.
class Pupil {
  constructor(name, surname) { this.name = name; this.surname = surname; }
  get fullName() { return `${this.surname} ${this.name}`; }
  set fullName(value) { const [surname, ...name] = value.trim().split(/\s+/); this.surname = surname; this.name = name.join(' '); }
  addFromForm(form, items) { const data = pupilValues(form); items.push(new Pupil(data.name, data.surname)); }
  renderAll(items, target) { writePupils(items, target); }
  renderResult(items, target) { target.textContent = `Учеников: ${items.length}`; }
}
class SchoolPupil extends Pupil {
  constructor(name, surname, schoolClass) { super(name, surname); this._schoolClass = schoolClass; }
  get schoolClass() { return this._schoolClass; }
  set schoolClass(value) { this._schoolClass = String(value).trim(); }
  addFromForm(form, items) { const data = pupilValues(form); items.push(new SchoolPupil(data.name, data.surname, data.schoolClass)); }
  renderAll(items, target) { writePupils(items, target, true); }
  renderResult(items, target) { writeNamesakes(items, target); }
}
if (typeof module !== 'undefined') module.exports = {ageOnDate, logarithmSeries, namesakes, Pupil, SchoolPupil, PupilPrototype, SchoolPupilPrototype};
