(() => {
  const year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());

  const applySite = (site) => {
    if (!site || typeof site !== "object") return;
    document.querySelectorAll("[data-site]").forEach((el) => {
      const key = el.getAttribute("data-site");
      const value = site[key];
      if (value == null || value === "") return;
      if (el.tagName === "A" && (el.getAttribute("href") || "").startsWith("mailto:")) {
        el.setAttribute("href", `mailto:${value}`);
      }
      if (el.children.length && !el.hasAttribute("data-site-html")) return;
      el.textContent = value;
    });
    const home = /(?:^|\/)(?:index\.html)?$/.test(location.pathname.replace(/\\/g, "/"));
    if (home && site.title) document.title = site.title;
    window.AlvaLook?.apply(site);
  };
  fetch("/api/site")
    .then((res) => (res.ok ? res.json() : null))
    .then(applySite)
    .catch(() => {});

  const clock = document.getElementById("clock");
  const tick = () => {
    if (!clock) return;
    clock.textContent = new Intl.DateTimeFormat("pt-BR", {
      timeZone: "America/Sao_Paulo",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date());
  };
  tick();
  setInterval(tick, 15000);

  const loader = document.getElementById("loader");
  const preview = new URLSearchParams(location.search).has("preview");
  const hideLoader = () => {
    if (!loader || loader.classList.contains("is-done")) return;
    loader.classList.add("is-done");
    window.setTimeout(() => {
      loader.classList.add("is-gone");
      loader.setAttribute("hidden", "");
      if (location.hash) {
        document.querySelector(location.hash)?.scrollIntoView({ behavior: "auto", block: "start" });
      }
    }, 750);
  };
  const path = location.pathname.replace(/\\/g, "/");
  const isHome = /(?:^|\/)(?:index\.html)?$/.test(path);
  if (preview || !isHome) {
    hideLoader();
    loader?.classList.add("is-gone");
    loader?.setAttribute("hidden", "");
  } else {
    window.addEventListener("load", () => setTimeout(hideLoader, 550));
    setTimeout(hideLoader, 1600);
  }

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const reveals = document.querySelectorAll(".reveal");
  if (preview) {
    reveals.forEach((el) => el.classList.add("is-in"));
    const shot = new URLSearchParams(location.search).get("shot");
    if (shot) document.getElementById(shot)?.scrollIntoView({ behavior: "auto", block: "start" });
  } else if (reduce) {
    reveals.forEach((el) => el.classList.add("is-in"));
  } else if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        });
      },
      { threshold: 0.16, rootMargin: "0px 0px -8% 0px" }
    );
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add("is-in"));
  }

  const nav = document.getElementById("nav");
  let lastY = window.scrollY;
  const onScroll = () => {
    if (!nav) return;
    const y = window.scrollY;
    const hide =
      window.innerWidth >= 720 &&
      y > lastY &&
      y > 80 &&
      !document.body.classList.contains("menu-open");
    nav.classList.toggle("is-hidden", hide);
    nav.classList.toggle("is-solid", y > 24);
    lastY = y;
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  const menu = document.getElementById("menu");
  const menuBtn = document.getElementById("menuBtn");
  const setMenu = (open) => {
    if (!menu || !menuBtn) return;
    menu.hidden = !open;
    menuBtn.classList.toggle("is-open", open);
    menuBtn.setAttribute("aria-expanded", String(open));
    menuBtn.textContent = open ? "Fechar" : "Menu";
    document.body.classList.toggle("menu-open", open);
    document.documentElement.classList.toggle("menu-open", open);
  };

  if (new URLSearchParams(location.search).has("menu")) setMenu(true);
  menuBtn?.addEventListener("click", () => setMenu(menu?.hidden));
  menu?.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => setMenu(false)));
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") setMenu(false);
  });

  const form = document.getElementById("form");
  const formOk = document.getElementById("formOk");
  const emailOk = (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);

  const showErr = (name, message) => {
    const field = form?.elements.namedItem(name);
    const err = form?.querySelector(`.form__err[data-for="${name}"]`);
    if (field instanceof HTMLElement) field.classList.toggle("is-invalid", Boolean(message));
    if (err) err.textContent = message;
  };

  form?.addEventListener("submit", (e) => {
    e.preventDefault();
    const data = new FormData(form);
    const nome = String(data.get("nome") || "").trim();
    const email = String(data.get("email") || "").trim();
    const mensagem = String(data.get("mensagem") || data.get("projeto") || "").trim();
    const assunto = String(data.get("assunto") || data.get("orcamento") || "").trim();
    let ok = true;

    showErr("nome", nome ? "" : "Escreva seu nome.");
    showErr("email", emailOk(email) ? "" : "E-mail inválido.");
    showErr("mensagem", mensagem.length >= 8 ? "" : "Escreva um pouco mais.");
    showErr("assunto", assunto ? "" : "Escolha um assunto.");
    showErr("projeto", "");
    showErr("orcamento", "");

    if (!nome || !emailOk(email) || mensagem.length < 8 || !assunto) ok = false;
    if (!ok) {
      form.querySelector(".is-invalid")?.focus();
      return;
    }

    const btn = form.querySelector("button[type=submit]");
    if (btn) btn.disabled = true;
    fetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: nome, email, subject: assunto, message: mensagem }),
    })
      .then(async (res) => {
        const payload = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(payload.error || "Não enviou.");
        form.reset();
        form.classList.add("is-sent");
        if (formOk) formOk.hidden = false;
      })
      .catch((error) => {
        showErr("mensagem", error.message || "Não foi possível enviar agora.");
      })
      .finally(() => {
        if (btn) btn.disabled = false;
      });
  });

  const fine = window.matchMedia("(pointer: fine)").matches;
  const cursor = document.getElementById("cursor");
  if (fine && cursor && !reduce) {
    document.body.classList.add("has-cursor");
    cursor.style.opacity = "0";
    window.addEventListener("pointermove", () => { cursor.style.opacity = "1"; }, { once: true });
    const label = cursor.querySelector(".cursor__label");
    let x = 0;
    let y = 0;
    let cx = 0;
    let cy = 0;

    window.addEventListener("pointermove", (e) => {
      x = e.clientX;
      y = e.clientY;
    });

    const loop = () => {
      cx += (x - cx) * 0.18;
      cy += (y - cy) * 0.18;
      cursor.style.transform = `translate(${cx}px, ${cy}px)`;
      requestAnimationFrame(loop);
    };
    loop();

    const hoverables = document.querySelectorAll("a, button, input, textarea, select, .magnetic");
    hoverables.forEach((el) => {
      el.addEventListener("pointerenter", () => {
        const view = el.getAttribute("data-cursor");
        cursor.classList.toggle("is-view", Boolean(view));
        cursor.classList.toggle("is-hover", !view);
        if (label) label.textContent = view || "";
      });
      el.addEventListener("pointerleave", () => {
        cursor.classList.remove("is-view", "is-hover");
        if (label) label.textContent = "";
      });
    });

    document.querySelectorAll(".magnetic").forEach((el) => {
      el.addEventListener("pointermove", (e) => {
        const r = el.getBoundingClientRect();
        const dx = e.clientX - (r.left + r.width / 2);
        const dy = e.clientY - (r.top + r.height / 2);
        el.style.transform = `translate(${dx * 0.18}px, ${dy * 0.18}px)`;
      });
      el.addEventListener("pointerleave", () => {
        el.style.transform = "";
      });
    });
  }

  if (!/admin\.html$/i.test(location.pathname)) {
    const msg = encodeURIComponent("Olá, vim da ALVA (alvaloja.com).");
    const home = /(?:^|\/)(?:index\.html)?$/.test(location.pathname);
    const fab = document.createElement("a");
    fab.className = "fab";
    fab.href = home ? "#contato" : "index.html#contato";
    fab.setAttribute("aria-label", "Fale com a ALVA");
    fab.innerHTML = `
      <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20.5 3.5A11 11 0 0 0 2.1 17.2L1 23l5.9-1.1A11 11 0 0 0 20.5 3.5Zm-8.5 17a9.1 9.1 0 0 1-4.6-1.3l-.3-.2-3.5.7.7-3.4-.2-.3A9.1 9.1 0 1 1 12 20.5Zm5-6.8c-.3-.1-1.6-.8-1.9-.9s-.4-.1-.6.1-.7.9-.8 1-.3.2-.6.1a7.4 7.4 0 0 1-2.2-1.4 8.2 8.2 0 0 1-1.5-1.9c-.2-.3 0-.4.1-.6l.4-.4.1-.3c0-.1 0-.3 0-.4s-.6-1.4-.8-1.9-.4-.4-.6-.4h-.5c-.2 0-.4.1-.6.3s-.8.8-.8 1.9.8 2.2.9 2.3a9.7 9.7 0 0 0 3.5 3.4c1.3.7 1.8.8 2.4.6s1.6-.7 1.8-1.3.2-1.2.1-1.3-.2-.2-.5-.3Z"/></svg>
      <span>Fale conosco</span>
    `;
    document.body.appendChild(fab);
    fetch("/api/config")
      .then((res) => res.json())
      .then((cfg) => {
        window.AlvaPixel?.start(cfg.pixelId);
        const phone = String(cfg.whatsapp || "").replace(/\D/g, "");
        if (phone.length < 10) return;
        fab.href = `https://wa.me/${phone}?text=${msg}`;
        fab.target = "_blank";
        fab.rel = "noopener noreferrer";
        fab.setAttribute("aria-label", "Falar no WhatsApp");
        const label = fab.querySelector("span");
        if (label) label.textContent = "WhatsApp";
      })
      .catch(() => {});
  }

  if (!/admin\.html$/i.test(location.pathname)) {
    const links = document.querySelector(".nav__links");
    if (links && !links.querySelector('[href="admin.html"]')) {
      const a = document.createElement("a");
      a.href = "admin.html";
      a.textContent = "Admin";
      links.appendChild(a);
    }
    const meta = document.querySelector(".nav__meta");
    if (meta && !meta.querySelector('[href="admin.html"]')) {
      const a = document.createElement("a");
      a.className = "nav__admin";
      a.href = "admin.html";
      a.textContent = "Admin";
      meta.insertBefore(a, meta.firstChild);
    }
    const menuNav = document.querySelector(".menu__nav");
    if (menuNav && !menuNav.querySelector('[href="admin.html"]')) {
      const a = document.createElement("a");
      a.href = "admin.html";
      a.dataset.index = "05";
      a.textContent = "Admin";
      menuNav.appendChild(a);
    }
    document.querySelectorAll(".footer__copy").forEach((el) => {
      if (el.querySelector('[href="admin.html"]')) return;
      el.insertAdjacentHTML("beforeend", ' <a href="admin.html">Admin</a>');
    });
  }
})();
