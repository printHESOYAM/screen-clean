// i18n.js — словари интерфейса (UI)

const I18N = {
  ru: {
    header_sub: "Автосортировка рабочего стола",
    theme_toggle: "Переключить тему",
    win_minimize: "Свернуть",
    win_close: "Скрыть в трей",
    status_active: "Автоочистка активна",
    status_paused: "Автоочистка выключена",
    hero_label: "файлов за 24 часа",
    hero_total: "всего {n} {files}",
    target_folder: "Папка назначения",
    target_placeholder: "Выберите папку…",
    browse: "Обзор",
    keep_on_desktop: "Хранить на столе",
    hours_short: "{n} ч",
    range_min: "1 ч",
    range_max: "7 дней",
    sort_by_type: "Сортировать по типу",
    sort_by_type_hint: "Картинки, документы, код…",
    autostart: "Автозапуск",
    autostart_hint: "Старт вместе с Windows",
    auto_clean: "Автоочистка",
    auto_clean_hint: "Фоновая проверка каждую минуту",
    telemetry: "Анонимная аналитика",
    telemetry_hint: "Помогает улучшать приложение, без личных данных",
    exclusions: "Исключения",
    exclusions_placeholder: "По одному имени на строку…",
    clean_now: "Очистить сейчас",
    save: "Сохранить",
    donate_title: "Поддержать проект",
    donate_toast: "Адрес {label} скопирован",
    donate_btc: "BTC",
    donate_usdt: "USDT TRC20",
    language: "Язык",
    toast_saved: "Настройки сохранены",
    toast_cleaning: "Очистка запущена…",
    toast_moved: "Перемещено: {n} {files}",
    toast_partial: "Перемещено: {n}. Не удалось: {list}",
    file_one: "файл",
    file_few: "файла",
    file_many: "файлов",
    update_badge: "Новое",
    update_title: "Доступно обновление",
    update_body: "Версия {version} готова · у вас {current}",
    update_download: "Скачать",
    update_later: "Позже",
  },
  en: {
    header_sub: "Automatic desktop sorting",
    theme_toggle: "Toggle theme",
    win_minimize: "Minimize",
    win_close: "Hide to tray",
    status_active: "Auto-clean is active",
    status_paused: "Auto-clean is paused",
    hero_label: "files in 24 hours",
    hero_total: "{n} total {files}",
    target_folder: "Destination folder",
    target_placeholder: "Choose a folder…",
    browse: "Browse",
    keep_on_desktop: "Keep on desktop",
    hours_short: "{n} h",
    range_min: "1 h",
    range_max: "7 days",
    sort_by_type: "Sort by file type",
    sort_by_type_hint: "Images, documents, code…",
    autostart: "Launch at startup",
    autostart_hint: "Start with Windows",
    auto_clean: "Auto-clean",
    auto_clean_hint: "Background check every minute",
    telemetry: "Anonymous analytics",
    telemetry_hint: "Help improve the app — no personal data",
    exclusions: "Exclusions",
    exclusions_placeholder: "One name per line…",
    clean_now: "Clean now",
    save: "Save",
    donate_title: "Support the project",
    donate_toast: "{label} address copied",
    donate_btc: "BTC",
    donate_usdt: "USDT TRC20",
    language: "Language",
    toast_saved: "Settings saved",
    toast_cleaning: "Cleaning…",
    toast_moved: "Moved: {n} {files}",
    toast_partial: "Moved: {n}. Failed: {list}",
    file_one: "file",
    file_few: "files",
    file_many: "files",
    update_badge: "New",
    update_title: "Update available",
    update_body: "Version {version} is ready · you have {current}",
    update_download: "Download",
    update_later: "Later",
  },
  es: {
    header_sub: "Clasificación automática del escritorio",
    theme_toggle: "Cambiar tema",
    win_minimize: "Minimizar",
    win_close: "Ocultar en la bandeja",
    status_active: "Limpieza automática activa",
    status_paused: "Limpieza automática pausada",
    hero_label: "archivos en 24 horas",
    hero_total: "{n} en total {files}",
    target_folder: "Carpeta de destino",
    target_placeholder: "Elegir carpeta…",
    browse: "Examinar",
    keep_on_desktop: "Conservar en el escritorio",
    hours_short: "{n} h",
    range_min: "1 h",
    range_max: "7 días",
    sort_by_type: "Ordenar por tipo",
    sort_by_type_hint: "Imágenes, documentos, código…",
    autostart: "Inicio automático",
    autostart_hint: "Iniciar con Windows",
    auto_clean: "Limpieza automática",
    auto_clean_hint: "Comprobación en segundo plano cada minuto",
    telemetry: "Analítica anónima",
    telemetry_hint: "Ayuda a mejorar la app, sin datos personales",
    exclusions: "Exclusiones",
    exclusions_placeholder: "Un nombre por línea…",
    clean_now: "Limpiar ahora",
    save: "Guardar",
    donate_title: "Apoyar el proyecto",
    donate_toast: "Dirección {label} copiada",
    donate_btc: "BTC",
    donate_usdt: "USDT TRC20",
    language: "Idioma",
    toast_saved: "Ajustes guardados",
    toast_cleaning: "Limpiando…",
    toast_moved: "Movidos: {n} {files}",
    toast_partial: "Movidos: {n}. Error: {list}",
    file_one: "archivo",
    file_few: "archivos",
    file_many: "archivos",
    update_badge: "Nuevo",
    update_title: "Actualización disponible",
    update_body: "Versión {version} lista · tienes {current}",
    update_download: "Descargar",
    update_later: "Después",
  },
  ja: {
    header_sub: "デスクトップの自動整理",
    theme_toggle: "テーマ切替",
    win_minimize: "最小化",
    win_close: "トレイに隠す",
    status_active: "自動整理が有効",
    status_paused: "自動整理が停止中",
    hero_label: "24時間で整理したファイル",
    hero_total: "合計 {n} {files}",
    target_folder: "移動先フォルダ",
    target_placeholder: "フォルダを選択…",
    browse: "参照",
    keep_on_desktop: "デスクトップに残す時間",
    hours_short: "{n}時間",
    range_min: "1時間",
    range_max: "7日",
    sort_by_type: "種類ごとに整理",
    sort_by_type_hint: "画像、ドキュメント、コードなど",
    autostart: "自動起動",
    autostart_hint: "Windows 起動時に開始",
    auto_clean: "自動整理",
    auto_clean_hint: "1分ごとにバックグラウンドで確認",
    telemetry: "匿名アナリティクス",
    telemetry_hint: "個人データなしで改善に協力",
    exclusions: "除外",
    exclusions_placeholder: "1行に1つの名前…",
    clean_now: "今すぐ整理",
    save: "保存",
    donate_title: "プロジェクトを支援",
    donate_toast: "{label} アドレスをコピーしました",
    donate_btc: "BTC",
    donate_usdt: "USDT TRC20",
    language: "言語",
    toast_saved: "設定を保存しました",
    toast_cleaning: "整理中…",
    toast_moved: "移動: {n}{files}",
    toast_partial: "移動: {n}。失敗: {list}",
    file_one: "件",
    file_few: "件",
    file_many: "件",
    update_badge: "新着",
    update_title: "アップデートがあります",
    update_body: "バージョン {version} が利用可能 · 現在 {current}",
    update_download: "ダウンロード",
    update_later: "後で",
  },
};

