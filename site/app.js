const COLORS = ["#a9603e", "#4b8c81", "#bf9a45", "#6576a0", "#8a6487", "#638047", "#c3755d"];
const MONTHS = ["Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic", "Ene", "Feb", "Mar"];
const YEAR_LABEL = (year) => `${year}–${String(year + 1).slice(-2)}`;
const numberFormat = new Intl.NumberFormat("es-CL", { maximumFractionDigits: 2 });
let appData;
let visibleStations = new Set();
let selectedMapStation = null;
let mapPeriod = "all";

const $ = (selector) => document.querySelector(selector);
const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[char]));
const selectedParameter = () => $("#parameter-select").value;
const selectedMapParameter = () => $("#map-parameter").value;
const metric = (record, key) => {
  const value = record.values[key];
  return typeof value === "number" && Number.isFinite(value) ? value : null;
};
const waterYear = (date) => {
  const year = Number(date.slice(0, 4));
  return Number(date.slice(5, 7)) >= 4 ? year : year - 1;
};
const filteredRecords = (stationId, parameter, period = "all") => appData.records.filter((record) =>
  record.stationId === stationId
  && metric(record, parameter) !== null
  && (period === "all" || waterYear(record.date) === Number(period)));
const stats = (records, parameter) => {
  const values = records.map((record) => metric(record, parameter)).filter((value) => value !== null);
  if (!values.length) return null;
  return {
    count: values.length,
    average: values.reduce((sum, value) => sum + value, 0) / values.length,
    min: Math.min(...values),
    max: Math.max(...values),
  };
};
const formatValue = (value) => value === null || value === undefined ? "—" : numberFormat.format(value);
const stationById = (id) => appData.stations.find((station) => station.id === id);
const parameterById = (id) => appData.parameters.find((parameter) => parameter.id === id);

function populateSelects() {
  const options = appData.parameters.map((parameter) =>
    `<option value="${parameter.id}">${escapeHtml(parameter.label)}</option>`).join("");
  $("#parameter-select").innerHTML = options;
  $("#map-parameter").innerHTML = options;
  $("#parameter-select").value = "waterTemp";
  $("#map-parameter").value = "waterTemp";

  const years = [...new Set(appData.records.map((record) => waterYear(record.date)))].sort((a, b) => a - b);
  $("#map-year").innerHTML = `<option value="all">Todos los años</option>${years.map((year) =>
    `<option value="${year}">${YEAR_LABEL(year)}</option>`).join("")}`;

  const locations = [...new Set(appData.stations.map((station) => station.site))];
  $("#photo-location").innerHTML = `<option value="all">Todos los sectores</option>${locations.map((location) =>
    `<option value="${escapeHtml(location)}">${escapeHtml(location)}</option>`).join("")}`;
}

function renderFilters() {
  $("#station-filters").querySelector(".filter-options").innerHTML = appData.stations.map((station, index) => `
    <label class="filter-option">
      <input type="checkbox" value="${station.id}" ${visibleStations.has(station.id) ? "checked" : ""}>
      <span class="filter-dot" style="background:${COLORS[index]}"></span>
      ${escapeHtml(station.site)} · ${escapeHtml(station.river)}
    </label>`).join("");
}

