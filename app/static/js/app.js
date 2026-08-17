/* Insider Threat Behavioral Intelligence System — console application. */
(function () {
  "use strict";

  const API = "/api/v1";
  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  const state = {
    token: sessionStorage.getItem("itbis_token") || null,
    analyst: null,
    page: "dashboard",
    users: { page: 1, perPage: 25, total: 0 },
    stream: { source: null, running: false, counts: {}, seen: 0 },
    investigation: null,
  };

  const PAGE_META = {
    dashboard: ["Executive Dashboard", "Enterprise insider-threat posture"],
    monitoring: ["Live Monitoring", "Near real-time activity stream with risk context"],
    profiling: ["Behavioral Profiling", "Per-user baselines and deviation from normal"],
    alerts: ["Threat Alerts", "Incident queue ranked by composite risk"],
    investigation: ["Investigation", "Forensic case analysis and explainability"],
    reports: ["Reports & Exports", "PDF case files and Excel risk workbooks"],
  };

  /* ── helpers ─────────────────────────────────────────────────────── */
  const esc = (v) =>
    String(v == null ? "" : v).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
    );

  const sevBadge = (s) =>
    `<span class="sev sev-${esc(s || "UNKNOWN")}">${esc(s || "UNKNOWN")}</span>`;

  const num = (v, d) => (v == null || isNaN(v) ? "—" : Number(v).toFixed(d == null ? 1 : d));

  function toast(message, kind) {
    const node = $("#toast");
    node.textContent = message;
    node.className = "toast" + (kind ? " " + kind : "");
    node.hidden = false;
    clearTimeout(node._timer);
    node._timer = setTimeout(() => (node.hidden = true), 4200);
  }

  async function api(path, options) {
    const opts = Object.assign({ headers: {} }, options);
    if (state.token) opts.headers.Authorization = "Bearer " + state.token;
    if (opts.body && typeof opts.body !== "string") {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(opts.body);
    }

    // Paths are relative to the API root unless they are already absolute.
    const url = /^(https?:\/\/|\/api\/|\/health\b|\/stream\b)/.test(path) ? path : API + path;
    const res = await fetch(url, opts);
    if (res.status === 401) {
      signOut(true);
      throw new Error("Session expired — sign in again.");
    }
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const body = await res.json();
        detail = body.detail || body.error || detail;
      } catch (_) { /* non-JSON error body */ }
      throw new Error(detail);
    }
    return res.status === 204 ? null : res.json();
  }

  async function download(path, filename) {
    const res = await fetch(path, { headers: { Authorization: "Bearer " + state.token } });
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const body = await res.json();
        detail = body.detail || body.error || detail;
      } catch (_) { /* binary or empty body */ }
      throw new Error(detail);
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  /* ── auth ────────────────────────────────────────────────────────── */
  $("#login-form").addEventListener("submit", async (evt) => {
    evt.preventDefault();
    const btn = $("#login-btn");
    const err = $("#login-error");
    err.hidden = true;
    btn.disabled = true;
    btn.textContent = "Authenticating…";
    try {
      const data = await api("/auth/login", {
        method: "POST",
        body: { username: $("#username").value, password: $("#password").value },
      });
      state.token = data.access_token;
      state.analyst = data.analyst;
      sessionStorage.setItem("itbis_token", state.token);
      await enterConsole();
    } catch (e) {
      err.textContent = e.message;
      err.hidden = false;
    } finally {
      btn.disabled = false;
      btn.textContent = "Authenticate";
    }
  });

  function signOut(silent) {
    stopStream();
    state.token = null;
    state.analyst = null;
    sessionStorage.removeItem("itbis_token");
    $("#console").hidden = true;
    $("#login-screen").hidden = false;
    if (!silent) toast("Signed out.", "ok");
  }

  $("#logout-btn").addEventListener("click", async () => {
    try { await api("/auth/logout", { method: "POST" }); } catch (_) { /* already gone */ }
    signOut();
  });

  async function enterConsole() {
    $("#login-screen").hidden = true;
    $("#console").hidden = false;
    $("#who-name").textContent = state.analyst ? state.analyst.username : "—";
    $("#who-role").textContent = state.analyst ? state.analyst.role : "—";
    await refreshEngineStatus();
    await loadPage("dashboard");
  }

  async function refreshEngineStatus() {
    const pill = $("#engine-pill");
    try {
      const health = await fetch("/health").then((r) => r.json());
      const ok = health.status === "ok";
      pill.textContent = ok ? "engine ready" : "engine degraded";
      pill.className = "pill " + (ok ? "ok" : "err");
    } catch (_) {
      pill.textContent = "engine unreachable";
      pill.className = "pill err";
    }
  }

  /* ── navigation ──────────────────────────────────────────────────── */
  $("#nav").addEventListener("click", (evt) => {
    const btn = evt.target.closest(".nav-item");
    if (btn) loadPage(btn.dataset.page);
  });

  $("#refresh-btn").addEventListener("click", () => loadPage(state.page, true));

  async function loadPage(page, force) {
    state.page = page;
    $$(".nav-item").forEach((b) => b.classList.toggle("is-active", b.dataset.page === page));
    $$(".page").forEach((s) => s.classList.toggle("is-active", s.dataset.page === page));
    const meta = PAGE_META[page] || ["", ""];
    $("#page-title").textContent = meta[0];
    $("#page-sub").textContent = meta[1];

    if (page !== "monitoring") stopStream();

    try {
      if (page === "dashboard") await renderDashboard();
      else if (page === "profiling") await renderUsers();
      else if (page === "alerts") await renderAlerts();
      else if (page === "reports") await renderReportTop();
      else if (page === "investigation" && force && state.investigation) {
        await runInvestigation(state.investigation.user, state.investigation.day);
      }
    } catch (e) {
      toast(e.message, "err");
    }
  }

  /* ── dashboard ───────────────────────────────────────────────────── */
  async function renderDashboard() {
    const data = await api("/dashboard");

    const sev = data.severity_distribution || {};
    $("#dash-tiles").innerHTML = [
      tile("Monitored users", data.total_users, `${data.total_user_days.toLocaleString()} user-days analysed`),
      tile("Open alerts", data.open_alerts, "user-days above the alerting threshold", sev.CRITICAL ? "crit" : ""),
      tile("Users at risk", data.users_at_risk, "peak score in the alerting band", "high"),
      tile("Critical subjects", sev.CRITICAL || 0, "peak score 80 or above", "crit"),
      tile("Mean composite risk", num(data.mean_risk), "population average, 0–100"),
      tile("Observation window", (data.date_range || []).join(" → "), "from the ingested activity logs", "text"),
    ].join("");

    const timeline = data.risk_timeline || [];
    Charts.lineChart($("#chart-trend"), {
      title: "Daily mean and peak composite risk",
      labels: timeline.map((d) => d.day_str),
      series: [
        { name: "Mean risk", color: Charts.palette.series1, points: timeline.map((d) => d.mean_risk) },
        { name: "Peak risk", color: Charts.palette.series2, points: timeline.map((d) => d.max_risk) },
      ],
      maxY: 100,
      formatValue: (v) => v.toFixed(1),
    });

    // Severity is status data: colour is reserved, and the tier name is
    // always spelled out beside the bar so colour never carries it alone.
    const order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];
    Charts.barsH($("#chart-severity"), {
      title: "Users by peak severity",
      labelWidth: 90,
      items: order.map((k) => ({
        label: k,
        value: sev[k] || 0,
        color: Charts.severityColor(k),
        tooltip:
          `<div class="t-row"><span class="t-key">Users</span><b>${sev[k] || 0}</b></div>` +
          `<div class="t-row"><span class="t-key">Share</span><b>${
            data.total_users ? (((sev[k] || 0) / data.total_users) * 100).toFixed(1) : "0.0"
          }%</b></div>`,
      })),
      formatValue: (v) => String(v),
    });

    const ramp = [Charts.palette.seq250, Charts.palette.seq350,
                  Charts.palette.seq450, Charts.palette.seq550, Charts.palette.seq550];
    Charts.barsH($("#chart-indicators"), {
      title: "Dominant weighted risk indicators",
      labelWidth: 170,
      maxValue: 100,
      items: (data.top_indicators || []).map((d, i) => ({
        label: d.label,
        value: d.share,
        color: ramp[Math.min(i, ramp.length - 1)],
        tooltip:
          `<div class="t-row"><span class="t-key">Share of weighted risk</span><b>${d.share}%</b></div>` +
          `<div class="t-row"><span class="t-key">Indicator weight</span><b>${d.weight}×</b></div>`,
      })),
      formatValue: (v) => v.toFixed(1) + "%",
      emptyMessage: "No alerts above the threshold — nothing to attribute.",
    });

    const m = data.model || {};
    $("#model-panel").innerHTML = [
      kv("Algorithm", m.name || "—"),
      kv("Backend", m.backend || "—"),
      kv("Input features", m.features),
      kv("PR-AUC", num(m.pr_auc, 3)),
      kv("ROC-AUC", num(m.roc_auc, 3)),
      kv("Precision", num(m.precision, 3)),
      kv("Recall", num(m.recall, 3)),
      kv("F1 score", num(m.f1, 3)),
      kv("Confirmed insiders in data", data.confirmed_insiders),
    ].join("");

    $("#nav-alert-count").textContent = data.open_alerts ? data.open_alerts : "";
  }

  const tile = (label, value, note, kind) =>
    `<div class="tile"><div class="tile-label">${esc(label)}</div>
     <div class="tile-value ${kind || ""}">${esc(value)}</div>
     <div class="tile-note">${esc(note || "")}</div></div>`;

  const kv = (k, v) => `<span class="k">${esc(k)}</span><span class="v">${esc(v)}</span>`;

  /* ── live monitoring ─────────────────────────────────────────────── */
  $("#stream-toggle").addEventListener("click", () =>
    state.stream.running ? stopStream() : startStream()
  );

  function startStream() {
    if (state.stream.running) return;
    const url = `/stream?token=${encodeURIComponent(state.token)}&batch=3`;
    const source = new EventSource(url);
    state.stream.source = source;
    state.stream.running = true;
    $("#stream-toggle").textContent = "Stop stream";

    source.addEventListener("open", () => setStreamStatus("streaming", "ok"));
    source.addEventListener("activity", (evt) => {
      try { appendEvents(JSON.parse(evt.data)); } catch (_) { /* malformed frame */ }
    });
    source.addEventListener("error", () => {
      setStreamStatus("reconnecting…", "err");
    });
    setStreamStatus("connecting…");
  }

  function stopStream() {
    if (state.stream.source) state.stream.source.close();
    state.stream.source = null;
    state.stream.running = false;
    $("#stream-toggle").textContent = "Start stream";
    setStreamStatus("disconnected");
  }

  function setStreamStatus(text, kind) {
    const pill = $("#stream-status");
    pill.textContent = text;
    pill.className = "pill" + (kind ? " " + kind : "");
  }

  function appendEvents(events) {
    const body = $("#stream-table tbody");
    events.forEach((e) => {
      state.stream.seen += 1;
      const key = e.severity || "UNKNOWN";
      state.stream.counts[key] = (state.stream.counts[key] || 0) + 1;
      if (e.off_hours) state.stream.counts.OFF_HOURS = (state.stream.counts.OFF_HOURS || 0) + 1;

      const tr = document.createElement("tr");
      tr.className = "row-new";
      tr.innerHTML = `
        <td class="mono">${esc(e.timestamp)}</td>
        <td class="mono">${esc(e.user)}</td>
        <td>${esc(e.source)}</td>
        <td>${esc(e.pc)}</td>
        <td class="wide">${esc(e.detail)}</td>
        <td>${e.off_hours ? "off-hours" : "business"}</td>
        <td class="num">${e.risk_score == null ? "—" : num(e.risk_score)}</td>
        <td>${sevBadge(e.severity)}</td>`;
      body.insertBefore(tr, body.firstChild);
    });
    while (body.children.length > 200) body.removeChild(body.lastChild);

    const c = state.stream.counts;
    $("#stream-tiles").innerHTML = [
      tile("Events observed", state.stream.seen, "since the stream started"),
      tile("Critical-context", c.CRITICAL || 0, "events on a critical-risk user-day", "crit"),
      tile("High-context", c.HIGH || 0, "events on a high-risk user-day", "high"),
      tile("Off-hours", c.OFF_HOURS || 0, "outside 07:00–18:00"),
    ].join("");
  }

  /* ── behavioural profiling ───────────────────────────────────────── */
  let searchTimer = null;
  $("#profile-search").addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => { state.users.page = 1; renderUsers(); }, 250);
  });
  $("#profile-severity").addEventListener("change", () => {
    state.users.page = 1;
    renderUsers();
  });
  $("#profile-close").addEventListener("click", () => ($("#profile-detail").hidden = true));

  async function renderUsers() {
    const params = new URLSearchParams({
      page: state.users.page,
      per_page: state.users.perPage,
      search: $("#profile-search").value.trim(),
      severity: $("#profile-severity").value,
    });
    const data = await api("/users?" + params);
    state.users.total = data.total;

    $("#users-table tbody").innerHTML = data.items.length
      ? data.items.map((u) => `
        <tr>
          <td class="mono">${esc(u.user)}</td>
          <td>${esc(u.name || "—")}</td>
          <td>${esc(u.department || "—")}</td>
          <td class="num">${num(u.peak_risk)}</td>
          <td class="num">${num(u.mean_risk)}</td>
          <td class="num">${u.flagged_days}</td>
          <td>${sevBadge(u.severity)}</td>
          <td><button class="btn btn-ghost btn-xs" data-profile="${esc(u.user)}">Profile</button></td>
        </tr>`).join("")
      : `<tr><td colspan="8" class="muted" style="padding:20px">No users match the current filter.</td></tr>`;

    const pages = data.pages;
    $("#users-pager").innerHTML =
      `<span class="muted">${data.total.toLocaleString()} users · page ${data.page} of ${pages}</span>
       <button class="btn btn-ghost btn-xs" data-page-move="-1" ${data.page <= 1 ? "disabled" : ""}>← Prev</button>
       <button class="btn btn-ghost btn-xs" data-page-move="1" ${data.page >= pages ? "disabled" : ""}>Next →</button>`;
  }

  document.addEventListener("click", async (evt) => {
    const move = evt.target.closest("[data-page-move]");
    if (move) {
      state.users.page += Number(move.dataset.pageMove);
      return renderUsers().catch((e) => toast(e.message, "err"));
    }
    const prof = evt.target.closest("[data-profile]");
    if (prof) return showProfile(prof.dataset.profile).catch((e) => toast(e.message, "err"));

    const inv = evt.target.closest("[data-investigate]");
    if (inv) {
      const [user, day] = inv.dataset.investigate.split("|");
      await loadPage("investigation");
      $("#inv-user").value = user;
      $("#inv-day").value = day || "";
      return runInvestigation(user, day).catch((e) => toast(e.message, "err"));
    }
    const rep = evt.target.closest("[data-report]");
    if (rep) {
      await loadPage("reports");
      $("#rep-user").value = rep.dataset.report;
      return;
    }
  });

  async function showProfile(user) {
    const p = await api(`/users/${encodeURIComponent(user)}/profile`);
    $("#profile-detail").hidden = false;
    $("#profile-name").textContent = `${p.user} — ${p.identity.name || "Unknown"}`;
    $("#profile-meta").textContent =
      `${p.identity.role || "Unknown role"} · ${p.identity.department || "Unknown dept"} · ` +
      `${p.active_days} active days · ${p.flagged_days} flagged`;

    Charts.lineChart($("#chart-profile"), {
      title: `Risk history for ${p.user}`,
      labels: p.timeline.map((d) => d.day),
      series: [{ name: "Composite risk", color: Charts.palette.series1,
                 points: p.timeline.map((d) => d.risk_score) }],
      maxY: 100,
    });

    $("#baseline-table tbody").innerHTML = p.baseline
      .map((b) => `<tr>
        <td>${esc(b.label)}</td>
        <td class="num">${num(b.baseline_mean, 2)}</td>
        <td class="num">${num(b.observed_mean, 2)}</td>
        <td class="num">${num(b.observed_max, 2)}</td></tr>`)
      .join("");

    $("#profile-detail").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  /* ── alerts ──────────────────────────────────────────────────────── */
  $("#alert-severity").addEventListener("change", () => renderAlerts().catch(reportErr));
  $("#alert-min").addEventListener("change", () => renderAlerts().catch(reportErr));
  const reportErr = (e) => toast(e.message, "err");

  async function renderAlerts() {
    const params = new URLSearchParams({ limit: 200 });
    if ($("#alert-severity").value) params.set("severity", $("#alert-severity").value);
    if ($("#alert-min").value) params.set("min_score", $("#alert-min").value);

    const data = await api("/alerts?" + params);
    $("#alerts-table tbody").innerHTML = data.items.length
      ? data.items.map((a) => `
        <tr>
          <td>${sevBadge(a.severity)}</td>
          <td class="mono">${esc(a.user)}</td>
          <td>${esc(a.name || "—")}</td>
          <td class="mono">${esc(a.day)}</td>
          <td class="num">${num(a.risk_score)}</td>
          <td class="num">${num(a.ueba_score)}</td>
          <td class="num">${num(a.ml_probability, 3)}</td>
          <td>${esc(a.top_indicator)}</td>
          <td>${esc(a.status)}${a.confirmed_insider ? " · confirmed" : ""}</td>
          <td><button class="btn btn-ghost btn-xs"
               data-investigate="${esc(a.user)}|${esc(a.day)}">Investigate</button></td>
        </tr>`).join("")
      : `<tr><td colspan="10" class="muted" style="padding:20px">No alerts match the current filter.</td></tr>`;

    $("#nav-alert-count").textContent = data.count || "";
  }

  /* ── investigation ───────────────────────────────────────────────── */
  $("#inv-run").addEventListener("click", () => {
    const user = $("#inv-user").value.trim();
    if (!user) return toast("Enter a user ID to investigate.", "err");
    runInvestigation(user, $("#inv-day").value || null).catch(reportErr);
  });

  async function runInvestigation(user, day) {
    const params = day ? "?day=" + encodeURIComponent(day) : "";
    const c = await api(`/investigate/${encodeURIComponent(user)}${params}`);
    state.investigation = { user: c.user, day: c.day };

    $("#inv-empty").hidden = true;
    $("#inv-result").hidden = false;
    $("#inv-user").value = c.user;
    $("#inv-day").value = c.day;

    $("#inv-tiles").innerHTML = [
      tile("Composite risk", num(c.risk_score), `${c.severity} · scored 0–100`,
           c.severity === "CRITICAL" ? "crit" : c.severity === "HIGH" ? "high" : ""),
      tile("UEBA behavioural", num(c.ueba_score), "weighted deviation from baseline"),
      tile("ML probability", num(c.ml_probability, 3), "Gradient Boosting classifier"),
      tile("Subject", c.user, `${(c.identity && c.identity.name) || "Unknown"} · ${c.day}`, "text"),
      tile("Baseline depth", c.baseline_days + " days", "history behind this comparison"),
      tile("Ground truth", c.confirmed_insider ? "Confirmed" : "Unlabelled",
           "from the CERT answer key", c.confirmed_insider ? "text crit" : "text"),
    ].join("");

    Charts.barsH($("#chart-contrib"), {
      title: "Weighted risk contributions",
      labelWidth: 170,
      items: c.risk_contributions.map((d) => ({
        label: d.label,
        value: d.points,
        color: Charts.palette.seq450,
        tooltip:
          `<div class="t-row"><span class="t-key">Points added</span><b>${d.points.toFixed(2)}</b></div>` +
          `<div class="t-row"><span class="t-key">Weight</span><b>${d.weight}×</b></div>` +
          `<div class="t-row"><span class="t-key">Intensity</span><b>${d.intensity.toFixed(2)}</b></div>`,
      })),
      formatValue: (v) => v.toFixed(1),
    });

    $("#shap-title").textContent =
      c.explanation.method === "shap"
        ? "SHAP feature attribution"
        : "Model importance attribution";
    Charts.barsDiverging($("#chart-shap"), {
      title: "Feature attribution",
      labelWidth: 170,
      items: c.explanation.features.map((f) => ({
        label: f.label, value: f.contribution, observed: f.value,
      })),
    });

    $("#dev-table tbody").innerHTML = c.deviations
      .map((d) => `<tr>
        <td>${esc(d.label)}${d.weighted ? ` <span class="muted">(${d.weight}×)</span>` : ""}</td>
        <td class="num">${num(d.observed, 1)}</td>
        <td class="num">${num(d.baseline, 2)}</td>
        <td class="num">${d.deviation_sigma >= 0 ? "+" : ""}${num(d.deviation_sigma, 2)}</td>
        <td class="num">${d.pct_change == null ? "—" : (d.pct_change > 0 ? "+" : "") + num(d.pct_change, 0) + "%"}</td>
        <td>${d.weighted ? d.weight + "×" : "—"}</td>
        <td>${d.anomalous ? '<span class="sev sev-HIGH">ANOMALY</span>' : ""}</td>
      </tr>`)
      .join("");

    Charts.lineChart($("#chart-inv-timeline"), {
      title: `Composite risk timeline for ${c.user}`,
      labels: c.timeline.map((d) => d.day),
      series: [{ name: "Composite risk", color: Charts.palette.series1,
                 points: c.timeline.map((d) => d.risk_score) }],
      maxY: 100,
    });
  }

  $("#inv-pdf").addEventListener("click", () => {
    if (!state.investigation) return;
    const { user, day } = state.investigation;
    download(`${API}/export/pdf?user=${encodeURIComponent(user)}&day=${encodeURIComponent(day)}`,
             `Investigation_Report_${user}_${day}.pdf`)
      .then(() => toast("Case file downloaded.", "ok"))
      .catch(reportErr);
  });

  $("#inv-xlsx").addEventListener("click", () => {
    if (!state.investigation) return;
    const { user } = state.investigation;
    download(`${API}/export/excel?user=${encodeURIComponent(user)}`,
             `ITBIS_Risk_Export_${user}.xlsx`)
      .then(() => toast("Workbook downloaded.", "ok"))
      .catch(reportErr);
  });

  /* ── reports ─────────────────────────────────────────────────────── */
  $("#rep-pdf").addEventListener("click", () => {
    const user = $("#rep-user").value.trim();
    if (!user) return toast("Enter a subject user ID.", "err");
    const day = $("#rep-day").value;
    const qs = new URLSearchParams({ user });
    if (day) qs.set("day", day);
    download(`${API}/export/pdf?` + qs, `Investigation_Report_${user}.pdf`)
      .then(() => toast("Case file downloaded.", "ok"))
      .catch(reportErr);
  });

  $("#rep-xlsx").addEventListener("click", () => {
    const qs = new URLSearchParams();
    if ($("#rep-sev").value) qs.set("severity", $("#rep-sev").value);
    if ($("#rep-min").value) qs.set("min_score", $("#rep-min").value);
    if ($("#rep-xuser").value.trim()) qs.set("user", $("#rep-xuser").value.trim());
    download(`${API}/export/excel?` + qs, "ITBIS_Risk_Export.xlsx")
      .then(() => toast("Workbook downloaded.", "ok"))
      .catch(reportErr);
  });

  async function renderReportTop() {
    const data = await api("/users?per_page=15&sort=peak_risk");
    $("#report-top tbody").innerHTML = data.items
      .map((u) => `<tr>
        <td class="mono">${esc(u.user)}</td>
        <td>${esc(u.name || "—")}</td>
        <td class="num">${num(u.peak_risk)}</td>
        <td>${sevBadge(u.severity)}</td>
        <td class="num">${u.flagged_days}</td>
        <td><button class="btn btn-ghost btn-xs" data-report="${esc(u.user)}">Use subject</button></td>
      </tr>`)
      .join("");
  }

  /* ── boot ────────────────────────────────────────────────────────── */
  let resizeTimer = null;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => loadPage(state.page, true).catch(() => {}), 220);
  });

  (async function boot() {
    if (!state.token) return;
    try {
      state.analyst = await api("/auth/me");
      await enterConsole();
    } catch (_) {
      signOut(true);
    }
  })();
})();
