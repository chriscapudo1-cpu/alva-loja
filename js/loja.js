(() => {
  const brl = (value) =>
    Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

  const grid = document.getElementById("shopGrid");
  const note = document.getElementById("shopNote");
  const chips = document.getElementById("catChips");
  const heading = document.getElementById("shopHeading");
  const lede = document.getElementById("shopLede");
  const params = new URLSearchParams(location.search);
  let current = params.get("cat") || "";
  let all = [];

  const card = (product) => {
    const el = document.createElement("article");
    el.className = "product reveal is-in";
    el.id = product.id;
    el.innerHTML = `
      <a class="product__media" href="produto.html?id=${encodeURIComponent(product.id)}">
        <figure>
          <img src="${product.image}?v=2" alt="${product.name}" loading="lazy" />
        </figure>
      </a>
      <div class="product__meta">
        <span>${product.tag}</span>
        <h2><a href="produto.html?id=${encodeURIComponent(product.id)}">${product.name}</a></h2>
        <p>${product.blurb}</p>
        <div class="product__row">
          <strong>${brl(product.price)}</strong>
          <button class="btn" type="button" data-add="${product.id}">
            <span>Colocar na sacola</span>
          </button>
        </div>
      </div>
    `;
    return el;
  };

  const paintChips = (categories) => {
    if (!chips) return;
    const items = ["Todas", ...categories];
    chips.innerHTML = items
      .map((name) => {
        const value = name === "Todas" ? "" : name;
        const on = current === value ? " is-on" : "";
        return `<button class="chip${on}" type="button" data-cat="${value}">${name}</button>`;
      })
      .join("");
  };

  const paint = () => {
    const list = current ? all.filter((item) => item.tag === current) : all;
    if (heading) heading.textContent = current || "Todas as categorias";
    if (lede) lede.textContent = `${list.length} produtos · envio após o pagamento`;
    if (grid) {
      grid.innerHTML = "";
      list.forEach((product) => grid.appendChild(card(product)));
    }
    chips?.querySelectorAll("[data-cat]").forEach((btn) => {
      btn.classList.toggle("is-on", btn.getAttribute("data-cat") === current);
    });
  };

  chips?.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-cat]");
    if (!btn) return;
    current = btn.getAttribute("data-cat") || "";
    const url = new URL(location.href);
    if (current) url.searchParams.set("cat", current);
    else url.searchParams.delete("cat");
    history.replaceState({}, "", url);
    paint();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  grid?.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-add]");
    if (!btn) return;
    window.LumeCart.add(btn.getAttribute("data-add"), 1);
    btn.querySelector("span").textContent = "Na sacola";
    window.setTimeout(() => {
      if (btn.querySelector("span")) btn.querySelector("span").textContent = "Colocar na sacola";
    }, 1400);
  });

  Promise.all([
    fetch("/api/products").then((res) => res.json()),
    fetch("/api/categories").then((res) => res.json()),
  ])
    .then(([catalog, cats]) => {
      all = catalog.products || [];
      paintChips(cats.categories || []);
      paint();
    })
    .catch(() => {
      if (note) {
        note.hidden = false;
        note.textContent = "Abra o site pelo servidor (python server.py) para carregar os 200 produtos.";
      }
    });
})();
