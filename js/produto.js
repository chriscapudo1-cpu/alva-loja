(() => {
  const brl = (value) =>
    Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

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
      root.innerHTML = `
        <article class="pdp__grid">
          <figure>
            <img src="${product.image}?v=2" alt="${product.name}" />
          </figure>
          <div>
            <p class="eyebrow">${product.tag}</p>
            <h1 class="display display--case">${product.name}</h1>
            <p class="lede">${product.blurb}</p>
            <p class="pdp__price">${brl(product.price)}</p>
            <button class="btn btn--solid" type="button" id="addBtn">
              <span>Colocar na sacola</span>
            </button>
            <p class="check__hint">Envio após a confirmação do pagamento.</p>
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
