(() => {
  const brl = (value) =>
    Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

  const empty = document.getElementById("empty");
  const layout = document.getElementById("checkLayout");
  const bag = document.getElementById("bag");
  const totals = document.getElementById("totals");
  const form = document.getElementById("payForm");
  const hint = document.getElementById("payHint");
  const err = document.getElementById("payErr");
  const btn = document.getElementById("payBtn");

  let products = [];
  let mercadoPago = false;

  let freeFrom = 200;
  let shipPrice = 18.9;
  const shippingOf = (subtotal) => (subtotal >= freeFrom ? 0 : shipPrice);

  const lines = () => {
    const cart = window.LumeCart.read();
    return cart
      .map((item) => {
        const product = products.find((p) => p.id === item.id);
        return product ? { ...product, qty: item.qty } : null;
      })
      .filter(Boolean);
  };

  const draw = () => {
    const items = lines();
    if (!items.length) {
      empty.hidden = false;
      layout.hidden = true;
      return;
    }
    empty.hidden = true;
    layout.hidden = false;
    bag.innerHTML = items
      .map(
        (item) => `
        <li class="bag__item">
          <img src="${item.image}" alt="" />
          <div>
            <h3>${item.name}</h3>
            <p>${brl(item.price)}</p>
            <div class="bag__qty">
              <button type="button" data-qty="${item.id}" data-delta="-1">−</button>
              <span>${item.qty}</span>
              <button type="button" data-qty="${item.id}" data-delta="1">+</button>
              <button type="button" class="bag__remove" data-remove="${item.id}">Tirar</button>
            </div>
          </div>
          <strong>${brl(item.price * item.qty)}</strong>
        </li>`
      )
      .join("");
    const subtotal = items.reduce((sum, item) => sum + item.price * item.qty, 0);
    const shipping = shippingOf(subtotal);
    const lack = Math.max(0, freeFrom - subtotal);
    const freightLabel = shipping
      ? `${brl(shipping)} · faltam ${brl(lack)} para frete grátis`
      : "Grátis a partir de R$ 200";
    totals.innerHTML = `
      <div><dt>Subtotal</dt><dd>${brl(subtotal)}</dd></div>
      <div><dt>Frete</dt><dd>${freightLabel}</dd></div>
      <div class="totals__sum"><dt>Total</dt><dd>${brl(subtotal + shipping)}</dd></div>
    `;
  };

  bag?.addEventListener("click", (event) => {
    const qtyBtn = event.target.closest("[data-qty]");
    const removeBtn = event.target.closest("[data-remove]");
    if (qtyBtn) {
      const id = qtyBtn.getAttribute("data-qty");
      const current = window.LumeCart.read().find((item) => item.id === id);
      window.LumeCart.setQty(id, Number(current?.qty || 1) + Number(qtyBtn.getAttribute("data-delta")));
      draw();
    }
    if (removeBtn) {
      window.LumeCart.remove(removeBtn.getAttribute("data-remove"));
      draw();
    }
  });

  Promise.all([
    fetch("/api/products").then((res) => res.json()),
    fetch("/api/config").then((res) => res.json()),
  ])
    .then(([catalog, config]) => {
      products = catalog.products || [];
      mercadoPago = Boolean(config.mercadoPago);
      if (Number(config.freeFrom)) freeFrom = Number(config.freeFrom);
      if (Number(config.shipPrice)) shipPrice = Number(config.shipPrice);
      if (!mercadoPago && hint && btn) {
        hint.textContent =
          "Pagamento ainda não ligado. Entre no painel (admin.html) e cole o Access Token do Mercado Pago.";
        btn.querySelector("span").textContent = "Reservar pedido";
      }
      draw();
    })
    .catch(() => {
      if (hint) hint.textContent = "Abra pelo python server.py para finalizar o pedido.";
      empty.hidden = false;
    });

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    err.textContent = "";
    const items = window.LumeCart.read();
    if (!items.length) return;
    const data = new FormData(form);
    btn.disabled = true;
    try {
      const res = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          items,
          customer: {
            name: data.get("name"),
            email: data.get("email"),
            phone: data.get("phone"),
            cep: data.get("cep"),
            address: data.get("address"),
            city: data.get("city"),
          },
        }),
      });
      const payload = await res.json();
      if (!res.ok) throw new Error(payload.error || "Não foi possível criar o pedido.");
      window.LumeCart.clear();
      window.location.href = payload.checkoutUrl;
    } catch (error) {
      err.textContent = error.message;
      btn.disabled = false;
    }
  });
})();