let currentLang = "en";

const LANG_CODES = { en: "EN", ru: "RU", es: "ES", ja: "JA" };

function t(key, vars = {}) {
  const dict = I18N[currentLang] || I18N.en;
  let text = dict[key] ?? I18N.en[key] ?? key;
  for (const [k, v] of Object.entries(vars)) {
    text = text.replace(new RegExp(`\\{${k}\\}`, "g"), String(v));
  }
  return text;
}

function pluralFiles(n) {
  if (currentLang === "en" || currentLang === "es") {
    return n === 1 ? t("file_one") : t("file_many");
  }
  if (currentLang === "ja") {
    return t("file_many");
  }
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod100 >= 11 && mod100 <= 19) return t("file_many");
  if (mod10 === 1) return t("file_one");
  if (mod10 >= 2 && mod10 <= 4) return t("file_few");
  return t("file_many");
}

function applyI18n() {
  document.documentElement.lang = currentLang;

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });

  document.querySelectorAll("[data-i18n-title]").forEach((el) => {
    el.title = t(el.dataset.i18nTitle);
  });

  document.querySelectorAll(".lang-chip").forEach((btn) => {
    btn.classList.toggle("lang-chip--active", btn.dataset.lang === currentLang);
  });

  const triggerLabel = document.getElementById("langTriggerLabel");
  if (triggerLabel) {
    triggerLabel.textContent = LANG_CODES[currentLang] || currentLang.toUpperCase();
  }
}

function setLang(lang) {
  if (!I18N[lang]) return;
  currentLang = lang;
  applyI18n();
}

function getLang() {
  return currentLang;
}

function formatHours(n) {
  return t("hours_short", { n });
}
