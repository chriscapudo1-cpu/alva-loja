(() => {
  const KEY = "lume-cart";
  const isAdmin = /admin\.html$/i.test(location.pathname);

  window.AlvaPixel = {
    queue: [],
    track(event, payload) {
      if (typeof window.fbq === "function") {
        window.fbq("track", event, payload || {});
        return;
      }
      this.queue.push([event, payload || {}]);
    },
    start(pixelId) {
      const id = String(pixelId || "").replace(/\D/g, "");
      if (!id || window.fbq) {
        if (window.fbq) this.queue.splice(0).forEach(([event, payload]) => window.fbq("track", event, payload));
        return;
      }
      const fbq = (window.fbq = function () {
        fbq.callMethod ? fbq.callMethod.apply(fbq, arguments) : fbq.queue.push(arguments);
      });
      if (!window._fbq) window._fbq = fbq;
      fbq.push = fbq;
      fbq.loaded = true;
      fbq.version = "2.0";
      fbq.queue = [];
      const script = document.createElement("script");
      script.async = true;
      script.src = "https://connect.facebook.net/en_US/fbevents.js";
      document.head.appendChild(script);
      window.fbq("init", id);
      window.fbq("track", "PageView");
      this.queue.splice(0).forEach(([event, payload]) => window.fbq("track", event, payload));
      if (!document.getElementById("alvaPixelImg")) {
        const img = document.createElement("img");
        img.id = "alvaPixelImg";
        img.height = 1;
        img.width = 1;
        img.alt = "";
        img.style.display = "none";
        img.src = `https://www.facebook.com/tr?id=${id}&ev=PageView&noscript=1`;
        document.body.appendChild(img);
      }
    },
  };

  const brl = (value) =>
    Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

  const esc = (value) =>
    String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");

  const parcel = (price) => brl(Number(price) / 3);

  const choiceLabel = (options) => {
    if (!options) return "";
    if (typeof options === "string") return options;
    return Object.values(options)
      .filter(Boolean)
      .join(" · ");
  };

  const optionKey = (options) => {
    const opts = options && typeof options === "object" ? options : {};
    return Object.keys(opts)
      .sort()
      .map((name) => `${name}:${opts[name]}`)
      .join("|");
  };

  const lineId = (item) => {
    const key = optionKey(item?.options);
    return key ? `${item.id}::${key}` : item.id;
  };

  const pickOptions = (product, chosen) => {
    const groups = product?.options || [];
    if (!groups.length) return {};
    const incoming = chosen && typeof chosen === "object" ? chosen : {};
    const out = {};
    groups.forEach((group) => {
      const values = group.values || [];
      if (!group.name || !values.length) return;
      out[group.name] = values.includes(incoming[group.name]) ? incoming[group.name] : values[0];
    });
    return out;
  };

  const COLOR_HEX = {
    preto: "#1c1c1c",
    branco: "#f4f1ea",
    cinza: "#8b8680",
    bege: "#d7c4a3",
    marrom: "#6b4423",
    azul: "#3a5a8c",
    verde: "#4a7a58",
    vermelho: "#a33c2c",
    rosa: "#d48a9b",
    lilas: "#9b7ab3",
    dourado: "#c4a36a",
    prata: "#c5c5c5",
    inox: "#b8bdc4",
    amarelo: "#d4b44a",
    laranja: "#d4783a",
    roxo: "#6b4a8c",
    nude: "#e0c8b0",
    "off-white": "#eee8dc",
    vinho: "#6e2430",
    grafite: "#4a4a4a",
    camel: "#c49a6c",
    khaki: "#b8a06a",
    militar: "#4d5c3a",
    offwhite: "#eee8dc",
    transparente: "#c8cdd3",
    tartaruga: "#6b4a2b",
  };

  const foldColor = (value) =>
    String(value || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z]/g, "");

  const colorHex = (value, group) => {
    const custom = group && group.hex && group.hex[value];
    if (custom) return custom;
    return COLOR_HEX[foldColor(value)] || "#8d8578";
  };

  const isLightHex = (hex) => {
    const h = String(hex || "").replace("#", "");
    if (h.length !== 6) return false;
    const r = parseInt(h.slice(0, 2), 16);
    const g = parseInt(h.slice(2, 4), 16);
    const b = parseInt(h.slice(4, 6), 16);
    return 0.299 * r + 0.587 * g + 0.114 * b > 186;
  };

  const isColorGroup = (name) => /cor|color/i.test(name || "");

  const optionPreview = (product) => {
    const groups = product?.options || [];
    if (!groups.length) return "";
    return `<div class="product__vars">${groups
      .map((group) => {
        const values = group.values || [];
        if (isColorGroup(group.name)) {
          const dots = values
            .map((val) => {
              const hex = colorHex(val, group);
              const light = isLightHex(hex) ? " is-light" : "";
              return `<span class="var-dot${light}" style="background:${hex}" title="${esc(val)}"></span>`;
            })
            .join("");
          return `<div class="var-row"><span class="var-label">${esc(group.name)}</span>${dots}<span class="var-vals">${esc(
            values.join(" · ")
          )}</span></div>`;
        }
        return `<div class="var-row"><span class="var-label">${esc(group.name)}</span><span class="var-vals">${esc(
          values.join(" · ")
        )}</span></div>`;
      })
      .join("")}</div>`;
  };

  const read = () => {
    try {
      const data = JSON.parse(localStorage.getItem(KEY) || "[]");
      return Array.isArray(data) ? data : [];
    } catch {
      return [];
    }
  };

  const write = (items) => {
    localStorage.setItem(KEY, JSON.stringify(items));
    paint();
    drawDrawer();
  };

  const count = () => read().reduce((sum, item) => sum + Number(item.qty || 0), 0);

  const paint = () => {
    const total = count();
    document.querySelectorAll("[data-cart-count]").forEach((el) => {
      el.textContent = String(total);
      el.hidden = total === 0;
    });
  };

  let catalog = [];
  let catalogPromise = null;

  const loadCatalog = () => {
    if (catalogPromise) return catalogPromise;
    catalogPromise = fetch("/api/products")
      .then((res) => res.json())
      .then((data) => {
        catalog = data.products || [];
        window.LumeCart.catalog = catalog;
        const items = read().map((item) => {
          const product = catalog.find((entry) => entry.id === item.id);
          return product ? { ...item, options: pickOptions(product, item.options) } : item;
        });
        localStorage.setItem(KEY, JSON.stringify(items));
        document.dispatchEvent(new CustomEvent("alva:catalog", { detail: catalog }));
        paint();
        drawDrawer();
        return catalog;
      })
      .catch(() => {
        catalogPromise = null;
        return [];
      });
    return catalogPromise;
  };

  const find = (id) => catalog.find((item) => item.id === id);

  const gallery = (product) => {
    const photos = [...new Set([product.image, ...(product.images || [])].filter(Boolean))];
    return photos;
  };

  const card = (product) => {
    const photos = gallery(product);
    const second = photos[1];
    const el = document.createElement("article");
    el.className = "product reveal is-in";
    el.innerHTML = `
      <a class="product__media" href="produto.html?id=${encodeURIComponent(product.id)}">
        <figure>
          <img src="${photos[0] || product.image}?v=18" alt="${esc(product.name)}" loading="lazy" />
          ${second ? `<img class="product__img--alt" src="${second}?v=18" alt="" loading="lazy" />` : ""}
        </figure>
        <span class="product__badge">${esc(product.tag)}</span>
      </a>
      <div class="product__meta">
        <h2><a href="produto.html?id=${encodeURIComponent(product.id)}">${esc(product.name)}</a></h2>
        ${optionPreview(product)}
        <p class="product__price">
          <strong>${brl(product.price)}</strong>
          <small>ou 3× de ${parcel(product.price)}</small>
        </p>
        ${
          (product.options || []).some((group) => !/cor|color/i.test(group.name))
            ? `<a class="btn product__add" href="produto.html?id=${encodeURIComponent(product.id)}"><span>Escolher</span></a>`
            : `<button class="btn product__add" type="button" data-add="${esc(product.id)}"><span>Adicionar</span></button>`
        }
      </div>
    `;
    return el;
  };

  const toast = (text) => {
    let el = document.getElementById("alvaToast");
    if (!el) {
      el = document.createElement("div");
      el.id = "alvaToast";
      el.className = "toast";
      el.setAttribute("role", "status");
      document.body.appendChild(el);
    }
    el.textContent = text;
    el.classList.add("is-on");
    clearTimeout(toast._t);
    toast._t = setTimeout(() => el.classList.remove("is-on"), 2400);
  };

  const mountDrawer = () => {
    if (isAdmin || document.getElementById("cartDrawer")) return;
    const wrap = document.createElement("div");
    wrap.innerHTML = `
      <div class="drawer-veil" id="cartVeil" hidden></div>
      <aside class="drawer" id="cartDrawer" hidden aria-label="Sacola">
        <header class="drawer__head">
          <h2>Sacola</h2>
          <button type="button" class="drawer__close" id="cartClose">Fechar</button>
        </header>
        <div class="drawer__body" id="cartBody"></div>
        <footer class="drawer__foot" id="cartFoot"></footer>
      </aside>
    `;
    document.body.appendChild(wrap);
    document.getElementById("cartClose")?.addEventListener("click", close);
    document.getElementById("cartVeil")?.addEventListener("click", close);
    document.getElementById("cartBody")?.addEventListener("click", (event) => {
      const qty = event.target.closest("[data-line][data-delta]");
      const remove = event.target.closest("[data-remove]");
      if (qty) {
        const key = qty.getAttribute("data-line");
        const current = read().find((item) => lineId(item) === key);
        window.LumeCart.setQty(key, Number(current?.qty || 1) + Number(qty.getAttribute("data-delta")));
      }
      if (remove) window.LumeCart.remove(remove.getAttribute("data-remove"));
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") close();
    });
  };

  const drawDrawer = () => {
    const body = document.getElementById("cartBody");
    const foot = document.getElementById("cartFoot");
    if (!body || !foot) return;
    const lines = read()
      .map((item) => {
        const product = find(item.id);
        if (!product) return null;
        const options = pickOptions(product, item.options);
        return { ...product, qty: item.qty, options, line: lineId({ id: item.id, options }) };
      })
      .filter(Boolean);
    if (!lines.length) {
      body.innerHTML = `<p class="drawer__empty">Sua sacola está vazia.</p>`;
      foot.innerHTML = `<a class="btn" href="loja.html"><span>Ver a loja</span></a>`;
      return;
    }
    const subtotal = lines.reduce((sum, item) => sum + item.price * item.qty, 0);
    body.innerHTML = lines
      .map(
        (item) => `
        <article class="drawer__item">
          <a href="produto.html?id=${encodeURIComponent(item.id)}">
            <img src="${item.image}?v=18" alt="" />
          </a>
          <div>
            <h3><a href="produto.html?id=${encodeURIComponent(item.id)}">${esc(item.name)}</a></h3>
            ${choiceLabel(item.options) ? `<p class="opt-line">${esc(choiceLabel(item.options))}</p>` : ""}
            <p>${brl(item.price)}</p>
            <div class="bag__qty">
              <button type="button" data-line="${esc(item.line)}" data-delta="-1" aria-label="Menos">−</button>
              <span>${item.qty}</span>
              <button type="button" data-line="${esc(item.line)}" data-delta="1" aria-label="Mais">+</button>
              <button type="button" class="bag__remove" data-remove="${esc(item.line)}">Tirar</button>
            </div>
          </div>
          <strong>${brl(item.price * item.qty)}</strong>
        </article>`
      )
      .join("");
    foot.innerHTML = `
      <div class="drawer__total"><span>Subtotal</span><strong>${brl(subtotal)}</strong></div>
      <p class="drawer__hint">Frete R$ 18,90 · grátis acima de R$ 200</p>
      <a class="btn btn--solid" href="checkout.html"><span>Finalizar pedido</span></a>
    `;
  };

  const open = () => {
    if (isAdmin) return;
    mountDrawer();
    drawDrawer();
    const drawer = document.getElementById("cartDrawer");
    const veil = document.getElementById("cartVeil");
    if (drawer) drawer.hidden = false;
    if (veil) veil.hidden = false;
    document.body.classList.add("drawer-open");
  };

  const close = () => {
    const drawer = document.getElementById("cartDrawer");
    const veil = document.getElementById("cartVeil");
    if (drawer) drawer.hidden = true;
    if (veil) veil.hidden = true;
    document.body.classList.remove("drawer-open");
  };

  window.LumeCart = {
    read,
    write,
    count,
    paint,
    catalog,
    brl,
    esc,
    parcel,
    card,
    toast,
    open,
    close,
    find,
    choiceLabel,
    lineId,
    pickOptions,
    colorHex,
    isLightHex,
    isColorGroup,
    ready: loadCatalog,
    add(id, qty = 1, chosen = null) {
      const product = find(id);
      const options = pickOptions(product, chosen);
      const items = read();
      const found = items.find((item) => item.id === id && optionKey(item.options) === optionKey(options));
      if (found) found.qty = Math.min(20, Number(found.qty) + qty);
      else items.push({ id, qty, options });
      write(items);
      const label = choiceLabel(options);
      toast(product ? `${product.name}${label ? " · " + label : ""} na sacola` : "Adicionado à sacola");
      window.AlvaPixel?.track("AddToCart", {
        content_ids: [id],
        content_name: product?.name || id,
        content_type: "product",
        contents: [{ id, quantity: qty }],
        value: Number(product?.price || 0) * qty,
        currency: "BRL",
      });
      open();
    },
    setQty(key, qty) {
      const next = Math.max(0, Math.min(20, Number(qty) || 0));
      const items = read().flatMap((item) => {
        const product = find(item.id);
        const options = pickOptions(product, item.options);
        const current = lineId({ id: item.id, options });
        if (current !== key && lineId(item) !== key) return [item];
        return next ? [{ id: item.id, qty: next, options }] : [];
      });
      write(items);
    },
    remove(key) {
      write(
        read().filter((item) => {
          const options = pickOptions(find(item.id), item.options);
          return lineId({ id: item.id, options }) !== key && lineId(item) !== key;
        })
      );
    },
    clear() {
      write([]);
    },
  };

  paint();
  if (!isAdmin) {
    mountDrawer();
    loadCatalog();
    document.addEventListener("click", (event) => {
      const link = event.target.closest(".cart-link");
      if (!link) return;
      event.preventDefault();
      open();
    });
  }
})();
