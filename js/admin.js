(() => {
  const brl = (value) =>
    Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

  const form = document.getElementById("loginForm");
  const board = document.getElementById("board");
  const list = document.getElementById("list");
  const summary = document.getElementById("summary");
  const loginErr = document.getElementById("loginErr");
  const tokenKey = "lume-admin-token";
  let catalog = [];

  const esc = (value) =>
    String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");

  const fold = (value) =>
    String(value || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");

  const paintCatalog = () => {
    const box = document.getElementById("catalog");
    const note = document.getElementById("catalogNote");
    const q = fold(document.getElementById("catalogQ")?.value || "");
    const cat = document.getElementById("catalogCat")?.value || "";
    const ae = document.getElementById("catalogAe");
    if (ae) {
      const term = (document.getElementById("catalogQ")?.value || "").trim() || "dropshipping";
      ae.href = `https://pt.aliexpress.com/w/wholesale-${encodeURIComponent(term)}.html`;
    }
    if (!box) return;
    const list = catalog.filter((item) => {
      if (cat && item.tag !== cat) return false;
      if (!q) return true;
      const hay = fold(
        [item.id, item.name, item.tag, item.search, item.supplier, item.supplierUrl].join(" ")
      );
      return hay.includes(q);
    });
    box.innerHTML = list
      .slice(0, 200)
      .map((item) => {
        const gain = Number(item.price) - Number(item.cost || 0);
        const buy = item.supplierUrl
          ? `<a href="${esc(item.supplierUrl)}" target="_blank" rel="noopener">AliExpress</a>`
          : "—";
        return `<tr>
          <td>${esc(item.name)}</td>
          <td>${esc(item.tag)}</td>
          <td>${brl(item.cost)}</td>
          <td>${brl(item.price)}</td>
          <td>${brl(gain)}</td>
          <td>${buy}</td>
          <td>
            <button class="admin__edit" type="button" data-edit="${esc(item.id)}">editar</button>
            <a href="produto.html?id=${encodeURIComponent(item.id)}">ver</a>
          </td>
        </tr>`;
      })
      .join("");
    if (note) {
      const extra = list.length > 200 ? ` · mostrando 200 de ${list.length}` : "";
      note.textContent = q || cat
        ? `${list.length} resultado(s)${extra}`
        : `${catalog.length} produtos no fornecedor${extra}`;
    }
    if (!list.length) {
      box.innerHTML = `<tr><td colspan="7">Nenhum produto com essa busca.</td></tr>`;
    }
  };

  const when = (iso) => {
    try {
      return new Intl.DateTimeFormat("pt-BR", {
        dateStyle: "short",
        timeStyle: "short",
      }).format(new Date(iso));
    } catch {
      return iso;
    }
  };

  const render = (orders) => {
    const paid = orders.filter((order) => order.status === "pago");
    summary.textContent = `${orders.length} pedido(s) · ${paid.length} pago(s) · ${brl(
      paid.reduce((sum, order) => sum + Number(order.total), 0)
    )} recebidos`;

    fetch("/api/admin/catalog", { headers: { "X-Admin-Token": sessionStorage.getItem("lume-admin-token") || "" } })
      .then((res) => res.json())
      .then((data) => {
        catalog = data.products || [];
        const select = document.getElementById("catalogCat");
        if (select && select.options.length <= 1) {
          [...new Set(catalog.map((item) => item.tag).filter(Boolean))].forEach((tag) => {
            const opt = document.createElement("option");
            opt.value = tag;
            opt.textContent = tag;
            select.appendChild(opt);
          });
        }
        paintCatalog();
        paintProductList();
      })
      .catch(() => {});
    list.innerHTML = orders
      .map((order) => {
        const person = order.customer || {};
        return `
          <article class="ticket">
            <header>
              <p>${when(order.createdAt)} · <strong>${order.id}</strong></p>
              <span class="ticket__status">${order.status.replaceAll("_", " ")}</span>
            </header>
            <p>${esc(person.name || "—")} · ${esc(person.email || "")} · ${esc(person.phone || "")}</p>
            <p>${esc(person.address || "")}${person.number ? ", " + esc(person.number) : ""}${
              person.complement ? " · " + esc(person.complement) : ""
            }${person.neighborhood ? " · " + esc(person.neighborhood) : ""} · ${esc(person.city || "")}${
              person.uf ? "/" + esc(person.uf) : ""
            } · CEP ${esc(person.cep || "")}</p>
            <ul class="order-items">
              ${(order.items || [])
                .map((item) => {
                  const shop = item.id
                    ? `<a class="order-items__link" href="produto.html?id=${encodeURIComponent(item.id)}">ver na loja</a>`
                    : "";
                  const buy = item.supplierUrl
                    ? `<a class="order-items__link" href="${item.supplierUrl}" target="_blank" rel="noopener">comprar no AliExpress</a>`
                    : "";
                  return `<li class="order-items__row">
                    <span>${item.qty}× ${item.name} — ${brl(item.price * item.qty)}</span>
                    <span class="order-items__links">${shop}${buy}</span>
                  </li>`;
                })
                .join("")}
            </ul>
            <p class="ticket__total">Frete ${brl(order.shipping)} · Total ${brl(order.total)}</p>
          </article>
        `;
      })
      .join("");
    if (!orders.length) list.innerHTML = "<p>Ainda não chegou nenhum pedido.</p>";
  };

  const paintPay = (data) => {
    const status = document.getElementById("payStatus");
    if (!status) return;
    if (data.mercadoPago && data.account) {
      const name = data.account.nickname || data.account.email || "conta";
      status.textContent = `Ligado · ${name} · token …${data.tokenTail}`;
    } else if (data.mercadoPago && data.accountError) {
      status.textContent = `Token salvo, mas o Mercado Pago recusou: ${data.accountError}`;
    } else {
      status.textContent = "Ainda desligado. Sem o token, o pedido só entra como reserva.";
    }
    const pixelStatus = document.getElementById("pixelStatus");
    if (pixelStatus) {
      pixelStatus.textContent = data.pixelId
        ? `Ligado · ID ${data.pixelId}`
        : "Ainda sem pixel. Cole o ID para os anúncios do Instagram e do Facebook.";
    }
  };

  const loadPay = async (token) => {
    const res = await fetch("/api/admin/payment", { headers: { "X-Admin-Token": token } });
    if (!res.ok) return;
    paintPay(await res.json());
  };

  const load = async (token) => {
    const res = await fetch("/api/admin/orders", { headers: { "X-Admin-Token": token } });
    if (!res.ok) throw new Error("Sessão inválida.");
    const data = await res.json();
    form.hidden = true;
    board.hidden = false;
    render(data.orders || []);
    await loadPay(token);
    await loadSite(token);
    try {
      const msgRes = await fetch("/api/admin/messages", { headers: { "X-Admin-Token": token } });
      const msgBox = document.getElementById("msgList");
      if (msgRes.ok && msgBox) {
        const payload = await msgRes.json();
        const notes = payload.messages || [];
        msgBox.innerHTML = notes.length
          ? notes
              .map(
                (item) => `<article class="ticket">
                  <header><p>${when(item.createdAt)} · ${esc(item.subject)}</p></header>
                  <p>${esc(item.name)} · <a href="mailto:${esc(item.email)}">${esc(item.email)}</a></p>
                  <p>${esc(item.body)}</p>
                </article>`
              )
              .join("")
          : "<p>Nenhuma mensagem ainda.</p>";
      }
    } catch {
      /* painel de pedidos continua mesmo se o recado falhar */
    }
  };

  document.getElementById("payForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const token = sessionStorage.getItem(tokenKey);
    const payErr = document.getElementById("payErr");
    const payOk = document.getElementById("payOk");
    const input = document.getElementById("accessToken");
    if (payErr) payErr.textContent = "";
    if (payOk) payOk.hidden = true;
    try {
      const res = await fetch("/api/admin/payment", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Admin-Token": token || "",
        },
        body: JSON.stringify({ accessToken: input?.value || "" }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Não salvou.");
      paintPay(data);
      if (input) input.value = "";
      if (payOk) payOk.hidden = false;
    } catch (error) {
      if (payErr) payErr.textContent = error.message;
    }
  });

  sessionStorage.removeItem(tokenKey);
  if (form) form.hidden = false;
  if (board) board.hidden = true;

  document.getElementById("pixelForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const token = sessionStorage.getItem(tokenKey);
    const pixelErr = document.getElementById("pixelErr");
    const pixelOk = document.getElementById("pixelOk");
    const input = document.getElementById("pixelId");
    if (pixelErr) pixelErr.textContent = "";
    if (pixelOk) pixelOk.hidden = true;
    try {
      const res = await fetch("/api/admin/pixel", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Admin-Token": token || "",
        },
        body: JSON.stringify({ pixelId: input?.value || "" }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Não salvou.");
      const pixelStatus = document.getElementById("pixelStatus");
      if (pixelStatus) pixelStatus.textContent = `Ligado · ID ${data.pixelId}`;
      if (input) input.value = "";
      if (pixelOk) pixelOk.hidden = false;
    } catch (error) {
      if (pixelErr) pixelErr.textContent = error.message;
    }
  });

  const SITE_FIELDS = [
    "title",
    "eyebrow",
    "hero1",
    "hero2",
    "hero3",
    "heroLede",
    "promise1Title",
    "promise1Text",
    "promise2Title",
    "promise2Text",
    "promise3Title",
    "promise3Text",
    "promise4Title",
    "promise4Text",
    "catsTitle",
    "catsLede",
    "featTitle",
    "featLede",
    "featCta",
    "footer",
    "contactTitle",
    "contactLede",
    "contactEmail",
  ];

  const fillSite = (site) => {
    const form = document.getElementById("siteForm");
    if (!form || !site) return;
    SITE_FIELDS.forEach((key) => {
      if (form.elements[key]) form.elements[key].value = site[key] || "";
    });
  };

  const loadSite = async (token) => {
    const res = await fetch("/api/admin/site", { headers: { "X-Admin-Token": token } });
    if (!res.ok) return;
    fillSite(await res.json());
  };

  const fillProduct = (item) => {
    if (!item) return;
    const set = (id, value) => {
      const el = document.getElementById(id);
      if (el) el.value = value ?? "";
    };
    set("prodId", item.id);
    set("prodName", item.name);
    set("prodTag", item.tag || "");
    set("prodPrice", item.price);
    set("prodCost", item.cost);
    set("prodStock", item.stock);
    set("prodBlurb", item.blurb || "");
    set("prodDesc", item.description || "");
    const view = document.getElementById("prodView");
    if (view) view.href = `produto.html?id=${encodeURIComponent(item.id)}`;
  };

  const paintProductList = () => {
    const listEl = document.getElementById("prodList");
    if (!listEl) return;
    listEl.innerHTML = catalog
      .map((item) => `<option value="${esc(item.id)}">${esc(item.name)} · ${esc(item.tag)}</option>`)
      .join("");
  };

  document.querySelector(".admin__tabs")?.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-panel]");
    if (!btn) return;
    const name = btn.getAttribute("data-panel");
    document.querySelectorAll(".admin__tab").forEach((tab) => {
      tab.classList.toggle("is-on", tab === btn);
    });
    document.querySelectorAll(".admin__panel").forEach((panel) => {
      panel.hidden = panel.getAttribute("data-panel") !== name;
    });
  });

  document.getElementById("siteForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const token = sessionStorage.getItem(tokenKey);
    const err = document.getElementById("siteErr");
    const ok = document.getElementById("siteOk");
    if (err) err.textContent = "";
    if (ok) ok.hidden = true;
    const form = event.currentTarget;
    const payload = {};
    SITE_FIELDS.forEach((key) => {
      payload[key] = form.elements[key]?.value || "";
    });
    try {
      const res = await fetch("/api/admin/site", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Admin-Token": token || "",
        },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Não salvou.");
      fillSite(data.site);
      if (ok) ok.hidden = false;
    } catch (error) {
      if (err) err.textContent = error.message;
    }
  });

  document.getElementById("catalog")?.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-edit]");
    if (!btn) return;
    const item = catalog.find((entry) => entry.id === btn.getAttribute("data-edit"));
    if (!item) return;
    fillProduct(item);
    const pick = document.getElementById("prodPick");
    if (pick) pick.value = item.id;
    document.querySelector('.admin__tab[data-panel="site"]')?.click();
    document.getElementById("productForm")?.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  document.getElementById("prodPick")?.addEventListener("change", () => {
    const value = document.getElementById("prodPick")?.value || "";
    const item =
      catalog.find((entry) => entry.id === value) ||
      catalog.find((entry) => fold(entry.name) === fold(value)) ||
      catalog.find((entry) => fold(entry.name).includes(fold(value)));
    if (item) fillProduct(item);
  });

  document.getElementById("productForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const token = sessionStorage.getItem(tokenKey);
    const err = document.getElementById("prodErr");
    const ok = document.getElementById("prodOk");
    if (err) err.textContent = "";
    if (ok) ok.hidden = true;
    const form = event.currentTarget;
    try {
      const res = await fetch("/api/admin/product", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Admin-Token": token || "",
        },
        body: JSON.stringify({
          id: form.elements.id.value,
          name: form.elements.name.value,
          price: form.elements.price.value,
          cost: form.elements.cost.value,
          stock: form.elements.stock.value,
          blurb: form.elements.blurb.value,
          description: form.elements.description.value,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Não salvou.");
      const index = catalog.findIndex((item) => item.id === data.product.id);
      if (index >= 0) catalog[index] = { ...catalog[index], ...data.product };
      fillProduct(data.product);
      paintCatalog();
      if (ok) ok.hidden = false;
    } catch (error) {
      if (err) err.textContent = error.message;
    }
  });

  document.getElementById("catalogQ")?.addEventListener("input", paintCatalog);
  document.getElementById("catalogCat")?.addEventListener("change", paintCatalog);

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    loginErr.textContent = "";
    try {
      const res = await fetch("/api/admin/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: form.password.value }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Não entrou.");
      sessionStorage.setItem(tokenKey, data.token);
      await load(data.token);
    } catch (error) {
      loginErr.textContent = error.message;
    }
  });
})();
