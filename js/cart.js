(() => {
  const KEY = "lume-cart";

  const read = () => {
    try {
      const data = JSON.parse(localStorage.getItem(KEY) || "[]");
      return Array.isArray(data) ? data : [];
    } catch {
      return [];
    }
  };

  const write = (items) => {
    localStorage.setItem(KEY, JSON.stringify(items));
    paint();
  };

  const count = () => read().reduce((sum, item) => sum + Number(item.qty || 0), 0);

  const paint = () => {
    const total = count();
    document.querySelectorAll("[data-cart-count]").forEach((el) => {
      el.textContent = String(total);
      el.hidden = total === 0;
    });
  };

  window.LumeCart = {
    read,
    write,
    count,
    paint,
    add(id, qty = 1) {
      const items = read();
      const found = items.find((item) => item.id === id);
      if (found) found.qty = Math.min(20, Number(found.qty) + qty);
      else items.push({ id, qty });
      write(items);
    },
    setQty(id, qty) {
      const next = Math.max(0, Math.min(20, Number(qty) || 0));
      const items = read().flatMap((item) => {
        if (item.id !== id) return [item];
        return next ? [{ id, qty: next }] : [];
      });
      write(items);
    },
    remove(id) {
      write(read().filter((item) => item.id !== id));
    },
    clear() {
      write([]);
    },
  };

  paint();
})();
