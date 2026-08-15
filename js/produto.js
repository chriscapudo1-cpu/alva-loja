(() => {
  const formatDesc = (raw, esc) => {
    const blocks = String(raw || "")
      .split(/\n\n+/)
      .map((block) => block.trim())
      .filter(Boolean);
    if (!blocks.length) return "<p></p>";
    return blocks
      .map((block) => {
        const lines = block.split("\n").map((line) => line.trim()).filter(Boolean);
        const bullets = lines.filter((line) => /^[-•]/.test(line));
        if (bullets.length && bullets.length === lines.length - 1) {
          const heading = esc(lines[0]);
          const items = bullets
            .map((line) => `<li>${esc(line.replace(/^[-•]\s*/, ""))}</li>`)
            .join("");
          return `<h3>${heading}</h3><ul>${items}</ul>`;
        }
        return `<p>${lines.map(esc).join("<br />")}</p>`;
      })
      .join("");
  };

  const root = document.querySelector(".pdp");
  const id = new URLSearchParams(location.search).get("id");

  window.LumeCart.ready()
    .then((products) => {
      const product = products.find((item) => item.id === id);
      if (!product) {
        root.innerHTML = `<p class="lede">Produto não encontrado. <a href="loja.html">Voltar à loja</a></p>`;
        return;
      }
      const { brl, esc, parcel, card } = window.LumeCart;
      document.title = `${product.name} — ALVA`;
      const desc = document.querySelector('meta[name="description"]');
      if (desc) desc.setAttribute("content", `${product.name} na ALVA. ${brl(product.price)}.`);
      const mainPhoto = product.image || "";
      const descHtml = formatDesc(product.description || product.blurb || "", esc);
      const stock = Number(product.stock || 0);
      const related = products
        .filter((item) => item.tag === product.tag && item.id !== product.id)
        .slice(0, 4);
      root.innerHTML = `
        <p class="pdp__back"><a href="loja.html?cat=${encodeURIComponent(product.tag)}">← ${esc(product.tag)}</a></p>
        <article class="pdp__grid">
          <div class="pdp__media">
            <figure class="pdp__plate">
              <img id="pdpMain" src="${mainPhoto}?v=10" alt="${esc(product.name)}" />
            </figure>
          </div>
          <div class="pdp__info">
            <p class="eyebrow">${esc(product.tag)}</p>
            <h1 class="display display--case">${esc(product.name)}</h1>
            <p class="pdp__price">${brl(product.price)}</p>
            <p class="pdp__install">${stock > 0 ? `ou 3× de ${parcel(product.price)} no cartão` : "Indisponível no momento"}</p>
            <ul class="pdp__trust">
              <li>Pix e cartão no Mercado Pago</li>
              <li>Frete R$ 18,90 · grátis acima de R$ 200</li>
              <li>Envio depois do pagamento confirmado</li>
            </ul>
            <div class="pdp__buy">
              <div class="pdp__qty" role="group" aria-label="Quantidade">
                <button type="button" id="qtyMinus" aria-label="Menos">−</button>
                <input id="qtyInput" type="text" inputmode="numeric" value="1" aria-label="Quantidade" />
                <button type="button" id="qtyPlus" aria-label="Mais">+</button>
              </div>
              <button class="btn btn--solid" type="button" id="addBtn" ${stock < 1 ? "disabled" : ""}>
                <span>Adicionar à sacola</span>
              </button>
            </div>
            <p class="pdp__links">
              <a href="envio.html">Prazo e frete</a>
              <a href="trocas.html">Trocas</a>
            </p>
            <div class="pdp__copy">
              <h2>Descrição</h2>
              ${descHtml}
            </div>
          </div>
        </article>
        ${
          related.length
            ? `<section class="pdp__also">
                <h2>Mais em ${esc(product.tag)}</h2>
                <div class="shop__grid pdp__also-grid" id="pdpAlso"></div>
              </section>`
            : ""
        }
        <div class="pdp__sticky" id="pdpSticky">
          <div>
            <strong>${esc(product.name)}</strong>
            <span>${brl(product.price)}</span>
          </div>
          <button class="btn btn--solid" type="button" id="stickyAdd" ${stock < 1 ? "disabled" : ""}>
            <span>Adicionar</span>
          </button>
        </div>
      `;

      const also = document.getElementById("pdpAlso");
      related.forEach((item) => also?.appendChild(card(item)));
      also?.addEventListener("click", (event) => {
        const btn = event.target.closest("[data-add]");
        if (!btn) return;
        window.LumeCart.add(btn.getAttribute("data-add"), 1);
      });

      const qtyInput = document.getElementById("qtyInput");
      const clampQty = (value) => Math.max(1, Math.min(20, Number(value) || 1));
      const setQty = (value) => {
        if (qtyInput) qtyInput.value = String(clampQty(value));
      };
      const add = () => {
        window.LumeCart.add(product.id, clampQty(qtyInput?.value));
        document.querySelectorAll("#addBtn span, #stickyAdd span").forEach((span) => {
          span.textContent = "Na sacola";
        });
      };
      document.getElementById("qtyMinus")?.addEventListener("click", () => setQty(Number(qtyInput.value) - 1));
      document.getElementById("qtyPlus")?.addEventListener("click", () => setQty(Number(qtyInput.value) + 1));
      qtyInput?.addEventListener("change", () => setQty(qtyInput.value));
      document.getElementById("addBtn")?.addEventListener("click", add);
      document.getElementById("stickyAdd")?.addEventListener("click", add);
    })
    .catch(() => {
      root.innerHTML = `<p class="lede">Abra pelo python server.py para ver o produto.</p>`;
    });
})();
