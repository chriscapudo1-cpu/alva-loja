(() => {
  const catsEl = document.getElementById("homeCats");
  const featEl = document.getElementById("homeFeat");

  const FEATURED = [
    "pingpong-001",
    "tech-001",
    "casa-021",
    "pet-041",
    "moda-061",
    "carro-083",
    "pingpong-010",
    "esporte-121",
  ];

  const slides = [...document.querySelectorAll("#heroSlides img")];
  const dotsWrap = document.getElementById("heroDots");
  let slide = 0;
  let timer;

  const paintSlide = (index) => {
    if (!slides.length) return;
    slide = (index + slides.length) % slides.length;
    slides.forEach((img, i) => img.classList.toggle("is-on", i === slide));
    dotsWrap?.querySelectorAll("button").forEach((btn, i) => btn.classList.toggle("is-on", i === slide));
  };

  if (slides.length && dotsWrap) {
    dotsWrap.innerHTML = slides
      .map((_, i) => `<button type="button" aria-label="Composição ${i + 1}"${i === 0 ? ' class="is-on"' : ""}></button>`)
      .join("");
    dotsWrap.querySelectorAll("button").forEach((btn, i) => {
      btn.addEventListener("click", () => {
        paintSlide(i);
        restart();
      });
    });
    const restart = () => {
      clearInterval(timer);
      timer = setInterval(() => paintSlide(slide + 1), 7000);
    };
    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) restart();
  }

  if (!catsEl && !featEl) return;

  window.LumeCart.ready()
    .then((products) => {
      if (featEl) {
        const pick = FEATURED.map((id) => products.find((p) => p.id === id)).filter(Boolean);
        const extra = products.filter((p) => !FEATURED.includes(p.id)).slice(0, 8 - pick.length);
        featEl.innerHTML = "";
        [...pick, ...extra].slice(0, 8).forEach((product) => featEl.appendChild(window.LumeCart.card(product)));
      }
    })
    .catch(() => {
      if (featEl) {
        featEl.innerHTML =
          '<p class="shop__note">Abra pelo servidor (python server.py) para ver os destaques.</p>';
      }
    });

  featEl?.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-add]");
    if (!btn) return;
    window.LumeCart.add(btn.getAttribute("data-add"), 1);
  });
})();
