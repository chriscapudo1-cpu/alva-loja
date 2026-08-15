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
      const gallery = [product.image].filter(Boolean);
      const thumbs = gallery
        .map(
          (src, index) =>
            `<button class="pdp__thumb${index === 0 ? " is-on" : ""}" type="button" data-src="${src}" aria-label="Foto ${index + 1}">
              <img src="${src}?v=7" alt="" />
            </button>`
        )
        .join("");
      root.innerHTML = `
        <article class="pdp__grid">
          <div class="pdp__media">
            <figure>
              <img id="pdpMain" src="${gallery[0]}?v=7" alt="${product.name}" />
            </figure>
            ${gallery.length > 1 ? `<div class="pdp__thumbs">${thumbs}</div>` : ""}
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
              <p>${product.description || product.blurb || ""}</p>
            </div>
          </div>
        </article>
      `;
      document.getElementById("addBtn")?.addEventListener("click", () => {
        window.LumeCart.add(product.id, 1);
        document.querySelector("#addBtn span").textContent = "Na sacola";
      });
      const main = document.getElementById("pdpMain");
      root.querySelectorAll(".pdp__thumb").forEach((btn) => {
        btn.addEventListener("click", () => {
          const src = btn.getAttribute("data-src");
          if (main && src) main.src = `${src}?v=7`;
          root.querySelectorAll(".pdp__thumb").forEach((el) => el.classList.toggle("is-on", el === btn));
        });
      });
    })
    .catch(() => {
      root.innerHTML = `<p class="lede">Abra pelo python server.py para ver o produto.</p>`;
    });
})();
