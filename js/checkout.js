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
  const SAVE = "alva-buyer";

  let products = [];
  let mercadoPago = false;
  let freeFrom = 200;
  let shipPrice = 18.9;
  const shippingOf = (subtotal) => (subtotal >= freeFrom ? 0 : shipPrice);

  const digits = (value) => String(value || "").replace(/\D/g, "");

  const maskCep = (value) => {
    const d = digits(value).slice(0, 8);
    return d.length > 5 ? `${d.slice(0, 5)}-${d.slice(5)}` : d;
  };

  const maskPhone = (value) => {
    const d = digits(value).slice(0, 11);
    if (d.length <= 2) return d;
    if (d.length <= 6) return `(${d.slice(0, 2)}) ${d.slice(2)}`;
    if (d.length <= 10) return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`;
    return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`;
  };

  const maskCpf = (value) => {
    const d = digits(value).slice(0, 11);
    if (d.length <= 3) return d;
    if (d.length <= 6) return `${d.slice(0, 3)}.${d.slice(3)}`;
    if (d.length <= 9) return `${d.slice(0, 3)}.${d.slice(3, 6)}.${d.slice(6)}`;
    return `${d.slice(0, 3)}.${d.slice(3, 6)}.${d.slice(6, 9)}-${d.slice(9)}`;
  };

  const field = (name) => form?.elements.namedItem(name);

  const saveBuyer = () => {
    if (!form) return;
    const data = Object.fromEntries(new FormData(form).entries());
    try {
      localStorage.setItem(SAVE, JSON.stringify(data));
    } catch {
      /* ignore */
    }
  };

  const restoreBuyer = () => {
    if (!form) return;
    try {
      const data = JSON.parse(localStorage.getItem(SAVE) || "{}");
      Object.entries(data).forEach(([key, value]) => {
        const el = field(key);
        if (el && "value" in el) el.value = value;
      });
    } catch {
      /* ignore */
    }
  };

  const fillCep = async (cep) => {
    const raw = digits(cep);
    if (raw.length !== 8) return;
    try {
      const res = await fetch(`https://viacep.com.br/ws/${raw}/json/`);
      const data = await res.json();
      if (data.erro) return;
      const street = field("address");
      const hood = field("neighborhood");
      const city = field("city");
      const uf = field("uf");
      if (street && !street.value) street.value = data.logradouro || "";
      if (hood) hood.value = data.bairro || hood.value;
      if (city) city.value = data.localidade || city.value;
      if (uf) uf.value = data.uf || uf.value;
      field("number")?.focus();
      saveBuyer();
    } catch {
      /* ViaCEP offline: o cliente preenche na mão */
    }
  };

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
          <a href="produto.html?id=${encodeURIComponent(item.id)}"><img src="${item.image}?v=8" alt="" /></a>
          <div>
            <h3><a href="produto.html?id=${encodeURIComponent(item.id)}">${item.name}</a></h3>
            <p>${brl(item.price)}</p>
            <div class="bag__qty">
              <button type="button" data-qty="${item.id}" data-delta="-1" aria-label="Menos">−</button>
              <span>${item.qty}</span>
              <button type="button" data-qty="${item.id}" data-delta="1" aria-label="Mais">+</button>
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
      : "Grátis";
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

  form?.addEventListener("input", (event) => {
    const el = event.target;
    if (!(el instanceof HTMLInputElement)) return;
    if (el.name === "cep") el.value = maskCep(el.value);
    if (el.name === "phone") el.value = maskPhone(el.value);
    if (el.name === "cpf") el.value = maskCpf(el.value);
    if (el.name === "uf") el.value = el.value.toUpperCase().replace(/[^A-Z]/g, "").slice(0, 2);
    saveBuyer();
  });

  field("cep")?.addEventListener("blur", () => fillCep(field("cep")?.value || ""));

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
          "Pagamento ainda não ligado. Entre no painel e cole o Access Token do Mercado Pago.";
        btn.querySelector("span").textContent = "Reservar pedido";
      }
      restoreBuyer();
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
    const customer = {
      name: String(data.get("name") || "").trim(),
      email: String(data.get("email") || "").trim(),
      phone: String(data.get("phone") || "").trim(),
      cpf: String(data.get("cpf") || "").trim(),
      cep: String(data.get("cep") || "").trim(),
      address: String(data.get("address") || "").trim(),
      number: String(data.get("number") || "").trim(),
      complement: String(data.get("complement") || "").trim(),
      neighborhood: String(data.get("neighborhood") || "").trim(),
      city: String(data.get("city") || "").trim(),
      uf: String(data.get("uf") || "").trim().toUpperCase(),
    };
    if (!customer.name || !customer.email.includes("@") || digits(customer.phone).length < 10) {
      err.textContent = "Preencha nome, e-mail e um telefone válido.";
      return;
    }
    if (digits(customer.cep).length !== 8 || !customer.address || !customer.number || !customer.city) {
      err.textContent = "Preencha CEP, rua, número e cidade.";
      return;
    }
    if (customer.uf && customer.uf.length !== 2) {
      err.textContent = "UF com 2 letras, por exemplo SP.";
      return;
    }
    if (customer.cpf && digits(customer.cpf).length !== 11) {
      err.textContent = "CPF incompleto. Pode deixar em branco se preferir.";
      return;
    }
    saveBuyer();
    btn.disabled = true;
    try {
      const res = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items, customer }),
      });
      const payload = await res.json();
      if (!res.ok) throw new Error(payload.error || "Não foi possível criar o pedido.");
      window.location.href = payload.checkoutUrl;
    } catch (error) {
      err.textContent = error.message;
      btn.disabled = false;
    }
  });
})();
