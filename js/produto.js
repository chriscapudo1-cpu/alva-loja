(() => {
  const brl = (value) =>
    Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

  const esc = (value) =>
    String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");

  const formatDesc = (raw) => {
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

  fetch("/api/products")
    .then((res) => res.json())
    .then((data) => {
      const products = data.products || [];
      const product = products.find((item) => item.id === id);
      if (!product) {
        root.innerHTML = `<p class="lede">Produto não encontrado. <a href="loja.html">Voltar à loja</a></p>`;
        return;
      }
      document.title = `${product.name} — ALVA`;
      const mainPhoto = product.image || "";
      const descHtml = formatDesc(product.description || product.blurb || "");
      const stock = Number(product.stock || 0);
      const related = products
        .filter((item) => item.tag === product.tag && item.id !== product.id)
        .slice(0, 4);
      root.innerHTML = `
        <p class="pdp__back"><a href="loja.html?cat=${encodeURIComponent(product.tag)}">← ${esc(product.tag)}</a></p>
        <article class="pdp__grid">
          <div class="pdp__media">
            <figure>
              <img id="pdpMain" src="${mainPhoto}?v=8" alt="${esc(product.name)}" />
            </figure>
          </div>
          <div>
            <p class="eyebrow">${esc(product.tag)}</p>
            <h1 class="display display--case">${esc(product.name)}</h1>
            <p class="pdp__price">${brl(product.price)}</p>
            <p class="pdp__stock">${stock > 0 ? "Em estoque · envio após o pagamento" : "Indisponível no momento"}</p>
            <div class="pdp__buy">
              <div class="pdp__qty" role="group" aria-label="Quantidade">
                <button type="button" id="qtyMinus" aria-label="Menos">−</button>
                <input id="qtyInput" type="text" inputmode="numeric" value="1" aria-label="Quantidade" />
                <button type="button" id="qtyPlus" aria-label="Mais">+</button>
              </div>
              <button class="btn btn--solid" type="button" id="addBtn" ${stock < 1 ? "disabled" : ""}>
                <span>Colocar na sacola</span>
              </button>
            </div>
            <p class="check__hint">Frete R$ 18,90 · grátis acima de R$ 200.</p>
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
                <div class="shop__grid pdp__also-grid">
                  ${related
                    .map(
                      (item) => `
                    <article class="product">
                      <a class="product__media" href="produto.html?id=${encodeURIComponent(item.id)}">
                        <figure><img src="${item.image}?v=8" alt="${esc(item.name)}" loading="lazy" /></figure>
                      </a>
                      <div class="product__meta">
                        <h2><a href="produto.html?id=${encodeURIComponent(item.id)}">${esc(item.name)}</a></h2>
                        <div class="product__row">
                          <strong>${brl(item.price)}</strong>
                        </div>
                      </div>
                    </article>`
                    )
                    .join("")}
                </div>
              </section>`
            : ""
        }
      `;

      const qtyInput = document.getElementById("qtyInput");
      const clampQty = (value) => Math.max(1, Math.min(20, Number(value) || 1));
      const setQty = (value) => {
        if (qtyInput) qtyInput.value = String(clampQty(value));
      };
      document.getElementById("qtyMinus")?.addEventListener("click", () => setQty(Number(qtyInput.value) - 1));
      document.getElementById("qtyPlus")?.addEventListener("click", () => setQty(Number(qtyInput.value) + 1));
      qtyInput?.addEventListener("change", () => setQty(qtyInput.value));

      document.getElementById("addBtn")?.addEventListener("click", () => {
        window.LumeCart.add(product.id, clampQty(qtyInput?.value));
        const span = document.querySelector("#addBtn span");
        if (span) span.textContent = "Na sacola";
      });
    })
    .catch(() => {
      root.innerHTML = `<p class="lede">Abra pelo python server.py para ver o produto.</p>`;
    });
})();
