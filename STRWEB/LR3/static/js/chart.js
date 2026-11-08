'use strict';
const chartForm = document.querySelector('#series-form');
const chartStatus = document.querySelector('#chart-status');
const saveChart = document.querySelector('#chart-save');
let seriesChart;
function buildSeriesChart() {
  if (!chartForm.reportValidity()) return;
  const start = Number(chartForm.elements.start.value);
  const end = Number(chartForm.elements.end.value);
  const step = Number(chartForm.elements.step.value);
  const epsilon = Number(chartForm.elements.epsilon.value);
  try {
    if (![start, end, step, epsilon].every(Number.isFinite) || step <= 0 || epsilon <= 0 || end <= start ||
        !((start > 1 && end > 1) || (start < -1 && end < -1)) || Math.ceil((end - start) / step) > 200)
      throw new Error('Нужен возрастающий диапазон целиком x > 1 или x < −1, положительные шаг и точность, не более 201 точки.');
    const points = [];
    for (let i = 0; i <= Math.floor((end - start) / step + 1e-9); i++) points.push(logarithmSeries(Number((start + step * i).toPrecision(12)), epsilon));
    const body = document.querySelector('#series-table tbody');
    body.replaceChildren();
    points.forEach(point => {
      const tr = document.createElement('tr');
      for (const value of [point.x, point.sum.toFixed(10), point.n, point.exact.toFixed(10), Math.abs(point.sum - point.exact).toExponential(2)]) tr.append(PetCare.node('td', value));
      body.append(tr);
    });
    if (typeof Chart === 'undefined') throw new Error('Chart.js не загрузился. Проверьте наличие static/vendor/chart.umd.js. Таблица вычислений доступна.');
    if (seriesChart) seriesChart.destroy();
    const dark = document.documentElement.dataset.theme === 'dark';
    const text = dark ? '#e3e7e5' : '#1c2630';
    const annotation = {
      id: 'series-note',
      beforeDraw(chart) {
        const {ctx, width, height} = chart;
        ctx.save();
        ctx.globalCompositeOperation = 'destination-over';
        ctx.fillStyle = dark ? '#1e2723' : '#ffffff';
        ctx.fillRect(0, 0, width, height);
        ctx.restore();
      },
      afterDraw(chart) {
        const {ctx, chartArea} = chart;
        ctx.save();
        ctx.fillStyle = text;
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(`|x| > 1; ε = ${epsilon}`, chartArea.right - 8, chartArea.top + 18);
        ctx.restore();
      },
    };
    saveChart.disabled = true;
    seriesChart = new Chart(document.querySelector('#series-chart'), {
      type: 'line', plugins: [annotation],
      data: {datasets: [
        {label: 'Ряд F(x)', data: points.map(p => ({x: p.x, y: p.sum})), borderColor: '#be6325', pointRadius: 3, borderWidth: 2},
        {label: 'Math.log((x+1)/(x−1))', data: points.map(p => ({x: p.x, y: p.exact})), borderColor: dark ? '#73cda6' : '#1d7a55', borderDash: [7, 5], pointRadius: 1, borderWidth: 2},
      ]},
      options: {
        responsive: true, maintainAspectRatio: false, locale: 'ru-BY',
        animation: matchMedia('(prefers-reduced-motion: reduce)').matches ? false : {duration: 800, onComplete() { saveChart.disabled = false; }},
        plugins: {title: {display: true, text: 'Разложение ln((x + 1) / (x − 1)) в ряд', color: text}, legend: {labels: {color: text}}},
        scales: {
          x: {type: 'linear', title: {display: true, text: 'x — аргумент', color: text}, ticks: {color: text}, grid: {color: dark ? '#46524b' : '#dfe4ea'}},
          y: {title: {display: true, text: 'F(x)', color: text}, ticks: {color: text}, grid: {color: dark ? '#46524b' : '#dfe4ea'}},
        },
      },
    });
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) saveChart.disabled = false;
    chartStatus.textContent = `Построено ${points.length} точек. Максимальная ошибка: ${Math.max(...points.map(p => Math.abs(p.sum - p.exact))).toExponential(2)}.`;
  } catch (error) { chartStatus.textContent = error.message; }
}
chartForm.addEventListener('submit', event => { event.preventDefault(); buildSeriesChart(); });
saveChart.addEventListener('click', () => {
  if (!seriesChart) return;
  const link = document.createElement('a');
  link.download = 'petcare-series-variant1.png';
  link.href = seriesChart.toBase64Image('image/png', 1);
  link.click();
});
document.addEventListener('themechange', buildSeriesChart);
buildSeriesChart();
