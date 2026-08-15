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
      const product = (data.products || []).find((item) => item.id === id);
      if (!product) {
        root.innerHTML = `<p class="lede">Produto não encontrado. <a href="loja.html">Voltar à loja</a></p>`;
        return;
      }
      document.title = `${product.name} — ALVA`;
      const mainPhoto = product.image || "";
      const descHtml = formatDesc(product.description || product.blurb || "");
      root.innerHTML = `
        <article class="pdp__grid">
          <div class="pdp__media">
            <figure>
              <img id="pdpMain" src="${mainPhoto}?v=8" alt="${product.name}" />
            </figure>
          </div>
          <div>
            <p class="eyebrow">${product.tag}</p>
            <h1 class="display display--case">${product.name}</h1>
            <p class="pdp__price">${brl(product.price)}</p>
            <button class="btn btn--solid" type="button" id="addBtn">
              <span>Colocar na sacola</span>
            </button>
            <p class="check__hint">Envio após a confirmação do pagamento.</p>
            <div class="pdp__copy">
              <h2>Descrição</h2>
              ${descHtml}
            </div>
          </div>
        </article>
      `;
      document.getElementById("addBtn")?.addEventListener("click", () => {
        window.LumeCart.add(product.id, 1);
        document.querySelector("#addBtn span").textContent = "Na sacola";
      });

    })
    .catch(() => {
      root.innerHTML = `<p class="lede">Abra pelo python server.py para ver o produto.</p>`;
    });
})();
