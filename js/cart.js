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
        document.dispatchEvent(new CustomEvent("alva:catalog", { detail: catalog }));
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
          <img src="${photos[0] || product.image}?v=16" alt="${esc(product.name)}" loading="lazy" />
          ${second ? `<img class="product__img--alt" src="${second}?v=16" alt="" loading="lazy" />` : ""}
        </figure>
        <span class="product__badge">${esc(product.tag)}</span>
      </a>
      <div class="product__meta">
        <h2><a href="produto.html?id=${encodeURIComponent(product.id)}">${esc(product.name)}</a></h2>
        <p class="product__price">
          <strong>${brl(product.price)}</strong>
          <small>ou 3× de ${parcel(product.price)}</small>
        </p>
        <button class="btn product__add" type="button" data-add="${esc(product.id)}">
          <span>Adicionar</span>
        </button>
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
      const qty = event.target.closest("[data-qty]");
      const remove = event.target.closest("[data-remove]");
      if (qty) {
        const id = qty.getAttribute("data-qty");
        const current = read().find((item) => item.id === id);
        window.LumeCart.setQty(id, Number(current?.qty || 1) + Number(qty.getAttribute("data-delta")));
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
        return product ? { ...product, qty: item.qty } : null;
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
            <img src="${item.image}?v=16" alt="" />
          </a>
          <div>
            <h3><a href="produto.html?id=${encodeURIComponent(item.id)}">${esc(item.name)}</a></h3>
            <p>${brl(item.price)}</p>
            <div class="bag__qty">
              <button type="button" data-qty="${item.id}" data-delta="-1" aria-label="Menos">−</button>
              <span>${item.qty}</span>
              <button type="button" data-qty="${item.id}" data-delta="1" aria-label="Mais">+</button>
              <button type="button" class="bag__remove" data-remove="${item.id}">Tirar</button>
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
    ready: loadCatalog,
    add(id, qty = 1) {
      const items = read();
      const found = items.find((item) => item.id === id);
      if (found) found.qty = Math.min(20, Number(found.qty) + qty);
      else items.push({ id, qty });
      write(items);
      const product = find(id);
      toast(product ? `${product.name} na sacola` : "Adicionado à sacola");
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
    setQty(id, qty) {
      const next = Math.max(0, Math.min(20, Number(qty) || 0));
      const items = read().flatMap((item) => {
        if (item.id !== id) return [item];
        return next ? [{ id, qty: next }] : [];
      });
      write(items);
    },
    remove(id) {
      write(read().filter((item) => item.id !== id));
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
