(() => {
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

  window.LumeCart.ready().then((products) => {
    const byTag = new Map();
    products.forEach((item) => {
      if (!byTag.has(item.tag)) byTag.set(item.tag, item);
    });

    if (catsEl) {
      catsEl.innerHTML = "";
      byTag.forEach((item, tag) => {
        const a = document.createElement("a");
        a.className = "home-cat reveal is-in";
        a.href = `loja.html?cat=${encodeURIComponent(tag)}`;
        a.innerHTML = `
          <figure>
            <img src="${item.image}?v=17" alt="" />
          </figure>
          <div>
            <h3>${tag}</h3>
            <p>Ver a categoria</p>
          </div>
        `;
        catsEl.appendChild(a);
      });
    }

    if (featEl) {
      const pick = FEATURED.map((id) => products.find((p) => p.id === id)).filter(Boolean);
      const extra = products.filter((p) => !FEATURED.includes(p.id)).slice(0, 8 - pick.length);
      featEl.innerHTML = "";
      [...pick, ...extra].slice(0, 8).forEach((product) => featEl.appendChild(window.LumeCart.card(product)));
    }
  }).catch(() => {
    if (catsEl) {
      catsEl.innerHTML =
        '<p class="shop__note">Abra pelo servidor (python server.py) para ver as categorias.</p>';
    }
  });

  featEl?.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-add]");
    if (!btn) return;
    window.LumeCart.add(btn.getAttribute("data-add"), 1);
  });
})();
