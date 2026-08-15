(() => {
  const brl = (value) =>
    Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

  const form = document.getElementById("loginForm");
  const board = document.getElementById("board");
  const list = document.getElementById("list");
  const summary = document.getElementById("summary");
  const loginErr = document.getElementById("loginErr");
  const tokenKey = "lume-admin-token";

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
        const box = document.getElementById("catalog");
        if (!box || !data.products) return;
        box.innerHTML = data.products
          .map((item) => {
            const gain = Number(item.price) - Number(item.cost || 0);
            return `<tr>
              <td>${item.name}</td>
              <td>${brl(item.cost)}</td>
              <td>${brl(item.price)}</td>
              <td>${brl(gain)}</td>
              <td><a href="${item.supplierUrl}" target="_blank" rel="noopener">AliExpress</a></td>
              <td><a href="produto.html?id=${item.id}">ver na loja</a></td>
            </tr>`;
          })
          .join("");
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
            <p>${person.name || "—"} · ${person.email || ""} · ${person.phone || ""}</p>
            <p>${person.address || ""}, ${person.city || ""} · CEP ${person.cep || ""}</p>
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
