// app.js — мост между UI и Python (pywebview js api)

let cfg = null;
let donateWallets = null;
let updateInfo = null;

function showToast(msg, duration = 2400) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), duration);
}

function applyTheme(theme) {
  document.getElementById("body").className = "theme-" + theme;
  document.getElementById("themeIcon").textContent = theme === "dark" ? "◐" : "◑";
  localStorage.setItem("dc_theme", theme);
}

function currentTheme() {
  return document.getElementById("body").className.includes("dark") ? "dark" : "light";
}

function updateRangeFill(slider) {
  const min = parseInt(slider.min, 10);
  const max = parseInt(slider.max, 10);
  const val = parseInt(slider.value, 10);
  const pct = ((val - min) / (max - min)) * 100;
  slider.style.setProperty("--range-pct", pct + "%");
}

function renderConfig(c) {
  document.getElementById("targetFolder").value = c.target_folder;
  const slider = document.getElementById("delaySlider");
  slider.value = c.delay_hours;
  document.getElementById("delayValue").textContent = formatHours(c.delay_hours);
  updateRangeFill(slider);
  document.getElementById("sortByType").checked = !!c.sort_by_type;
  document.getElementById("autostart").checked = !!c.autostart;
  document.getElementById("enabled").checked = !!c.enabled;
  document.getElementById("telemetryEnabled").checked = c.telemetry_enabled !== false;
  document.getElementById("exclusions").value = (c.exclusions || []).join("\n");
  updateStatusUI(c.enabled);
}

function updateStatusUI(enabled) {
  const dot = document.getElementById("statusDot");
  const text = document.getElementById("statusText");
  if (enabled) {
    dot.classList.remove("off");
    text.textContent = t("status_active");
  } else {
    dot.classList.add("off");
    text.textContent = t("status_paused");
  }
}

function renderStats(stats) {
  document.getElementById("heroCount").textContent = String(stats.window_count);
  document.getElementById("heroSub").textContent = t("hero_total", {
    n: stats.total_all_time,
    files: pluralFiles(stats.total_all_time),
  });
}

function collectConfig() {
  const exclusions = document.getElementById("exclusions").value
    .split("\n").map(s => s.trim()).filter(Boolean);
  return {
    target_folder: document.getElementById("targetFolder").value,
    delay_hours: parseInt(document.getElementById("delaySlider").value, 10),
    sort_by_type: document.getElementById("sortByType").checked,
    autostart: document.getElementById("autostart").checked,
    enabled: document.getElementById("enabled").checked,
    telemetry_enabled: document.getElementById("telemetryEnabled").checked,
    exclusions: exclusions,
    language: getLang(),
  };
}

async function switchLanguage(lang) {
  setLang(lang);
  updateStatusUI(document.getElementById("enabled").checked);
  const slider = document.getElementById("delaySlider");
  document.getElementById("delayValue").textContent = formatHours(slider.value);
  const stats = await window.pywebview.api.get_stats();
  renderStats(stats);
  await window.pywebview.api.save_config(collectConfig());
  refreshDonateLabels();
  renderUpdateBanner();
}

function refreshDonateLabels() {
  if (!donateWallets) return;
  const labels = { btc: t("donate_btc"), usdt_trc20: t("donate_usdt") };
  document.querySelectorAll(".donate-chip").forEach((chip) => {
    const key = chip.dataset.wallet;
    if (donateWallets[key]) chip.textContent = labels[key];
  });
}

function positionLangFootnote() {
  const trigger = document.getElementById("langTrigger");
  const panel = document.getElementById("langPanel");
  if (!trigger || !panel) return;
  const rect = trigger.getBoundingClientRect();
  panel.style.top = `${rect.top + rect.height / 2}px`;
  panel.style.right = `${window.innerWidth - rect.left + 10}px`;
  panel.style.left = "auto";
}

function setLangPickerOpen(open) {
  const panel = document.getElementById("langPanel");
  const trigger = document.getElementById("langTrigger");
  if (!panel || !trigger) return;
  if (open) positionLangFootnote();
  panel.classList.toggle("is-open", open);
  trigger.classList.toggle("is-open", open);
  trigger.setAttribute("aria-expanded", open ? "true" : "false");
}

