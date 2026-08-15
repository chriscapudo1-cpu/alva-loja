(() => {
  const brl = (value) =>
    Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

  const params = new URLSearchParams(location.search);
  const status = params.get("status") || "pending";
  const orderId = params.get("order") || params.get("external_reference") || "";
  const paymentId = params.get("payment_id") || params.get("collection_id") || "";

  const copy = {
    success: ["Pedido pago", "O pagamento entrou. Vamos separar as peças."],
    approved: ["Pedido pago", "O pagamento entrou. Vamos separar as peças."],
    reserved: ["Pedido reservado", "Recebemos o pedido. Para cobrar no Mercado Pago, adicione o token no .env."],
    pending: ["Pagamento em análise", "O Mercado Pago ainda está confirmando. Acompanhe no e-mail."],
    failure: ["Pagamento não concluído", "Nada foi cobrado. Você pode tentar de novo pela loja."],
    rejected: ["Pagamento não concluído", "Nada foi cobrado. Você pode tentar de novo pela loja."],
  };

  const [title, text] = copy[status] || copy.pending;
  const titleEl = document.getElementById("thanksTitle");
  const textEl = document.getElementById("thanksText");
  const box = document.getElementById("thanksBox");
  if (titleEl) titleEl.textContent = title;
  if (textEl) textEl.textContent = text;

  if (status === "success" || status === "approved" || status === "reserved") {
    window.LumeCart?.clear();
  }

  if (orderId) {
    fetch("/api/order/sync", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ orderId, paymentId, status }),
    }).catch(() => {});

    fetch(`/api/order?id=${encodeURIComponent(orderId)}`)
      .then((res) => res.json())
      .then((data) => {
        const order = data.order;
        if (!order) return;
        box.innerHTML = `
          <p>Pedido <strong>${order.id}</strong> · ${order.status.replaceAll("_", " ")}</p>
          <ul>
            ${order.items
              .map((item) => `<li>${item.qty}× ${item.name} — ${brl(item.price * item.qty)}</li>`)
              .join("")}
          </ul>
          <p>Total ${brl(order.total)}</p>
        `;
      })
      .catch(() => {});
  }
})();