function renderCharts() {
  const parameter = parameterById(selectedParameter());
  const years = [...new Set(appData.records.map((record) => waterYear(record.date)))].sort((a, b) => a - b);
  $("#chart-grid").innerHTML = years.map((year) => {
    const records = appData.records.filter((record) => waterYear(record.date) === year);
    const series = appData.stations.filter((station) => visibleStations.has(station.id)).map((station) => ({
      station,
      records: records.filter((record) => record.stationId === station.id && metric(record, parameter.id) !== null),
    }));
    const values = series.flatMap(({ records: stationRecords }) => stationRecords.map((record) => metric(record, parameter.id)));
    const min = values.length ? Math.min(...values) : 0;
    const max = values.length ? Math.max(...values) : 1;
    const spread = max - min || Math.max(Math.abs(max) * 0.1, 1);
    const lower = min - spread * 0.1;
    const upper = max + spread * 0.1;
    const width = 620;
    const height = 190;
    const left = 43;
    const right = 10;
    const top = 15;
    const bottom = 32;
    const plotWidth = width - left - right;
    const plotHeight = height - top - bottom;
    const y = (value) => top + (upper - value) / (upper - lower) * plotHeight;
    const grid = Array.from({ length: 4 }, (_, index) => {
      const position = top + index * plotHeight / 3;
      const value = upper - index * (upper - lower) / 3;
      return `<line class="chart-gridline" x1="${left}" y1="${position}" x2="${width - right}" y2="${position}"></line>
        <text class="chart-axis-label" x="${left - 7}" y="${position + 3}" text-anchor="end">${formatValue(value)}</text>`;
    }).join("");
    const xLabels = MONTHS.map((month, index) => {
      const x = left + index * plotWidth / 11;
      return `<text class="chart-axis-label" x="${x}" y="${height - 7}" text-anchor="middle">${month}</text>`;
    }).join("");
    const paths = series.map(({ station, records: stationRecords }) => {
      const stationIndex = appData.stations.findIndex((entry) => entry.id === station.id);
      const pointList = stationRecords.map((record) => {
        const month = Number(record.date.slice(5, 7));
        const monthIndex = month >= 4 ? month - 4 : month + 8;
        const x = left + monthIndex * plotWidth / 11;
        return { x, y: y(metric(record, parameter.id)), value: metric(record, parameter.id), date: record.date };
      });
      if (!pointList.length) return "";
      const line = pointList.map((point, index) => `${index ? "L" : "M"}${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(" ");
      const points = pointList.map((point) => `<circle class="chart-point" cx="${point.x}" cy="${point.y}" r="3.5" fill="${COLORS[stationIndex]}">
        <title>${escapeHtml(station.site)} · ${escapeHtml(station.river)} — ${point.date}: ${formatValue(point.value)} ${escapeHtml(parameter.unit)}</title>
      </circle>`).join("");
      return `<path class="chart-line" d="${line}" stroke="${COLORS[stationIndex]}">${escapeHtml(station.site)} · ${escapeHtml(station.river)}</path>${points}`;
    }).join("");
    return `<article class="chart-card">
      <h3>Año hídrico ${YEAR_LABEL(year)}</h3>
      <p>${escapeHtml(parameter.label)}${parameter.unit ? ` · ${escapeHtml(parameter.unit)}` : ""}</p>
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(parameter.label)} durante el año hídrico ${YEAR_LABEL(year)}">
        ${grid}${xLabels}${paths || `<text class="chart-empty" x="${width / 2}" y="${height / 2}" text-anchor="middle">Sin mediciones para mostrar</text>`}
      </svg>
    </article>`;
  }).join("");
  renderSummary(parameter);
}

function renderSummary(parameter) {
  const stations = appData.stations.filter((station) => visibleStations.has(station.id));
  $("#summary-title").textContent = `Estadísticas · ${parameter.label}`;
  $("#summary-cards").innerHTML = stations.map((station) => {
    const result = stats(filteredRecords(station.id, parameter.id), parameter.id);
    const index = appData.stations.findIndex((entry) => entry.id === station.id);
    return `<article class="summary-card">
      <h4><span class="filter-dot" style="background:${COLORS[index]}"></span>${escapeHtml(station.site)} · ${escapeHtml(station.river)}</h4>
      <dl><dt>Promedio</dt><dd>${formatValue(result?.average)} ${escapeHtml(parameter.unit)}</dd>
        <dt>Mínimo</dt><dd>${formatValue(result?.min)} ${escapeHtml(parameter.unit)}</dd>
        <dt>Máximo</dt><dd>${formatValue(result?.max)} ${escapeHtml(parameter.unit)}</dd></dl>
    </article>`;
  }).join("") || `<p class="source-note">Activa al menos una estación para ver sus estadísticas.</p>`;
}

function renderMap() {
  const groups = new Map();
  for (const station of appData.stations) {
    if (!groups.has(station.site)) groups.set(station.site, { ...station.location, site: station.site, count: 0 });
    groups.get(station.site).count += 1;
  }
  const locations = [...groups.values()];
  const lonValues = locations.map((location) => location.lon);
  const latValues = locations.map((location) => location.lat);
  const minLon = Math.min(...lonValues) - 0.02;
  const maxLon = Math.max(...lonValues) + 0.02;
  const minLat = Math.min(...latValues) - 0.02;
  const maxLat = Math.max(...latValues) + 0.02;
  const width = 700, height = 390, margin = 52;
  const project = (location) => ({
    x: margin + (location.lon - minLon) / (maxLon - minLon) * (width - margin * 2),
    y: height - margin - (location.lat - minLat) / (maxLat - minLat) * (height - margin * 2),
  });
  const grid = Array.from({ length: 5 }, (_, index) => {
    const offsetX = margin + index * (width - margin * 2) / 4;
    const offsetY = margin + index * (height - margin * 2) / 4;
    const longitude = minLon + index * (maxLon - minLon) / 4;
    const latitude = maxLat - index * (maxLat - minLat) / 4;
    return `<line class="map-grid" x1="${offsetX}" y1="${margin}" x2="${offsetX}" y2="${height - margin}"></line>
      <line class="map-grid" x1="${margin}" y1="${offsetY}" x2="${width - margin}" y2="${offsetY}"></line>
      <text class="map-coordinate" x="${offsetX}" y="${height - 18}" text-anchor="middle">${longitude.toFixed(2)}° O</text>
      <text class="map-coordinate" x="6" y="${offsetY + 3}">${latitude.toFixed(2)}° S</text>`;
  }).join("");
  const markers = locations.map((location) => {
    const point = project(location);
    return `<circle class="map-marker-halo" cx="${point.x}" cy="${point.y}" r="20"></circle>
      <circle class="map-marker" cx="${point.x}" cy="${point.y}" r="12"></circle>
      <text class="map-marker-count" x="${point.x}" y="${point.y}">${location.count}</text>
      <text class="map-label" x="${point.x + 17}" y="${point.y - 7}">${escapeHtml(location.site)}</text>`;
  }).join("");
  $("#station-map").innerHTML = `<svg viewBox="0 0 ${width} ${height}" aria-hidden="true">${grid}${markers}</svg>`;

  $("#station-list").innerHTML = appData.stations.map((station) => {
    const index = appData.stations.findIndex((entry) => entry.id === station.id);
    return `<button class="station-button" type="button" data-station="${station.id}" aria-pressed="${selectedMapStation === station.id}">
      <span class="filter-dot" style="background:${COLORS[index]}"></span>
      <span><strong>${escapeHtml(station.site)}</strong><small>Río ${escapeHtml(station.river)}</small></span>
    </button>`;
  }).join("");
  $("#station-list").querySelectorAll("[data-station]").forEach((button) => {
    button.addEventListener("click", () => {
      selectedMapStation = button.dataset.station;
      renderMap();
      renderMapSummary();
    });
  });
  renderMapSummary();
}

function renderMapSummary() {
  const station = stationById(selectedMapStation);
  if (!station) {
    $("#map-summary").innerHTML = "<p>Selecciona una estación para ver su resumen.</p>";
    return;
  }
  const parameter = parameterById(selectedMapParameter());
  const result = stats(filteredRecords(station.id, parameter.id, mapPeriod), parameter.id);
  $("#map-summary").innerHTML = `<h3>${escapeHtml(station.site)} · Río ${escapeHtml(station.river)}</h3>
    <dl><div><dt>Promedio</dt><dd>${formatValue(result?.average)}</dd></div>
    <div><dt>Mínimo</dt><dd>${formatValue(result?.min)}</dd></div>
    <div><dt>Máximo</dt><dd>${formatValue(result?.max)}</dd></div></dl>
    <p>${escapeHtml(parameter.unit)}${mapPeriod === "all" ? " · todos los años" : ` · año hídrico ${YEAR_LABEL(Number(mapPeriod))}`}</p>`;
}

function photoDate(filename) {
  const match = filename.match(/(?:19|20)\d{2}/);
  return match ? match[0] : "";
}

function renderPhotos() {
  const location = $("#photo-location").value;
  const images = appData.photos.filter((photo) => location === "all" || photo.location === location);
  $("#photo-count").textContent = `${images.length} fotografías`;
  $("#photo-grid").innerHTML = images.length ? images.map((photo) => `
    <button class="photo-card" type="button" data-photo="${escapeHtml(photo.path)}" data-caption="${escapeHtml(photo.filename)}">
      <img src="${encodeURI(photo.path)}" loading="lazy" alt="Fotografía de ${escapeHtml(photo.location)}: ${escapeHtml(photo.filename)}">
      <span class="photo-caption"><strong>${escapeHtml(photo.location)}</strong><small>${escapeHtml(photoDate(photo.filename) || photo.filename)}</small></span>
    </button>`).join("") : `<p class="photo-empty">No hay fotografías disponibles para este sector.</p>`;
  $("#photo-grid").querySelectorAll("[data-photo]").forEach((button) => {
    button.addEventListener("click", () => {
      $("#dialog-image").src = encodeURI(button.dataset.photo);
      $("#dialog-image").alt = `${button.dataset.caption}, ${location}`;
      $("#dialog-caption").textContent = `${location === "all" ? "Fotografía" : location} · ${button.dataset.caption}`;
      $("#photo-dialog").showModal();
    });
  });
}

function downloadFile(filename, content, type) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function downloadCsv() {
  const header = ["Fecha", "Año hídrico", "Sector", "Río", ...appData.parameters.map((parameter) => parameter.label)];
  const rows = appData.records.map((record) => {
    const station = stationById(record.stationId);
    return [record.date, YEAR_LABEL(waterYear(record.date)), station.site, station.river,
      ...appData.parameters.map((parameter) => metric(record, parameter.id) ?? "")];
  });
  const csv = [header, ...rows].map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(",")).join("\r\n");
  downloadFile("voluntarios-por-el-agua-datos.csv", `\uFEFF${csv}`, "text/csv;charset=utf-8");
}

function attachEvents() {
  $("#parameter-select").addEventListener("change", renderCharts);
  $("#station-filters").addEventListener("change", (event) => {
    if (event.target.matches("input[type=checkbox]")) {
      if (event.target.checked) visibleStations.add(event.target.value);
      else visibleStations.delete(event.target.value);
      renderCharts();
    }
  });
  $("#map-parameter").addEventListener("change", renderMapSummary);
  $("#map-year").addEventListener("change", (event) => {
    mapPeriod = event.target.value;
    renderMapSummary();
  });
  $("#photo-location").addEventListener("change", renderPhotos);
  $("#download-csv").addEventListener("click", downloadCsv);
  $("#download-json").addEventListener("click", () =>
    downloadFile("voluntarios-por-el-agua-datos.json", JSON.stringify(appData.records, null, 2), "application/json"));
  $("#menu-toggle").addEventListener("click", () => {
    const button = $("#menu-toggle");
    const expanded = button.getAttribute("aria-expanded") === "true";
    button.setAttribute("aria-expanded", String(!expanded));
    $("#site-nav").classList.toggle("is-open", !expanded);
  });
  $("#site-nav").querySelectorAll("a").forEach((link) => link.addEventListener("click", () => {
    $("#site-nav").classList.remove("is-open");
    $("#menu-toggle").setAttribute("aria-expanded", "false");
  }));
  $("#photo-dialog").querySelector(".dialog-close").addEventListener("click", () => $("#photo-dialog").close());
}

async function start() {
  try {
    const [measurementResponse, photoResponse] = await Promise.all([
      fetch("data/measurements.json"),
      fetch("data/photos.json"),
    ]);
    if (!measurementResponse.ok || !photoResponse.ok) throw new Error("No se pudieron cargar los archivos de datos del sitio.");
    const [measurements, photos] = await Promise.all([measurementResponse.json(), photoResponse.json()]);
    appData = { ...measurements, photos };
    visibleStations = new Set(appData.stations.map((station) => station.id));
    populateSelects();
    renderFilters();
    renderCharts();
    renderMap();
    renderPhotos();
    attachEvents();
  } catch (error) {
    $("#chart-grid").innerHTML = `<p class="loading">${escapeHtml(error.message)} Ejecuta el generador de datos y abre el sitio mediante un servidor web local.</p>`;
  }
}

start();
