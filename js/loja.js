(() => {
  const brl = (value) =>
    Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

  const fold = (value) =>
    String(value || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");

  const grid = document.getElementById("shopGrid");
  const note = document.getElementById("shopNote");
  const chips = document.getElementById("catChips");
  const heading = document.getElementById("shopHeading");
  const lede = document.getElementById("shopLede");
  const empty = document.getElementById("shopEmpty");
  const sortEl = document.getElementById("shopSort");
  const params = new URLSearchParams(location.search);
  const PAGE = 48;
  let current = params.get("cat") || "";
  let query = (params.get("q") || "").trim();
  let sort = params.get("sort") || "nome";
  let all = [];
  let shown = PAGE;
  const searchInput = document.getElementById("shopQ");
  if (searchInput && query) searchInput.value = query;
  if (sortEl) sortEl.value = sort;

  const card = (product) => {
    const el = document.createElement("article");
    el.className = "product reveal is-in";
    el.id = product.id;
    el.innerHTML = `
      <a class="product__media" href="produto.html?id=${encodeURIComponent(product.id)}">
        <figure>
          <img src="${product.image}?v=8" alt="${product.name}" loading="lazy" />
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

  const more = document.getElementById("shopMore");

  const filtered = () => {
    const q = fold(query);
    const list = all.filter((item) => {
      if (current && item.tag !== current) return false;
      if (!q) return true;
      const hay = fold(`${item.name} ${item.tag} ${item.description || ""} ${item.blurb || ""}`);
      return hay.includes(q);
    });
    if (sort === "menor") list.sort((a, b) => a.price - b.price);
    else if (sort === "maior") list.sort((a, b) => b.price - a.price);
    else list.sort((a, b) => String(a.name).localeCompare(b.name, "pt-BR"));
    return list;
  };

  const paint = () => {
    const list = filtered();
    const slice = list.slice(0, shown);
    if (heading) heading.textContent = query ? `Busca: ${query}` : current || "Todas as categorias";
    if (lede) lede.textContent = `${list.length} produto${list.length === 1 ? "" : "s"} · envio após o pagamento`;
    if (grid) {
      grid.innerHTML = "";
      slice.forEach((product) => grid.appendChild(card(product)));
    }
    if (empty) {
      empty.hidden = list.length > 0;
      empty.textContent = query
        ? `Nada encontrado para “${query}”. Tente outro nome.`
        : "Nenhum produto nesta categoria.";
    }
    if (more) {
      more.hidden = slice.length >= list.length;
      if (list.length > slice.length) {
        more.querySelector("span").textContent = `Carregar mais (${list.length - slice.length} restantes)`;
      }
    }
    chips?.querySelectorAll("[data-cat]").forEach((btn) => {
      btn.classList.toggle("is-on", btn.getAttribute("data-cat") === current);
    });
  };

  const writeUrl = () => {
    const url = new URL(location.href);
    if (current) url.searchParams.set("cat", current);
    else url.searchParams.delete("cat");
    if (query) url.searchParams.set("q", query);
    else url.searchParams.delete("q");
    if (sort && sort !== "nome") url.searchParams.set("sort", sort);
    else url.searchParams.delete("sort");
    history.replaceState({}, "", url);
  };

  chips?.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-cat]");
    if (!btn) return;
    current = btn.getAttribute("data-cat") || "";
    shown = PAGE;
    writeUrl();
    paint();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  more?.addEventListener("click", () => {
    shown += PAGE;
    paint();
  });

  sortEl?.addEventListener("change", () => {
    sort = sortEl.value || "nome";
    shown = PAGE;
    writeUrl();
    paint();
  });

  document.getElementById("shopSearch")?.addEventListener("submit", (event) => {
    event.preventDefault();
    query = (searchInput?.value || "").trim();
    shown = PAGE;
    writeUrl();
    paint();
  });

  grid?.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-add]");
    if (!btn) return;
    window.LumeCart.add(btn.getAttribute("data-add"), 1);
    btn.querySelector("span").textContent = "Na sacola";
    window.setTimeout(() => {
      if (btn.querySelector("span")) btn.querySelector("span").textContent = "Sacola";
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
        note.textContent = "Abra o site pelo servidor (python server.py) para carregar os produtos.";
      }
    });
})();