function initLangPicker() {
  const panel = document.getElementById("langPanel");
  const trigger = document.getElementById("langTrigger");
  if (!panel || !trigger) return;

  trigger.onclick = (e) => {
    e.stopPropagation();
    setLangPickerOpen(!panel.classList.contains("is-open"));
  };

  document.querySelectorAll(".lang-chip").forEach((btn) => {
    btn.onclick = async (e) => {
      e.stopPropagation();
      if (btn.dataset.lang === getLang()) {
        setLangPickerOpen(false);
        return;
      }
      await switchLanguage(btn.dataset.lang);
      setLangPickerOpen(false);
    };
  });

  document.addEventListener("click", (e) => {
    if (trigger.contains(e.target) || panel.contains(e.target)) return;
    setLangPickerOpen(false);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") setLangPickerOpen(false);
  });
  window.addEventListener("resize", () => {
    if (panel.classList.contains("is-open")) positionLangFootnote();
  });
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

function positionDonatePanel() {
  const btn = document.getElementById("donateBtn");
  const panel = document.getElementById("donatePanel");
  if (!btn || !panel) return;
  const rect = btn.getBoundingClientRect();
  panel.style.left = `${rect.left + rect.width / 2}px`;
  panel.style.bottom = `${window.innerHeight - rect.top + 10}px`;
  panel.style.top = "auto";
  panel.style.right = "auto";
}

function setDonatePanelOpen(open) {
  const panel = document.getElementById("donatePanel");
  const btn = document.getElementById("donateBtn");
  if (!panel || !btn) return;
  if (open) positionDonatePanel();
  panel.classList.toggle("is-open", open);
  btn.classList.toggle("is-open", open);
  btn.setAttribute("aria-expanded", open ? "true" : "false");
}

async function initDonate() {
  const btn = document.getElementById("donateBtn");
  const panel = document.getElementById("donatePanel");
  if (!btn || !panel) return;

  const wallets = await window.pywebview.api.get_donate_wallets();
  donateWallets = wallets;
  const labels = { btc: t("donate_btc"), usdt_trc20: t("donate_usdt") };

  document.querySelectorAll(".donate-chip").forEach((chip) => {
    const key = chip.dataset.wallet;
    const address = wallets[key];
    if (!address) {
      chip.hidden = true;
      return;
    }
    chip.textContent = labels[key] || key.toUpperCase();
    chip.onclick = async (e) => {
      e.stopPropagation();
      const copied = await copyText(address);
      setDonatePanelOpen(false);
      if (copied) {
        showToast(t("donate_toast", { label: labels[key] }), 2800);
      } else {
        showToast(address, 7000);
      }
    };
  });

  if (!wallets.btc && !wallets.usdt_trc20) {
    btn.hidden = true;
    return;
  }

  btn.onclick = (e) => {
    e.stopPropagation();
    setDonatePanelOpen(!panel.classList.contains("is-open"));
  };

  document.addEventListener("click", (e) => {
    if (btn.contains(e.target) || panel.contains(e.target)) return;
    setDonatePanelOpen(false);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") setDonatePanelOpen(false);
  });
  window.addEventListener("resize", () => {
    if (panel.classList.contains("is-open")) positionDonatePanel();
  });
}

function renderUpdateBanner() {
  const banner = document.getElementById("updateBanner");
  if (!banner) return;

  if (!updateInfo || !updateInfo.available || updateInfo.dismissed) {
    banner.classList.add("hidden");
    return;
  }

  document.getElementById("updateBadge").textContent = t("update_badge");
  document.getElementById("updateTitle").textContent = t("update_title");
  document.getElementById("updateSub").textContent = t("update_body", {
    version: updateInfo.latest,
    current: updateInfo.current,
  });
  document.getElementById("updateDownloadBtn").textContent = t("update_download");
  document.getElementById("updateDismissBtn").textContent = t("update_later");
  banner.classList.remove("hidden");
}

async function refreshUpdateCheck() {
  try {
    updateInfo = await window.pywebview.api.check_for_updates();
    renderUpdateBanner();
  } catch {
    /* offline or API unavailable */
  }
}
window.refreshUpdateCheck = refreshUpdateCheck;

async function initUpdateCheck() {
  const banner = document.getElementById("updateBanner");
  const downloadBtn = document.getElementById("updateDownloadBtn");
  const dismissBtn = document.getElementById("updateDismissBtn");
  if (!banner || !downloadBtn || !dismissBtn) return;

  downloadBtn.onclick = async () => {
    if (updateInfo && updateInfo.url) {
      await window.pywebview.api.open_url(updateInfo.url);
    }
  };

  dismissBtn.onclick = async () => {
    if (updateInfo && updateInfo.latest) {
      await window.pywebview.api.dismiss_update(updateInfo.latest);
      updateInfo.dismissed = true;
    }
    renderUpdateBanner();
  };

  try {
    updateInfo = await window.pywebview.api.check_for_updates();
    renderUpdateBanner();
  } catch {
    /* offline or API unavailable — skip silently */
  }
}

async function init() {
  applyTheme(localStorage.getItem("dc_theme") || "dark");

  cfg = await window.pywebview.api.get_config();
  setLang(cfg.language || "en");
  renderConfig(cfg);

  const stats = await window.pywebview.api.get_stats();
  renderStats(stats);

  initLangPicker();
  initDonate();
  initUpdateCheck();

  document.getElementById("themeToggle").onclick = () => {
    applyTheme(currentTheme() === "dark" ? "light" : "dark");
  };

  document.getElementById("minBtn").onclick = () => {
    window.pywebview.api.minimize_window();
  };

  document.getElementById("closeBtn").onclick = () => {
    window.pywebview.api.hide_to_tray();
  };

  const dragZone = document.querySelector(".titlebar__drag");
  dragZone.addEventListener("pointerdown", (e) => {
    if (e.button !== 0 || !window.pywebview || !window.pywebview._bridge) return;
    e.preventDefault();
    dragZone.setPointerCapture(e.pointerId);
    dragZone.style.cursor = "grabbing";
    window.pywebview._bridge.call("scDragStart", [e.screenX, e.screenY], "drag");

    function onMove(ev) {
      window.pywebview._bridge.call("scDragMove", [ev.screenX, ev.screenY], "move");
    }

    function onUp() {
      dragZone.releasePointerCapture(e.pointerId);
      dragZone.style.cursor = "";
      window.pywebview._bridge.call("scDragEnd", [], "drag");
      dragZone.removeEventListener("pointermove", onMove);
      dragZone.removeEventListener("pointerup", onUp);
      dragZone.removeEventListener("pointercancel", onUp);
    }

    dragZone.addEventListener("pointermove", onMove);
    dragZone.addEventListener("pointerup", onUp);
    dragZone.addEventListener("pointercancel", onUp);
  });

  const slider = document.getElementById("delaySlider");
  slider.oninput = (e) => {
    document.getElementById("delayValue").textContent = formatHours(e.target.value);
    updateRangeFill(e.target);
  };

  document.getElementById("browseBtn").onclick = async () => {
    const folder = await window.pywebview.api.pick_folder();
    if (folder) document.getElementById("targetFolder").value = folder;
  };

  document.getElementById("enabled").onchange = (e) => {
    updateStatusUI(e.target.checked);
  };

  document.getElementById("saveBtn").onclick = async () => {
    const newCfg = collectConfig();
    await window.pywebview.api.save_config(newCfg);
    showToast(t("toast_saved"));
  };

  document.getElementById("cleanNowBtn").onclick = async () => {
    showToast(t("toast_cleaning"));
    const result = await window.pywebview.api.clean_now(collectConfig());
    if (result.failed && result.failed.length) {
      const list = result.failed.map((f) => f.name + " (" + f.error + ")").join("; ");
      showToast(t("toast_partial", { n: result.moved, list: list }), 5000);
    } else {
      showToast(t("toast_moved", { n: result.moved, files: pluralFiles(result.moved) }));
    }
    renderStats(await window.pywebview.api.get_stats());
  };
}

window.addEventListener("pywebviewready", init);
