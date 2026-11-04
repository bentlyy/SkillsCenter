(function () {
  var R = window.RADAR || { items: [], total: 0, fuentes: 0, categorias: 0, nuevos: 0 };
  var items = R.items || [];
  var grid = document.querySelector("[data-items]");
  if (!grid) return;

  var chipBox = document.querySelector("[data-chips]");
  var res = document.querySelector("[data-resultado]");
  var more = document.querySelector("[data-vermas]");
  var input = document.querySelector("[data-buscar]");
  var categoria = "Todo";
  var texto = "";
  var paso = parseInt(grid.getAttribute("data-items") || "9", 10);
  var limite = paso;
  var top = (R.categoriasDetalle || []).filter(function (c) {
    return c.nombre && c.nombre !== "otros";
  }).slice(0, 8);

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function num(n) {
    return Number(n || 0).toLocaleString("es-ES");
  }

  function compacto(n) {
    n = Number(n || 0);
    if (n >= 1e6) return (n / 1e6).toFixed(1).replace(".", ",") + "M";
    if (n >= 1e3) return Math.round(n / 1e3) + "k";
    return String(n);
  }

  function metrica(it) {
    var m = it.metricas || {};
    var partes = [];
    if (m.estrellas) partes.push("★ " + compacto(m.estrellas));
    if (m.descargas) partes.push("↓ " + compacto(m.descargas));
    if (m.likes) partes.push("♥ " + compacto(m.likes));
    if (m.puntos) partes.push(num(m.puntos) + " pts");
    if (m.forks) partes.push("⑂ " + compacto(m.forks));
    return partes.join(" · ");
  }

  function tarjeta(it) {
    var met = metrica(it);
    return (
      '<article class="item">' +
        '<div class="item-top"><span class="badge">' + esc(it.fuente) + '</span>' +
        '<span class="score">' + (it.score || 0) + "</span></div>" +
        '<h3><a href="' + esc(it.url) + '" target="_blank" rel="noopener">' + esc(it.nombre) + "</a></h3>" +
        '<p class="desc">' + esc(it.desc || "Sin descripción disponible.") + "</p>" +
        '<div class="meta">' + (met ? "<span>" + esc(met) + "</span>" : "") +
        '<span class="cat">' + esc(it.cat || it.tipo || "") + "</span></div>" +
      "</article>"
    );
  }

  function visibles() {
    var q = texto.toLowerCase();
    return items.filter(function (it) {
      if (categoria !== "Todo" && it.cat !== categoria) return false;
      if (!q) return true;
      return (it.nombre + " " + it.desc + " " + it.fuente + " " + it.cat).toLowerCase().indexOf(q) !== -1;
    });
  }

  function pintar() {
    var lista = visibles();
    grid.innerHTML = lista.length
      ? lista.slice(0, limite).map(tarjeta).join("")
      : '<p class="vacio">Sin resultados para esa búsqueda. Prueba con “mcp”, “agente” o “rag”.</p>';
    if (res) {
      res.textContent = "Mostrando " + Math.min(limite, lista.length) + " de " + lista.length +
        " entradas de la muestra · " + num(R.total) + " en el catálogo";
    }
    if (more) more.hidden = lista.length <= limite;
    grid.querySelectorAll(".item").forEach(function (el) { el.classList.add("entra"); });
  }

  function chips() {
    if (!chipBox) return;
    var cats = [{ nombre: "Todo", n: items.length }].concat(top);
    chipBox.innerHTML = cats.map(function (c) {
      return '<button class="chip" type="button" data-cat="' + esc(c.nombre) + '" aria-pressed="' +
        (c.nombre === "Todo") + '">' + esc(c.nombre) + "</button>";
    }).join("");
    chipBox.addEventListener("click", function (e) {
      var b = e.target.closest("[data-cat]");
      if (!b) return;
      categoria = b.getAttribute("data-cat");
      limite = paso;
      chipBox.querySelectorAll(".chip").forEach(function (c) {
        c.setAttribute("aria-pressed", String(c === b));
      });
      pintar();
    });
  }

  function cifras() {
    var mapa = { "[data-total]": num(R.total), "[data-fuentes]": R.fuentes, "[data-categorias]": R.categorias, "[data-nuevos]": "+" + num(R.nuevos) };
    Object.keys(mapa).forEach(function (sel) {
      var el = document.querySelector(sel);
      if (el) el.textContent = mapa[sel];
    });
    document.querySelectorAll("[data-fecha]").forEach(function (el) {
      el.textContent = R.actualizado || "";
    });
  }

  function banda() {
    var box = document.querySelector("[data-cats-lista]");
    if (!box) return;
    box.innerHTML = top.map(function (c) {
      return '<button class="cat-tile" type="button" data-cat-tile="' + esc(c.nombre) + '">' +
        "<span>" + esc(c.nombre) + "</span><b>" + num(c.n) + "</b></button>";
    }).join("");
    box.addEventListener("click", function (e) {
      var b = e.target.closest("[data-cat-tile]");
      if (!b) return;
      var nombre = b.getAttribute("data-cat-tile");
      var chip = chipBox && chipBox.querySelector('[data-cat="' + nombre + '"]');
      if (chip) chip.click();
      document.getElementById("catalogo").scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  cifras();
  chips();
  banda();
  pintar();

  if (input) {
    input.addEventListener("input", function () {
      texto = input.value.trim();
      limite = paso;
      pintar();
    });
  }

  if (more) {
    more.addEventListener("click", function () {
      limite += paso;
      pintar();
    });
  }
})();
