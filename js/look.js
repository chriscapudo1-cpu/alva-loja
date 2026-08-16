(() => {
  const THEMES = {
    escuro: { bg: "#0b0a09", text: "#f3ece0", accent: "#c4a36a" },
    claro: { bg: "#f4efe6", text: "#1b1713", accent: "#9a7040" },
    oceano: { bg: "#0b1218", text: "#e8eef3", accent: "#6eb3c7" },
    vinho: { bg: "#140b0d", text: "#f3e8e6", accent: "#c47a6a" },
    floresta: { bg: "#0c110d", text: "#e8efe6", accent: "#8aaa6e" },
  };

  const hexToRgb = (hex) => {
    const n = String(hex || "").replace("#", "");
    if (n.length !== 6) return [11, 10, 9];
    return [0, 2, 4].map((i) => parseInt(n.slice(i, i + 2), 16));
  };

  const toHex = (rgb) =>
    `#${rgb.map((v) => Math.max(0, Math.min(255, v)).toString(16).padStart(2, "0")).join("")}`;

  const mix = (a, b, t) => {
    const A = hexToRgb(a);
    const B = hexToRgb(b);
    return toHex(A.map((v, i) => Math.round(v + (B[i] - v) * t)));
  };

  const rgba = (hex, alpha) => {
    const [r, g, b] = hexToRgb(hex);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  };

  const apply = (site) => {
    if (!site || typeof site !== "object") return;
    const preset = THEMES[site.theme] || THEMES.escuro;
    const bg = site.colorBg || preset.bg;
    const text = site.colorText || preset.text;
    const accent = site.colorAccent || preset.accent;
    const light = mix(bg, "#ffffff", 0.72);
    const root = document.documentElement;
    const set = (key, value) => root.style.setProperty(key, value);
    set("--bg", bg);
    set("--bg-2", mix(bg, text, 0.06));
    set("--bg-3", mix(bg, text, 0.12));
    set("--cream", text);
    set("--cream-dim", mix(text, bg, 0.22));
    set("--muted", mix(text, bg, 0.42));
    set("--gold", accent);
    set("--gold-2", mix(accent, text, 0.35));
    set("--rust", mix(accent, "#c45c32", 0.45));
    set("--line", rgba(text, 0.12));
    set("--line-strong", rgba(text, 0.22));
    set("--photo-bg", light);
    root.style.background = bg;
    document.body.style.background = bg;
    document.body.dataset.theme = site.theme || "escuro";
    document.body.dataset.font = site.font || "editorial";
    document.body.dataset.radius = site.radius || "reta";
    document.body.dataset.density = site.density || "confortavel";
    document.body.dataset.hero = site.heroStyle || "capa";
    document.body.dataset.cols = site.shopCols || "3";
    document.body.classList.toggle("hide-promises", site.showPromises === "nao");
    document.body.classList.toggle("hide-cats", site.showCats === "nao");
    document.body.classList.toggle("hide-feat", site.showFeat === "nao");
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", bg);
  };

  window.AlvaLook = { THEMES, apply, mix };
})();
