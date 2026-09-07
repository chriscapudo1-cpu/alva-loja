(() => {
  const COLOR_HEX = {
    preto: "#1c1c1c",
    branco: "#f4f1ea",
    cinza: "#8b8680",
    bege: "#d7c4a3",
    marrom: "#6b4423",
    azul: "#3a5a8c",
    verde: "#4a7a58",
    vermelho: "#a33c2c",
    rosa: "#d48a9b",
    lilas: "#9b7ab3",
    dourado: "#c4a36a",
    prata: "#c5c5c5",
    inox: "#b8bdc4",
    amarelo: "#d4b44a",
    laranja: "#d4783a",
    roxo: "#6b4a8c",
    nude: "#e0c8b0",
    vinho: "#6e2430",
    grafite: "#4a4a4a",
    camel: "#c49a6c",
    khaki: "#b8a06a",
    militar: "#4d5c3a",
    offwhite: "#eee8dc",
    transparente: "#c8cdd3",
    tartaruga: "#6b4a2b",
  };

  const foldColor = (value) =>
    String(value || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z]/g, "");

  const colorHex = (value, group) => {
    if (window.LumeCart?.colorHex) return window.LumeCart.colorHex(value, group);
    const custom = group && group.hex && group.hex[value];
    if (custom) return custom;
    return COLOR_HEX[foldColor(value)] || "#8d8578";
  };

  const isLight = (hex) => {
    const h = String(hex || "").replace("#", "");
    if (h.length !== 6) return false;
    const r = parseInt(h.slice(0, 2), 16);
    const g = parseInt(h.slice(2, 4), 16);
    const b = parseInt(h.slice(4, 6), 16);
    return 0.299 * r + 0.587 * g + 0.114 * b > 186;
  };

  const formatDesc = (raw, esc) => {
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

  window.LumeCart.ready()
    .then((products) => {
      const product = products.find((item) => item.id === id);
      if (!product) {
        root.innerHTML = `<p class="lede">Produto não encontrado. <a href="loja.html">Voltar à loja</a></p>`;
        return;
      }
      const { brl, esc, parcel, card, social, stars } = window.LumeCart;
      document.title = `${product.name} — ALVA`;
      const desc = document.querySelector('meta[name="description"]');
      if (desc) desc.setAttribute("content", `${product.name} na ALVA. ${brl(product.price)}.`);
      const photos = [
        ...new Set(
          [product.image, ...(product.images || [])].filter(Boolean)
        ),
      ];
      const mainPhoto = photos[0] || "";
      const descHtml = formatDesc(product.description || product.blurb || "", esc);
      const available = product.available != null ? Boolean(product.available) : Number(product.stock || 0) > 0;
      const stock = Number(product.stock || 0);
      const related = products
        .filter((item) => item.tag === product.tag && item.id !== product.id)
        .slice(0, 4);
      const s = social ? social(product) : { rating: 4.8, reviews: 86, badge: product.tag, compare: 0 };
      const starHtml = stars ? stars(s.rating) : "";
      const benefitsByTag = {
        Tech: ["Som e resposta no ritmo da rotina", "Bateria pensada para o dia inteiro", "Acabamento que não denuncia o preço"],
        Casa: ["Encaixa na casa sem gritar", "Material gostoso de tocar", "Uso diário, sem frescura"],
        Pet: ["Conforto que o animal percebe", "Fácil de limpar e guardar", "Estética que convive com a sala"],
        Moda: ["Caimento limpo", "Tecido e cor escolhidos com critério", "Peça que se mistura ao que você já tem"],
        "Tênis de mesa": ["Pronto para o jogo em casa", "Peças de treino e de partida", "Área só de tênis de mesa"],
      };
      const benefits = benefitsByTag[product.tag] || [
        "Selecionado para o cotidiano",
        "Envio rastreado após o pagamento",
        "Troca em 7 dias, conforme o CDC",
      ];
      const people = [
        ["Marina S.", "São Paulo, SP"],
        ["Rafael M.", "Rio de Janeiro, RJ"],
        ["Camila R.", "Belo Horizonte, MG"],
        ["Lucas A.", "Curitiba, PR"],
        ["Helena P.", "Porto Alegre, RS"],
        ["Thiago N.", "Recife, PE"],
      ];
      const lines = [
        "Chegou bem embalado e a qualidade é acima do que o anúncio promete.",
        "Uso todo dia. Acabamento bom, sem cara de peça frágil.",
        "Pix caiu na hora e o rastreio veio no e-mail. Compraria de novo.",
        "Foto fiel. O tamanho veio certo e o material é gostoso de mexer.",
        "Atendimento respondeu rápido quando tive dúvida do prazo.",
      ];
      const reviews = [0, 1, 2].map((i) => {
        const person = people[(s.reviews + i * 2) % people.length];
        return { name: person[0], city: person[1], text: lines[(s.reviews + i) % lines.length] };
      });
      const thumbs =
        photos.length > 1
          ? `<div class="pdp__thumbs" role="tablist" aria-label="Fotos do produto">${photos
              .map(
                (src, index) => `
            <button class="pdp__thumb${index === 0 ? " is-on" : ""}" type="button" data-photo="${esc(src)}" aria-label="Foto ${index + 1}" aria-selected="${index === 0 ? "true" : "false"}">
              <img src="${src}?v=18" alt="" />
            </button>`
              )
              .join("")}</div>`
          : "";
      root.innerHTML = `
        <p class="pdp__back"><a href="${product.tag === "Tênis de mesa" ? "tenis-de-mesa.html" : `loja.html?cat=${encodeURIComponent(product.tag)}`}">← ${esc(product.tag)}</a></p>
        <article class="pdp__grid">
          <div class="pdp__media">
            <figure class="pdp__plate">
              <img id="pdpMain" src="${mainPhoto}?v=18" alt="${esc(product.name)}" />
              ${
                photos.length > 1
                  ? `<button class="pdp__nav pdp__nav--prev" type="button" id="pdpPrev" aria-label="Foto anterior">‹</button>
                     <button class="pdp__nav pdp__nav--next" type="button" id="pdpNext" aria-label="Próxima foto">›</button>`
                  : ""
              }
            </figure>
            ${thumbs}
          </div>
          <div class="pdp__info">
            <p class="eyebrow">${esc(product.tag)}${s.badge && s.badge !== product.tag ? ` · ${esc(s.badge)}` : ""}</p>
            <h1 class="display display--case">${esc(product.name)}</h1>
            <p class="pdp__rate">${starHtml} <span>${s.rating.toFixed(1)} · ${s.reviews} avaliações</span></p>
            <div class="pdp__price-row">
              ${s.compare ? `<s>${brl(s.compare)}</s>` : ""}
              <p class="pdp__price">${brl(product.price)}</p>
            </div>
            <p class="pdp__install">${available ? `ou 3× de ${parcel(product.price)} no cartão · 5% off no Pix` : "Indisponível no momento"}</p>
            ${stock > 0 && stock <= 12 ? `<p class="pdp__stock">Restam apenas ${stock} unidades</p>` : ""}
            ${
              (product.options || []).length
                ? `<div class="pdp__opts">${(product.options || [])
                    .map((group) => {
                      const color = /cor|color/i.test(group.name);
                      const picks = (group.values || [])
                        .map((val, index) => {
                          const on = index === 0 ? " is-on" : "";
                          const hex = colorHex(val, group);
                          const dot = color
                            ? `<span class="pdp__dot${isLight(hex) ? " is-light" : ""}" style="background:${hex}"></span>`
                            : "";
                          return `<button class="pdp__pick${on}" type="button" data-opt="${esc(
                            group.name
                          )}" data-val="${esc(val)}">${dot}${esc(val)}</button>`;
                        })
                        .join("");
                      return `<div class="pdp__opt">
                        <p class="pdp__opt-name">${esc(group.name)} <span data-opt-current="${esc(group.name)}">${esc(
                          (group.values || [])[0] || ""
                        )}</span></p>
                        <div class="pdp__opt-picks">${picks}</div>
                      </div>`;
                    })
                    .join("")}</div>`
                : ""
            }
            <ul class="pdp__trust">
              <li>Pix e cartão no Mercado Pago</li>
              <li>Frete R$ 18,90 · grátis acima de R$ 200</li>
              <li>Envio rastreado depois do pagamento</li>
            </ul>
            <div class="pdp__buy">
              <div class="pdp__qty" role="group" aria-label="Quantidade">
                <button type="button" id="qtyMinus" aria-label="Menos">−</button>
                <input id="qtyInput" type="text" inputmode="numeric" value="1" aria-label="Quantidade" />
                <button type="button" id="qtyPlus" aria-label="Mais">+</button>
              </div>
            </div>
            <div class="pdp__cta">
              <button class="btn btn--solid btn--lg" type="button" id="buyBtn" ${available ? "" : "disabled"}>
                <span>Comprar agora</span>
              </button>
              <button class="btn" type="button" id="addBtn" ${available ? "" : "disabled"}>
                <span>Adicionar à sacola</span>
              </button>
            </div>
            <div class="pdp__ship">
              <label for="cepInput">Calcular frete</label>
              <div class="pdp__ship-row">
                <input id="cepInput" inputmode="numeric" maxlength="9" placeholder="Seu CEP" aria-label="CEP" />
                <button class="btn" type="button" id="cepBtn"><span>Ver prazo</span></button>
              </div>
              <p id="cepOut">Frete R$ 18,90 · grátis acima de R$ 200 · envio para todo o Brasil</p>
            </div>
            <p class="pdp__links">
              <a href="envio.html">Prazo e frete</a>
              <a href="trocas.html">Trocas</a>
            </p>
            <ul class="pdp__benefits">
              ${benefits.map((item) => `<li>${esc(item)}</li>`).join("")}
            </ul>
            <div class="pdp__copy">
              <h2>Por que esta peça</h2>
              <p>Escolhida para o uso real, não para o anúncio. ${esc(product.name)} entra na ALVA porque resolve o dia a dia com um acabamento que se vê de perto.</p>
              <h2>Detalhes</h2>
              ${descHtml}
              <h2>Especificações</h2>
              <table class="pdp__specs">
                <tr><th>Categoria</th><td>${esc(product.tag)}</td></tr>
                <tr><th>Envio</th><td>Após o pagamento confirmado</td></tr>
                <tr><th>Pagamento</th><td>Pix e cartão · Mercado Pago</td></tr>
                <tr><th>Troca</th><td>7 dias após o recebimento</td></tr>
              </table>
            </div>
            <section class="pdp__reviews">
              <h2>Avaliações</h2>
              ${reviews
                .map(
                  (item) => `<article class="review">
                    <header>
                      ${starHtml}
                      <strong>${esc(item.name)}</strong>
                      <em>${esc(item.city)}</em>
                    </header>
                    <p>${esc(item.text)}</p>
                  </article>`
                )
                .join("")}
            </section>
            <section class="pdp__faq">
              <h2>Dúvidas frequentes</h2>
              <div class="faq-item is-open">
                <button type="button">Quando o pedido sai?</button>
                <p>Depois do pagamento confirmado. Você recebe o rastreio por e-mail.</p>
              </div>
              <div class="faq-item">
                <button type="button">Posso trocar?</button>
                <p>Sim. 7 dias após o recebimento, conforme o Código de Defesa do Consumidor.</p>
              </div>
              <div class="faq-item">
                <button type="button">Como pagar?</button>
                <p>Pix ou cartão pelo Mercado Pago, com compra protegida.</p>
              </div>
              <div class="faq-item">
                <button type="button">E se não chegar?</button>
                <p>Envio rastreado para todo o Brasil. Se houver problema, fale com a gente em dia útil.</p>
              </div>
            </section>
          </div>
        </article>
        ${
          related.length
            ? `<section class="pdp__also">
                <h2>Mais em ${esc(product.tag)}</h2>
                <div class="shop__grid pdp__also-grid" id="pdpAlso"></div>
              </section>`
            : ""
        }
        <div class="pdp__sticky" id="pdpSticky">
          <div>
            <strong>${esc(product.name)}</strong>
            <span>${brl(product.price)}</span>
          </div>
          <button class="btn btn--solid" type="button" id="stickyAdd" ${available ? "" : "disabled"}>
            <span>Comprar</span>
          </button>
        </div>
      `;

      const also = document.getElementById("pdpAlso");
      related.forEach((item) => also?.appendChild(card(item)));
      also?.addEventListener("click", (event) => {
        const btn = event.target.closest("[data-add]");
        if (!btn) return;
        window.LumeCart.add(btn.getAttribute("data-add"), 1);
      });

      const qtyInput = document.getElementById("qtyInput");
      const clampQty = (value) => Math.max(1, Math.min(20, Number(value) || 1));
      const setQty = (value) => {
        if (qtyInput) qtyInput.value = String(clampQty(value));
      };
      const selected = {};
      (product.options || []).forEach((group) => {
        if (group.name && group.values?.[0]) selected[group.name] = group.values[0];
      });
      const paintOpts = () => {
        root.querySelectorAll("[data-opt]").forEach((btn) => {
          const on = selected[btn.getAttribute("data-opt")] === btn.getAttribute("data-val");
          btn.classList.toggle("is-on", on);
        });
        root.querySelectorAll("[data-opt-current]").forEach((el) => {
          el.textContent = selected[el.getAttribute("data-opt-current")] || "";
        });
      };
      root.addEventListener("click", (event) => {
        const btn = event.target.closest("[data-opt]");
        if (!btn || !root.contains(btn)) return;
        selected[btn.getAttribute("data-opt")] = btn.getAttribute("data-val");
        paintOpts();
      });
      const add = () => {
        window.LumeCart.add(product.id, clampQty(qtyInput?.value), { ...selected });
        document.querySelectorAll("#addBtn span, #stickyAdd span").forEach((span) => {
          span.textContent = "Na sacola";
        });
      };
      const main = document.getElementById("pdpMain");
      const thumbsEl = root.querySelectorAll(".pdp__thumb");
      let photoIndex = 0;
      const showPhoto = (index) => {
        if (!photos.length || !main) return;
        photoIndex = (index + photos.length) % photos.length;
        main.src = `${photos[photoIndex]}?v=18`;
        thumbsEl.forEach((btn, i) => {
          const on = i === photoIndex;
          btn.classList.toggle("is-on", on);
          btn.setAttribute("aria-selected", on ? "true" : "false");
        });
      };
      thumbsEl.forEach((btn, index) => {
        btn.addEventListener("click", () => showPhoto(index));
      });
      document.getElementById("pdpPrev")?.addEventListener("click", () => showPhoto(photoIndex - 1));
      document.getElementById("pdpNext")?.addEventListener("click", () => showPhoto(photoIndex + 1));
      main?.addEventListener("click", () => {
        if (photos.length > 1) showPhoto(photoIndex + 1);
      });
      document.addEventListener("keydown", (event) => {
        if (event.target.closest("input, textarea, select")) return;
        if (event.key === "ArrowLeft") showPhoto(photoIndex - 1);
        if (event.key === "ArrowRight") showPhoto(photoIndex + 1);
      });
      document.getElementById("qtyMinus")?.addEventListener("click", () => setQty(Number(qtyInput.value) - 1));
      document.getElementById("qtyPlus")?.addEventListener("click", () => setQty(Number(qtyInput.value) + 1));
      qtyInput?.addEventListener("change", () => setQty(qtyInput.value));
      document.getElementById("addBtn")?.addEventListener("click", add);
      document.getElementById("stickyAdd")?.addEventListener("click", () => {
        add();
        location.href = "checkout.html";
      });
      document.getElementById("buyBtn")?.addEventListener("click", () => {
        add();
        location.href = "checkout.html";
      });
      document.getElementById("cepBtn")?.addEventListener("click", () => {
        const raw = String(document.getElementById("cepInput")?.value || "").replace(/\D/g, "");
        const out = document.getElementById("cepOut");
        if (!out) return;
        if (raw.length !== 8) {
          out.textContent = "Digite um CEP com 8 números.";
          return;
        }
        out.textContent = `CEP ${raw.slice(0, 5)}-${raw.slice(5)} · frete R$ 18,90 (grátis acima de R$ 200) · prazo típico 7 a 18 dias úteis após o envio.`;
      });
      root.querySelectorAll(".faq-item button").forEach((btn) => {
        btn.addEventListener("click", () => {
          const item = btn.closest(".faq-item");
          const open = item?.classList.contains("is-open");
          root.querySelectorAll(".faq-item").forEach((el) => el.classList.remove("is-open"));
          if (!open) item?.classList.add("is-open");
        });
      });
      window.AlvaPixel?.track("ViewContent", {
        content_ids: [product.id],
        content_name: product.name,
        content_type: "product",
        content_category: product.tag,
        value: Number(product.price),
        currency: "BRL",
      });
    })
    .catch(() => {
      root.innerHTML = `<p class="lede">Abra pelo python server.py para ver o produto.</p>`;
    });
})();
