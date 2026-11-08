'use strict';
// Конструктор текстовых полей, вариант 1.
const builder = document.querySelector('#field-builder');
const builderStatus = document.querySelector('#builder-status');
const fieldKey = 'petcare.text-fields';
let fieldData = PetCare.read(fieldKey, []);
if (!Array.isArray(fieldData)) fieldData = [];
fieldData = fieldData.filter(item => item && typeof item === 'object').slice(0, 100).map(item => ({
  name: String(item.name || '').slice(0, 80), placeholder: String(item.placeholder || '').slice(0, 200),
  maxlength: Math.max(1, Math.min(1000, Number(item.maxlength) || 100)),
  value: String(item.value || '').slice(0, 1000), readonly: item.readonly === true, disabled: item.disabled === true,
}));
function saveFields() {
  builderStatus.textContent = PetCare.save(fieldKey, fieldData)
    ? `Сохранено в этом браузере. Полей: ${fieldData.length}.`
    : 'Хранилище браузера недоступно: поля будут потеряны после обновления.';
}
function renderFields() {
  builder.replaceChildren();
  fieldData.forEach((data, index) => {
    const section = PetCare.node('section', null, {class: 'builder-field'});
    section.append(PetCare.node('h3', `Текстовое поле ${index + 1}`));
    const previewLabel = PetCare.node('label', 'Результат');
    const preview = PetCare.node('input', null, {type: 'text'});
    const apply = () => {
      for (const key of ['name', 'placeholder', 'maxlength']) preview.setAttribute(key, data[key]);
      preview.value = data.value;
      preview.readOnly = data.readonly;
      preview.disabled = data.disabled;
    };
    apply();
    preview.addEventListener('input', () => {
      data.value = preview.value;
      valueControl.value = preview.value;
      saveFields();
    });
    previewLabel.append(preview);
    section.append(previewLabel);
    let valueControl;
    for (const [key, label] of Object.entries({name: 'name — имя', placeholder: 'placeholder — подсказка', maxlength: 'maxlength — максимальная длина', value: 'value — значение', readonly: 'readonly — только чтение', disabled: 'disabled — отключено'})) {
      const wrapper = PetCare.node('label', label);
      const input = document.createElement('input');
      input.dataset.attribute = key;
      input.type = ['readonly', 'disabled'].includes(key) ? 'checkbox' : key === 'maxlength' ? 'number' : 'text';
      if (input.type === 'checkbox') input.checked = data[key]; else input.value = data[key];
      if (key === 'maxlength') { input.min = 1; input.max = 1000; }
      else if (input.type === 'text') input.maxLength = key === 'name' ? 80 : 1000;
      if (key === 'value') valueControl = input;
      input.addEventListener('input', () => {
        if (key === 'maxlength' && !input.checkValidity()) return;
        data[key] = input.type === 'checkbox' ? input.checked : key === 'maxlength' ? Number(input.value) : input.value;
        apply();
        saveFields();
      });
      wrapper.append(input);
      section.append(wrapper);
    }
    const remove = PetCare.node('button', 'Удалить это поле', {type: 'button', class: 'secondary'});
    remove.addEventListener('click', () => {
      fieldData.splice(index, 1);
      saveFields();
      renderFields();
      document.querySelector('#generate-field').focus();
    });
    section.append(remove);
    builder.append(section);
  });
}
document.querySelector('#generate-field').addEventListener('change', event => {
  if (!event.target.checked) return;
  if (fieldData.length < 100) {
    fieldData.push({name: `field_${fieldData.length + 1}`, placeholder: 'Введите текст', maxlength: 100, value: '', readonly: false, disabled: false});
    saveFields();
    renderFields();
  } else builderStatus.textContent = 'Достигнут предел: 100 полей.';
  event.target.checked = false;
});
renderFields();

const birthForm = document.querySelector('#birth-form');
const today = new Date();
birthForm.elements.birth_date.max = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
birthForm.addEventListener('submit', event => {
  event.preventDefault();
  const status = document.querySelector('#birth-result');
  try {
    const {age, weekday} = ageOnDate(birthForm.elements.birth_date.value);
    status.textContent = `Возраст: ${age}. ` + (age >= 18 ? `День рождения: ${weekday}.` : 'Для использования сайта нужно разрешение родителей.');
    if (age < 18) alert('Для использования сайта необходимо разрешение родителей.');
  } catch (error) { status.textContent = error.message; }
});

// Переключение реализации создаёт независимый массив объектов выбранного класса.
let pupils = [];
let pupilController;
const pupilsForm = document.querySelector('#pupils-form');
function renderPupils() {
  pupilController.renderAll(pupils, document.querySelector('#pupils-list'));
  pupilController.renderResult(pupils, document.querySelector('#pupils-result'));
}
function resetPupils() {
  const Constructor = document.querySelector('#inheritance-style').value === 'class' ? SchoolPupil : SchoolPupilPrototype;
  pupilController = new Constructor('', '', '');
  pupils = [new Constructor('Анна', 'Иванова', '8А'), new Constructor('Иван', 'Петров', '9Б'), new Constructor('Ольга', 'Иванова', '10А')];
  renderPupils();
}
document.querySelector('#inheritance-style').addEventListener('change', resetPupils);
document.querySelector('#pupils-demo').addEventListener('click', resetPupils);
pupilsForm.addEventListener('submit', event => {
  event.preventDefault();
  if (![pupilsForm.elements.name, pupilsForm.elements.surname, pupilsForm.elements.schoolClass].every(input => input.value.trim())) return;
  pupilController.addFromForm(pupilsForm, pupils);
  renderPupils();
  pupilsForm.reset();
  pupilsForm.elements.name.focus();
});
resetPupils();

// Web Speech API требует нажатия, чтение не начинается автоматически.
const speechStatus = document.querySelector('#speech-status');
const speak = document.querySelector('#speech-start');
const stop = document.querySelector('#speech-stop');
if (!('speechSynthesis' in window)) {
  speak.disabled = stop.disabled = true;
  speechStatus.textContent = 'Браузер не поддерживает синтез речи. Попробуйте Chrome или Edge.';
} else {
  speak.addEventListener('click', () => {
    const text = document.querySelector('#speech-text').value.trim();
    if (!text) { speechStatus.textContent = 'Введите текст для чтения.'; return; }
    speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ru-RU';
    utterance.onstart = () => { speechStatus.textContent = 'Читаем текст…'; };
    utterance.onend = () => { speechStatus.textContent = 'Чтение завершено.'; };
    utterance.onerror = event => { speechStatus.textContent = `Чтение недоступно (${event.error}). Проверьте голосовой движок браузера.`; };
    speechStatus.textContent = 'Запускаем синтез речи…';
    speechSynthesis.speak(utterance);
  });
  stop.addEventListener('click', () => { speechSynthesis.cancel(); speechStatus.textContent = 'Чтение остановлено.'; });
  addEventListener('pagehide', () => speechSynthesis.cancel());
}
