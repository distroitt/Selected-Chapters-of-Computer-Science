const {test} = require('node:test');
const assert = require('node:assert/strict');
const {ageOnDate, logarithmSeries, namesakes, Pupil, SchoolPupil, PupilPrototype, SchoolPupilPrototype} = require('../static/js/lab-core.js');

test('Возраст: день совершеннолетия, день до него, неверные и будущие даты', () => {
  const today = new Date(2026, 10, 8);
  assert.equal(ageOnDate('2008-11-08', today).age, 18);
  assert.equal(ageOnDate('2008-11-09', today).age, 17);
  assert.equal(ageOnDate('2008-02-29', today).age, 18);
  for (const date of ['2025-02-29', '2026-11-09', '', '1900-02-29']) assert.throws(() => ageOnDate(date, today));
});

test('Ряд сходится к Math.log на обеих ветвях и гарантирует погрешность', () => {
  for (const x of [-5, -2, -1.02, 1.02, 1.2, 2, 5]) {
    const point = logarithmSeries(x, 1e-10);
    assert.ok(Math.abs(point.sum - point.exact) < 1e-10);
    assert.ok(point.n >= 1);
    assert.ok(point.remainder <= 1e-10);
  }
  for (const x of [-1, 0, 1, NaN, Infinity]) assert.throws(() => logarithmSeries(x));
  assert.throws(() => logarithmSeries(1.00001, 1e-12, 3));
});

test('Поиск однофамильцев не зависит от регистра и пробелов', () => {
  assert.equal(namesakes([{surname: ' Иванов '}, {surname: 'иванов'}, {surname: 'Петров'}]).length, 1);
  assert.deepEqual(namesakes([{surname: 'Иванов'}, {surname: 'Петров'}]), []);
});

test('Две реализации создают наследников, геттеры и сеттеры работают одинаково', () => {
  for (const [Base, Derived] of [[Pupil, SchoolPupil], [PupilPrototype, SchoolPupilPrototype]]) {
    const pupil = new Derived('Иван', 'Иванов', '8А');
    assert.ok(pupil instanceof Base);
    assert.equal(pupil.fullName, 'Иванов Иван');
    pupil.fullName = 'Петров Пётр';
    pupil.schoolClass = ' 9Б ';
    assert.equal(pupil.fullName, 'Петров Пётр');
    assert.equal(pupil.schoolClass, '9Б');
    for (const method of ['addFromForm', 'renderAll', 'renderResult']) assert.equal(typeof pupil[method], 'function');
  }
});
