(() => {
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
    if (heading) heading.textContent = query ? `Busca: ${query}` : current || "Toda a loja";
    if (lede) {
      lede.textContent = `${list.length} ${list.length === 1 ? "peça" : "peças"} · Pix, cartão · frete grátis acima de R$ 200`;
    }
    if (grid) {
      grid.innerHTML = "";
      slice.forEach((product) => grid.appendChild(window.LumeCart.card(product)));
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
        more.querySelector("span").textContent = `Ver mais (${list.length - slice.length})`;
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

  const applyQuery = (value) => {
    query = (value || "").trim();
    shown = PAGE;
    writeUrl();
    paint();
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
    applyQuery(searchInput?.value);
  });

  let live;
  searchInput?.addEventListener("input", () => {
    clearTimeout(live);
    live = setTimeout(() => applyQuery(searchInput.value), 180);
  });

  grid?.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-add]");
    if (!btn) return;
    window.LumeCart.add(btn.getAttribute("data-add"), 1);
  });

  Promise.all([window.LumeCart.ready(), fetch("/api/categories").then((res) => res.json())])
    .then(([products, cats]) => {
      all = products || [];
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
