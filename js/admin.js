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
          <td><a href="produto.html?id=${encodeURIComponent(item.id)}">ver na loja</a></td>
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
