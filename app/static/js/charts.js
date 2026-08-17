/* Minimal SVG chart layer for the security console.
 *
 * Deliberately dependency-free. Three forms cover everything the console
 * needs: a multi-series line (change over time), a horizontal bar (magnitude
 * by category) and a diverging bar (signed attribution).
 *
 * Conventions: 2px strokes, 4px rounded data-ends anchored to the baseline,
 * a 2px surface gap between adjacent bars, recessive grid, crosshair or
 * per-mark tooltips on every plot.
 */
(function (global) {
  "use strict";

  const NS = "http://www.w3.org/2000/svg";
  const css = (name) =>
    getComputedStyle(document.body).getPropertyValue(name).trim();

  const PALETTE = {
    get series1() { return css("--series-1"); },
    get series2() { return css("--series-2"); },
    get seq250() { return css("--seq-250"); },
    get seq350() { return css("--seq-350"); },
    get seq450() { return css("--seq-450"); },
    get seq550() { return css("--seq-550"); },
    get surface() { return css("--surface-1"); },
    get muted() { return css("--text-muted"); },
  };

  const SEVERITY_COLORS = {
    get CRITICAL() { return css("--sev-critical"); },
    get HIGH() { return css("--sev-high"); },
    get MEDIUM() { return css("--sev-medium"); },
    get LOW() { return css("--sev-low"); },
    get UNKNOWN() { return css("--text-muted"); },
  };

  function el(tag, attrs, parent) {
    const node = document.createElementNS(NS, tag);
    for (const k in attrs || {}) node.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(node);
    return node;
  }

  function clear(host) {
    host.textContent = "";
  }

  function empty(host, message) {
    clear(host);
    const p = document.createElement("p");
    p.className = "chart-empty";
    p.textContent = message || "No data for the current selection.";
    host.appendChild(p);
  }

  function legend(host, entries) {
    const box = document.createElement("div");
    box.className = "chart-legend";
    entries.forEach((e) => {
      const span = document.createElement("span");
      const swatch = document.createElement("i");
      swatch.style.background = e.color;
      span.appendChild(swatch);
      span.appendChild(document.createTextNode(e.name));
      box.appendChild(span);
    });
    host.appendChild(box);
    return box;
  }

  /* ── shared tooltip ──────────────────────────────────────────────── */
  const tip = {
    node: null,
    ensure() {
      if (!this.node) this.node = document.getElementById("tooltip");
      return this.node;
    },
    show(html, evt) {
      const n = this.ensure();
      if (!n) return;
      n.innerHTML = html;
      n.hidden = false;
      const pad = 14;
      const rect = n.getBoundingClientRect();
      let x = evt.clientX + pad;
      let y = evt.clientY + pad;
      if (x + rect.width > window.innerWidth - 8) x = evt.clientX - rect.width - pad;
      if (y + rect.height > window.innerHeight - 8) y = evt.clientY - rect.height - pad;
      n.style.left = x + "px";
      n.style.top = y + "px";
    },
    hide() {
      const n = this.ensure();
      if (n) n.hidden = true;
    },
  };

  const row = (k, v) =>
    `<div class="t-row"><span class="t-key">${k}</span><b>${v}</b></div>`;

  function niceCeil(value) {
    if (value <= 0) return 1;
    const exp = Math.pow(10, Math.floor(Math.log10(value)));
    const frac = value / exp;
    const step = frac <= 1 ? 1 : frac <= 2 ? 2 : frac <= 5 ? 5 : 10;
    return step * exp;
  }

  /* ── line chart ──────────────────────────────────────────────────── */
  function lineChart(host, opts) {
    const series = (opts.series || []).filter((s) => s.points && s.points.length);
    if (!series.length) return empty(host, opts.emptyMessage);

    clear(host);
    if (series.length > 1) {
      legend(host, series.map((s) => ({ name: s.name, color: s.color })));
    }

    const W = host.clientWidth || 640;
    const H = opts.height || 230;
    const M = { top: 12, right: 14, bottom: 26, left: 42 };
    const iw = Math.max(W - M.left - M.right, 10);
    const ih = Math.max(H - M.top - M.bottom, 10);

    const labels = opts.labels || series[0].points.map((_, i) => i);
    const n = Math.max(...series.map((s) => s.points.length));
    const maxY = opts.maxY != null
      ? opts.maxY
      : niceCeil(Math.max(...series.flatMap((s) => s.points)) || 1);

    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, height: H,
                            role: "img", "aria-label": opts.title || "chart" }, host);
    const plot = el("g", { transform: `translate(${M.left},${M.top})` }, svg);

    const X = (i) => (n <= 1 ? iw / 2 : (i / (n - 1)) * iw);
    const Y = (v) => ih - (Math.max(0, Math.min(v, maxY)) / maxY) * ih;

    // grid + y axis
    const grid = el("g", { class: "grid" }, plot);
    const axis = el("g", { class: "axis" }, plot);
    const ticks = 4;
    for (let t = 0; t <= ticks; t++) {
      const v = (maxY / ticks) * t;
      const y = Y(v);
      el("line", { x1: 0, x2: iw, y1: y, y2: y }, grid);
      const label = el("text", { x: -8, y: y + 3.5, "text-anchor": "end" }, axis);
      label.textContent = opts.formatY ? opts.formatY(v) : Math.round(v);
    }
    el("line", { x1: 0, x2: iw, y1: ih, y2: ih }, axis);

    // x labels — first, middle, last only, to avoid collisions
    [0, Math.floor((n - 1) / 2), n - 1].forEach((i, k, arr) => {
      if (i < 0 || (k > 0 && i === arr[k - 1])) return;
      const t = el("text", {
        x: X(i), y: ih + 16,
        "text-anchor": k === 0 ? "start" : k === arr.length - 1 ? "end" : "middle",
      }, axis);
      t.textContent = labels[i] != null ? String(labels[i]) : "";
    });

    // series paths
    series.forEach((s) => {
      const d = s.points
        .map((v, i) => `${i ? "L" : "M"}${X(i).toFixed(2)},${Y(v).toFixed(2)}`)
        .join(" ");
      el("path", { d, class: "series-line", stroke: s.color }, plot);
    });

    // crosshair + hover tooltip
    const cross = el("line", { class: "crosshair", y1: 0, y2: ih, opacity: 0 }, plot);
    const dots = series.map((s) =>
      el("circle", {
        r: 4.5, fill: s.color, stroke: PALETTE.surface, "stroke-width": 2, opacity: 0,
      }, plot)
    );
    const hit = el("rect", { class: "hit", x: 0, y: 0, width: iw, height: ih }, plot);

    hit.addEventListener("mousemove", (evt) => {
      const bounds = svg.getBoundingClientRect();
      const scale = iw / (bounds.width - M.left - M.right || 1);
      const px = (evt.clientX - bounds.left - M.left * (bounds.width / W)) * scale;
      const i = Math.max(0, Math.min(n - 1, Math.round((px / iw) * (n - 1))));

      cross.setAttribute("x1", X(i));
      cross.setAttribute("x2", X(i));
      cross.setAttribute("opacity", 1);

      let html = `<div><b>${labels[i] != null ? labels[i] : i}</b></div>`;
      series.forEach((s, k) => {
        const v = s.points[i];
        if (v == null) return dots[k].setAttribute("opacity", 0);
        dots[k].setAttribute("cx", X(i));
        dots[k].setAttribute("cy", Y(v));
        dots[k].setAttribute("opacity", 1);
        html += row(s.name, opts.formatValue ? opts.formatValue(v) : v.toFixed(1));
      });
      tip.show(html, evt);
    });
    hit.addEventListener("mouseleave", () => {
      cross.setAttribute("opacity", 0);
      dots.forEach((d) => d.setAttribute("opacity", 0));
      tip.hide();
    });

    return svg;
  }

  /* ── horizontal bars ─────────────────────────────────────────────── */
  function barsH(host, opts) {
    const items = opts.items || [];
    if (!items.length) return empty(host, opts.emptyMessage);

    clear(host);
    const rowH = opts.rowHeight || 30;
    const GAP = 2; // surface gap between adjacent bars
    const W = host.clientWidth || 640;
    const M = { top: 4, right: 54, bottom: 4, left: opts.labelWidth || 150 };
    const H = items.length * rowH + M.top + M.bottom;
    const iw = Math.max(W - M.left - M.right, 10);

    const maxV = opts.maxValue != null
      ? opts.maxValue
      : niceCeil(Math.max(...items.map((d) => d.value)) || 1);

    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, height: H,
                            role: "img", "aria-label": opts.title || "chart" }, host);
    const plot = el("g", { transform: `translate(${M.left},${M.top})` }, svg);

    items.forEach((d, i) => {
      const y = i * rowH + GAP / 2;
      const h = rowH - GAP * 2;
      const w = Math.max((Math.max(d.value, 0) / maxV) * iw, d.value > 0 ? 3 : 0);

      const label = el("text", {
        x: -10, y: y + h / 2 + 4, "text-anchor": "end", class: "label",
      }, plot);
      label.textContent = d.label;

      // 4px rounded data-end, square against the baseline
      el("rect", {
        x: 0, y, width: w, height: h, rx: 4,
        fill: d.color || PALETTE.seq450,
      }, plot);
      if (w > 4) {
        el("rect", { x: 0, y, width: Math.min(4, w), height: h,
                     fill: d.color || PALETTE.seq450 }, plot);
      }

      const value = el("text", { x: w + 9, y: y + h / 2 + 4, class: "value" }, plot);
      value.textContent = opts.formatValue ? opts.formatValue(d.value) : d.value;

      const hit = el("rect", { class: "hit", x: -M.left, y, width: W, height: rowH }, plot);
      hit.addEventListener("mousemove", (evt) =>
        tip.show(
          `<div><b>${d.label}</b></div>` +
            (d.tooltip || row("Value", opts.formatValue ? opts.formatValue(d.value) : d.value)),
          evt
        )
      );
      hit.addEventListener("mouseleave", () => tip.hide());
    });

    return svg;
  }

  /* ── diverging bars (signed attribution) ─────────────────────────── */
  function barsDiverging(host, opts) {
    const items = opts.items || [];
    if (!items.length) return empty(host, opts.emptyMessage);

    clear(host);
    legend(host, [
      { name: opts.positiveName || "Increases risk", color: opts.positiveColor || "#e66767" },
      { name: opts.negativeName || "Reduces risk", color: opts.negativeColor || PALETTE.series1 },
    ]);

    const rowH = opts.rowHeight || 28;
    const GAP = 2;
    const W = host.clientWidth || 640;
    const M = { top: 4, right: 16, bottom: 4, left: opts.labelWidth || 150 };
    const H = items.length * rowH + M.top + M.bottom;
    const iw = Math.max(W - M.left - M.right, 10);
    const mid = iw / 2;

    const maxAbs = Math.max(...items.map((d) => Math.abs(d.value))) || 1;

    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, height: H,
                            role: "img", "aria-label": opts.title || "chart" }, host);
    const plot = el("g", { transform: `translate(${M.left},${M.top})` }, svg);

    el("line", { x1: mid, x2: mid, y1: 0, y2: H - M.top - M.bottom,
                 stroke: css("--baseline"), "stroke-width": 1 }, plot);

    items.forEach((d, i) => {
      const y = i * rowH + GAP / 2;
      const h = rowH - GAP * 2;
      const w = Math.max((Math.abs(d.value) / maxAbs) * (mid - 6), 2);
      const positive = d.value >= 0;
      const color = positive
        ? opts.positiveColor || "#e66767"
        : opts.negativeColor || PALETTE.series1;

      const label = el("text", { x: -10, y: y + h / 2 + 4,
                                 "text-anchor": "end", class: "label" }, plot);
      label.textContent = d.label;

      el("rect", { x: positive ? mid : mid - w, y, width: w, height: h, rx: 4, fill: color }, plot);
      // square the end that meets the zero baseline
      el("rect", { x: positive ? mid : mid - Math.min(4, w), y,
                   width: Math.min(4, w), height: h, fill: color }, plot);

      const value = el("text", {
        x: positive ? mid + w + 8 : mid - w - 8, y: y + h / 2 + 4,
        "text-anchor": positive ? "start" : "end", class: "value",
      }, plot);
      value.textContent = (d.value >= 0 ? "+" : "") + d.value.toFixed(3);

      const hit = el("rect", { class: "hit", x: -M.left, y, width: W, height: rowH }, plot);
      hit.addEventListener("mousemove", (evt) =>
        tip.show(
          `<div><b>${d.label}</b></div>` +
            row("Observed", d.observed != null ? d.observed : "—") +
            row("Attribution", (d.value >= 0 ? "+" : "") + d.value.toFixed(4)) +
            row("Effect", positive ? "increases risk" : "reduces risk"),
          evt
        )
      );
      hit.addEventListener("mouseleave", () => tip.hide());
    });

    return svg;
  }

  global.Charts = {
    lineChart,
    barsH,
    barsDiverging,
    empty,
    palette: PALETTE,
    severityColor: (s) => SEVERITY_COLORS[s] || SEVERITY_COLORS.UNKNOWN,
  };
})(window);
