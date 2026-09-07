(() => {
  const TAG = "Tênis de mesa";
  const GROUPS = ["Raquetes", "Bolas", "Mesa e rede", "Treino", "Acessórios"];
  const grid = document.getElementById("shopGrid");
  const note = document.getElementById("shopNote");
  const chips = document.getElementById("pingChips");
  const heading = document.getElementById("shopHeading");
  const lede = document.getElementById("shopLede");
  const empty = document.getElementById("shopEmpty");
  const sortEl = document.getElementById("shopSort");
  const params = new URLSearchParams(location.search);
  const PAGE = 48;
  let group = params.get("grupo") || "";
  let sort = params.get("sort") || "nome";
  let all = [];
  let shown = PAGE;
  const more = document.getElementById("shopMore");
  if (sortEl) sortEl.value = sort;

  const paintChips = () => {
    if (!chips) return;
    const items = ["Todas", ...GROUPS];
    chips.innerHTML = items
      .map((name) => {
        const value = name === "Todas" ? "" : name;
        const on = group === value ? " is-on" : "";
        return `<button class="chip${on}" type="button" data-group="${value}">${name}</button>`;
      })
      .join("");
  };

  const filtered = () => {
    const list = all.filter((item) => {
      if (item.tag !== TAG) return false;
      if (group && item.group !== group) return false;
      return true;
    });
    if (sort === "menor") list.sort((a, b) => a.price - b.price);
    else if (sort === "maior") list.sort((a, b) => b.price - a.price);
    else list.sort((a, b) => String(a.name).localeCompare(b.name, "pt-BR"));
    return list;
  };

  const writeUrl = () => {
    const url = new URL(location.href);
    if (group) url.searchParams.set("grupo", group);
    else url.searchParams.delete("grupo");
    if (sort && sort !== "nome") url.searchParams.set("sort", sort);
    else url.searchParams.delete("sort");
    history.replaceState({}, "", url);
  };

  const paint = () => {
    const list = filtered();
    const slice = list.slice(0, shown);
    if (heading) heading.textContent = group || `Tênis de mesa · ${list.length} produtos`;
    if (lede) {
      lede.textContent = group
        ? `${group} · ${list.length} itens · frete grátis acima de R$ 200`
        : `${list.length} produtos só de tênis de mesa. Pix, cartão · frete grátis acima de R$ 200`;
    }
    if (grid) {
      grid.innerHTML = "";
      slice.forEach((product) => grid.appendChild(window.LumeCart.card(product)));
    }
    if (empty) {
      empty.hidden = list.length > 0;
      empty.textContent = "Nenhum produto neste grupo.";
    }
    if (more) {
      more.hidden = slice.length >= list.length;
    }
    chips?.querySelectorAll("[data-group]").forEach((btn) => {
      btn.classList.toggle("is-on", btn.getAttribute("data-group") === group);
    });
    document.querySelectorAll(".ping-path").forEach((btn) => {
      btn.classList.toggle("is-on", btn.getAttribute("data-group") === group);
    });
  };

  const applyGroup = (value) => {
    group = value || "";
    shown = PAGE;
    writeUrl();
    paint();
  };

  chips?.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-group]");
    if (!btn) return;
    applyGroup(btn.getAttribute("data-group") || "");
  });

  document.querySelectorAll(".ping-path").forEach((btn) => {
    btn.addEventListener("click", () => {
      applyGroup(btn.getAttribute("data-group") || "");
      document.getElementById("catalogo")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  sortEl?.addEventListener("change", () => {
    sort = sortEl.value || "nome";
    shown = PAGE;
    writeUrl();
    paint();
  });

  more?.addEventListener("click", () => {
    shown += PAGE;
    paint();
  });

  grid?.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-add]");
    if (!btn) return;
    window.LumeCart.add(btn.getAttribute("data-add"), 1);
  });

  paintChips();

  window.LumeCart.ready()
    .then((products) => {
      all = (products || []).filter((item) => item.tag === TAG);
      if (!all.length) {
        return fetch(`/api/products?cat=${encodeURIComponent(TAG)}`)
          .then((res) => res.json())
          .then((data) => {
            all = data.products || [];
            paint();
          });
      }
      paint();
    })
    .catch(() => {
      if (note) {
        note.hidden = false;
        note.textContent = "Abra o site pelo servidor (python server.py) para carregar os produtos.";
      }
    });
})();
