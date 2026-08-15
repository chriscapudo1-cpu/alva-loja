(() => {
  const brl = (value) =>
    Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

  const catsEl = document.getElementById("homeCats");
  const featEl = document.getElementById("homeFeat");
  if (!catsEl && !featEl) return;

  const FEATURED = [
    "tech-001",
    "casa-021",
    "pet-041",
    "moda-061",
    "carro-083",
    "beleza-105",
    "esporte-121",
    "tech-005",
  ];

  const card = (product) => {
    const el = document.createElement("article");
    el.className = "product reveal is-in";
    el.innerHTML = `
      <a class="product__media" href="produto.html?id=${encodeURIComponent(product.id)}">
        <figure>
          <img src="${product.image}?v=7" alt="${product.name}" loading="lazy" />
        </figure>
      </a>
      <div class="product__meta">
        <span>${product.tag}</span>
        <h2><a href="produto.html?id=${encodeURIComponent(product.id)}">${product.name}</a></h2>
        <div class="product__row">
          <strong>${brl(product.price)}</strong>
          <button class="btn product__add" type="button" data-add="${product.id}">
            <span>Sacola</span>
          </button>
        </div>
      </div>
    `;
    return el;
  };

  fetch("/api/products")
    .then((res) => res.json())
    .then((data) => {
      const products = data.products || [];
      const byTag = new Map();
      products.forEach((item) => {
        if (!byTag.has(item.tag)) byTag.set(item.tag, item);
      });

      if (catsEl) {
        catsEl.innerHTML = "";
        byTag.forEach((item, tag) => {
          const count = products.filter((p) => p.tag === tag).length;
          const a = document.createElement("a");
          a.className = "home-cat reveal is-in";
          a.href = `loja.html?cat=${encodeURIComponent(tag)}`;
          a.innerHTML = `
            <figure>
              <img src="${item.image}?v=7" alt="" />
            </figure>
            <div>
              <h3>${tag}</h3>
              <p>${count} produtos</p>
            </div>
          `;
          catsEl.appendChild(a);
        });
      }

      if (featEl) {
        const pick = FEATURED.map((id) => products.find((p) => p.id === id)).filter(Boolean);
        const extra = products.filter((p) => !FEATURED.includes(p.id)).slice(0, 8 - pick.length);
        featEl.innerHTML = "";
        [...pick, ...extra].slice(0, 8).forEach((product) => featEl.appendChild(card(product)));
      }
    })
    .catch(() => {
      if (catsEl) {
        catsEl.innerHTML =
          '<p class="shop__note">Abra pelo servidor (python server.py) para ver as categorias.</p>';
      }
    });

  featEl?.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-add]");
    if (!btn) return;
    window.LumeCart.add(btn.getAttribute("data-add"), 1);
    const span = btn.querySelector("span");
    if (span) span.textContent = "Na sacola";
    window.setTimeout(() => {
      if (span) span.textContent = "Colocar na sacola";
    }, 1400);
  });
})();
