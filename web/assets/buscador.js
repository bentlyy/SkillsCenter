(function () {
  "use strict";

  var C = window.CATALOGO;
  var grid = document.querySelector("[data-items]");
  if (!C || !grid) return;

  var FUENTES = C.fuentes || [];
  var TIPOS = C.tipos || [];
  var USOS = C.usos || [];
  var PASO = parseInt(grid.getAttribute("data-items") || "24", 10);

  var input = document.querySelector("[data-buscar]");
  var res = document.querySelector("[data-resultado]");
  var more = document.querySelector("[data-vermas]");
  var tiposChips = document.querySelector("[data-tipos-chips]");
  var usosChips = document.querySelector("[data-usos-chips]");
  var tiposLista = document.querySelector("[data-tipos-lista]");
  var usosLista = document.querySelector("[data-usos-lista]");
  var resumen = document.querySelector("[data-filtro-resumen]");
  var form = document.querySelector("[data-buscador]");
  var vivo = document.querySelector("[data-resultado-vivo]");
  var interpretacion = document.querySelector("[data-interpretacion]");
  var intencionesChips = document.querySelector("[data-intenciones-chips]");
  var intencionesBox = document.querySelector("[data-intenciones]");
  var previaBox = document.querySelector("[data-previa]");
  var previaLista = document.querySelector("[data-previa-lista]");
  var previaN = document.querySelector("[data-previa-n]");
  var previaVer = document.querySelector("[data-ver-resultados]");
  var catalogo = document.getElementById("catalogo");

  var q = "";
  var tipo = "";
  var uso = "";
  var limite = PASO;
  var frame = 0;
  var urlTimer = 0;

  var STOP = {
    necesito: 1,
    quiero: 1,
    busco: 1,
    buscar: 1,
    algo: 1,
    una: 1,
    un: 1,
    que: 1,
    haga: 1,
    hacer: 1,
    sirva: 1,
    sirve: 1,
    para: 1,
    de: 1,
    del: 1,
    la: 1,
    el: 1,
    los: 1,
    las: 1,
    en: 1,
    con: 1,
    por: 1,
    mi: 1,
    me: 1,
    y: 1,
    o: 1,
    u: 1,
    como: 1,
    donde: 1,
    cual: 1,
    cuales: 1,
    es: 1,
    son: 1,
    herramienta: 1,
    herramientas: 1,
    tool: 1,
    tools: 1,
    the: 1,
    a: 1,
    an: 1,
    for: 1,
    to: 1,
    with: 1,
    that: 1,
    does: 1,
    do: 1,
    i: 1,
    need: 1,
    want: 1,
    looking: 1
  };

  var INTENCIONES = [
    {
      id: "web",
      nombre: "Diseñar una web",
      descripcion: "Landings, interfaces y componentes.",
      consulta: "diseño de páginas web",
      frases: [
        "diseno de paginas web",
        "diseno web",
        "pagina web",
        "paginas web",
        "landing page",
        "sitio web",
        "aplicacion web",
        "interfaz web",
        "frontend",
        "disenar una web"
      ],
      terminos: [
        "web",
        "landing",
        "frontend",
        "front-end",
        "html",
        "css",
        "react",
        "vue",
        "svelte",
        "tailwind",
        "figma",
        "interfaz",
        "componente",
        "ui",
        "ux",
        "design",
        "diseno",
        "disenar"
      ],
      usos: ["diseno", "codigo"]
    },
    {
      id: "datos",
      nombre: "Modelar una base de datos",
      descripcion: "Esquemas, SQL, ETL y análisis.",
      consulta: "arquitectura de base de datos",
      frases: [
        "base de datos",
        "arquitectura de datos",
        "modelo de datos",
        "esquema de datos",
        "consultar datos",
        "analizar datos",
        "analisis de datos",
        "disenar base de datos"
      ],
      terminos: [
        "sql",
        "database",
        "postgres",
        "postgresql",
        "mysql",
        "sqlite",
        "mongodb",
        "esquema",
        "schema",
        "etl",
        "dataframe",
        "datos",
        "analitica",
        "duckdb",
        "bigquery",
        "consulta"
      ],
      usos: ["datos", "investigacion"]
    },
    {
      id: "automatizacion",
      nombre: "Automatizar tareas",
      descripcion: "Agentes, flujos y orquestación.",
      consulta: "automatizar tareas",
      frases: [
        "automatizar tareas",
        "automatizar procesos",
        "flujo de trabajo",
        "workflow",
        "orquestar agentes",
        "agentes autonomos",
        "automatizacion"
      ],
      terminos: [
        "automatizar",
        "automatizacion",
        "workflow",
        "orquestador",
        "orquestar",
        "agente",
        "agentes",
        "agents",
        "n8n",
        "zapier",
        "make",
        "pipeline",
        "tarea",
        "tareas"
      ],
      usos: ["automatizacion"]
    },
    {
      id: "codigo",
      nombre: "Escribir código",
      descripcion: "Programar, revisar y probar.",
      consulta: "escribir código",
      frases: [
        "escribir codigo",
        "programar",
        "revisar codigo",
        "generar codigo",
        "asistente de codigo",
        "desarrollo de software"
      ],
      terminos: [
        "codigo",
        "programar",
        "programacion",
        "developer",
        "dev",
        "ide",
        "vscode",
        "copilot",
        "testing",
        "refactor",
        "debug",
        "software"
      ],
      usos: ["codigo"]
    },
    {
      id: "prompts",
      nombre: "Crear prompts",
      descripcion: "Instrucciones, plantillas y evaluación.",
      consulta: "crear prompts",
      frases: [
        "crear prompts",
        "disenar prompts",
        "prompt engineering",
        "plantillas de prompts",
        "mejorar prompts",
        "sistema de prompts"
      ],
      terminos: [
        "prompt",
        "prompts",
        "instrucciones",
        "plantilla",
        "plantillas",
        "few shot"
      ],
      usos: ["prompts"]
    },
    {
      id: "imagen",
      nombre: "Generar imágenes",
      descripcion: "Crear, editar y analizar imagen.",
      consulta: "generar imágenes",
      frases: [
        "generar imagenes",
        "crear imagenes",
        "editar imagenes",
        "analizar imagenes",
        "vision artificial",
        "texto a imagen",
        "generar fotos",
        "editar fotos"
      ],
      terminos: [
        "imagen",
        "imagenes",
        "image",
        "images",
        "vision",
        "diffusion",
        "midjourney",
        "dalle",
        "flux",
        "comfyui",
        "ocr",
        "foto",
        "fotos"
      ],
      usos: ["imagen"]
    },
    {
      id: "investigacion",
      nombre: "Investigar y RAG",
      descripcion: "Buscar, recuperar y sintetizar.",
      consulta: "investigar con RAG",
      frases: [
        "investigar",
        "buscar informacion",
        "rag",
        "retrieval augmented generation",
        "base de conocimiento",
        "resumir documentos",
        "analizar pdf",
        "leer documentos"
      ],
      terminos: [
        "rag",
        "retrieval",
        "embedding",
        "embeddings",
        "vector",
        "busqueda",
        "search",
        "investigacion",
        "investigar",
        "research",
        "pdf",
        "documento",
        "documentos",
        "knowledge",
        "memoria"
      ],
      usos: ["investigacion"]
    },
    {
      id: "integracion",
      nombre: "Conectar herramientas",
      descripcion: "APIs, MCP, Slack y datos.",
      consulta: "conectar herramientas con MCP",
      frases: [
        "conectar herramientas",
        "integrar api",
        "servidor mcp",
        "model context protocol",
        "conectar slack",
        "conectar base de datos",
        "conectar api",
        "plugin"
      ],
      terminos: [
        "mcp",
        "api",
        "integracion",
        "integrar",
        "conectar",
        "plugin",
        "webhook",
        "slack",
        "notion",
        "github",
        "sdk",
        "server",
        "servidor"
      ],
      usos: ["integracion"]
    }
  ];

  function norm(valor) {
    return String(valor == null ? "" : valor)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();
  }

  function esc(valor) {
    return String(valor == null ? "" : valor).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function num(valor) {
    return String(Number(valor || 0)).replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  }

  function urlOk(valor) {
    return /^https?:\/\//i.test(String(valor || "")) ? valor : "#";
  }

  function coincide(haystack, token) {
    var i = haystack.indexOf(token);
    while (i !== -1) {
      if (i === 0 || !/[a-z0-9]/.test(haystack.charAt(i - 1))) return true;
      i = haystack.indexOf(token, i + 1);
    }
    return false;
  }

  function exacta(haystack, token) {
    var i = haystack.indexOf(token);
    while (i !== -1) {
      var fin = i + token.length;
      if (
        (i === 0 || !/[a-z0-9]/.test(haystack.charAt(i - 1))) &&
        (fin === haystack.length || !/[a-z0-9]/.test(haystack.charAt(fin)))
      ) {
        return true;
      }
      i = haystack.indexOf(token, i + 1);
    }
    return false;
  }

  var ITEMS = (C.items || []).map(function (a) {
    var tipoDef = TIPOS[a[3]] || { id: "", nombre: "", alias: [] };
    var fuente = FUENTES[a[2]] || { nombre: "" };
    var usos = (a[6] || []).map(function (indice) {
      return USOS[indice];
    }).filter(Boolean);
    var it = {
      n: a[0],
      u: a[1],
      t: tipoDef.id,
      c: a[4] || "",
      p: a[5] || 0,
      f: a[6] || [],
      m: a[7] || "",
      d: a[8] || "",
      k: a[9] || "",
      tipo: tipoDef,
      usos: usos,
      fuente: fuente
    };
    it.ui = usos.map(function (u) {
      return u.id;
    });
    var alias = [tipoDef.nombre + " " + (tipoDef.alias || []).join(" ")].concat(
      usos.map(function (u) {
        return u.nombre + " " + (u.alias || []).join(" ");
      })
    );
    it.nn = norm(it.n);
    it.nd = norm(it.d);
    it.nk = norm(it.k);
    it.nc = norm(it.c);
    it.nf = norm(fuente.nombre);
    it.nu = norm(
      usos.map(function (u) {
        return u.nombre + " " + (u.alias || []).join(" ");
      }).join(" ")
    );
    it.nt = norm(tipoDef.nombre + " " + (tipoDef.alias || []).join(" "));
    it.h = norm(
      [it.n, it.d, it.c, it.k, fuente.nombre].concat(alias).join(" ")
    );
    return it;
  });

  function tokensDe(texto) {
    return norm(texto).split(/[^a-z0-9]+/).filter(function (token) {
      return token.length > 1 && !STOP[token];
    });
  }

  function intencionPorId(id) {
    for (var i = 0; i < INTENCIONES.length; i++) {
      if (INTENCIONES[i].id === id) return INTENCIONES[i];
    }
    return null;
  }

  function detectarIntenciones(texto, tokens) {
    var halladas = [];
    INTENCIONES.forEach(function (intent) {
      var puntos = 0;
      intent.frases.forEach(function (frase) {
        if (coincide(texto, frase)) puntos += 8 + frase.split(/\s+/).length;
      });
      intent.terminos.forEach(function (term) {
        if (tokens.indexOf(term) !== -1) puntos += 5;
        else if (term.length > 3 && coincide(texto, term)) puntos += 2;
      });
      if (puntos >= 5) halladas.push({ intent: intent, puntos: puntos });
    });
    halladas.sort(function (a, b) {
      return b.puntos - a.puntos;
    });
    return halladas.slice(0, 2).map(function (item) {
      return item.intent;
    });
  }

  function consulta() {
    var texto = norm(q);
    var tokens = tokensDe(q);
    if (coincide(texto, "base de datos")) {
      tokens = tokens.filter(function (token) {
        return token !== "base";
      });
    }
    return {
      texto: texto,
      tokens: tokens,
      tokensRango: tokens,
      intents: detectarIntenciones(texto, tokens)
    };
  }

  function coincideIntencion(it, intent) {
    for (var i = 0; i < intent.terminos.length; i++) {
      if (exacta(it.h, intent.terminos[i])) return true;
    }
    return false;
  }

  function porTexto(consultaActual) {
    if (!consultaActual.texto) return ITEMS;
    if (!consultaActual.tokens.length) return ITEMS;

    var estrictos = ITEMS.filter(function (it) {
      for (var i = 0; i < consultaActual.tokens.length; i++) {
        if (!coincide(it.h, consultaActual.tokens[i])) return false;
      }
      return true;
    });
    if (estrictos.length) return estrictos;

    if (consultaActual.intents.length) {
      return ITEMS.filter(function (it) {
        for (var i = 0; i < consultaActual.intents.length; i++) {
          if (coincideIntencion(it, consultaActual.intents[i])) return true;
        }
        return false;
      });
    }

    return estrictos;
  }

  function porTipo(base, id) {
    if (!id) return base;
    return base.filter(function (it) {
      return it.t === id;
    });
  }

  function porUso(base, id) {
    if (!id) return base;
    return base.filter(function (it) {
      return it.ui.indexOf(id) !== -1;
    });
  }

  function contar(lista, campo) {
    var mapa = {};
    lista.forEach(function (it) {
      if (campo === "tipo") {
        mapa[it.t] = (mapa[it.t] || 0) + 1;
      } else {
        it.ui.forEach(function (id) {
          mapa[id] = (mapa[id] || 0) + 1;
        });
      }
    });
    return mapa;
  }

  function nombreTipo(id) {
    for (var i = 0; i < TIPOS.length; i++) {
      if (TIPOS[i].id === id) return TIPOS[i].nombre;
    }
    return id;
  }

  function nombreUso(id) {
    for (var i = 0; i < USOS.length; i++) {
      if (USOS[i].id === id) return USOS[i].nombre;
    }
    return id;
  }

  function tarjeta(it) {
    var usos = it.usos.slice(0, 3).map(function (u) {
      return '<span class="uso">' + esc(u.nombre) + "</span>";
    }).join("");
    var href = esc(urlOk(it.u));
    var metrica = it.m ? '<span class="metric">' + esc(it.m) + "</span>" : "";
    return (
      '<article class="item">' +
        '<div class="item-top"><span class="badge">' + esc(it.tipo.nombre) + "</span>" +
        '<span class="score" title="Puntuación">' + esc(it.p) + "</span></div>" +
        '<h3><a href="' + href + '" target="_blank" rel="noopener">' + esc(it.n) + "</a></h3>" +
        '<p class="desc">' + esc(it.d || "Sin descripción disponible.") + "</p>" +
        '<div class="usos">' + usos + "</div>" +
        '<div class="meta"><span>' + esc(it.fuente.nombre) + "</span>" + metrica +
        '<a class="abrir" href="' + href + '" target="_blank" rel="noopener">Abrir ↗</a></div>' +
      "</article>"
    );
  }

  function chip(id, nombre, n, activo, atributo) {
    var deshabilitado = n === 0 && !activo ? " disabled" : "";
    return (
      '<button class="chip" type="button" ' + atributo + '="' + esc(id) + '" aria-pressed="' +
      (activo ? "true" : "false") + '"' + deshabilitado + ">" + esc(nombre) +
      ' <span class="n">' + num(n) + "</span></button>"
    );
  }

  function pintarChips(conteoTipos, conteoUsos, totalTipos, totalUsos) {
    if (tiposChips) {
      var tipos = [{ id: "", nombre: "Todos" }].concat(
        TIPOS.filter(function (t) {
          return t.id && (conteoTipos[t.id] || tipo === t.id);
        })
      );
      tiposChips.innerHTML = tipos.map(function (t) {
        return chip(
          t.id,
          t.nombre,
          t.id ? conteoTipos[t.id] || 0 : totalTipos,
          t.id === tipo,
          "data-tipo"
        );
      }).join("");
    }

    if (usosChips) {
      var usos = [{ id: "", nombre: "Todos" }].concat(
        USOS.filter(function (u) {
          return u.id && (conteoUsos[u.id] || uso === u.id);
        })
      );
      usosChips.innerHTML = usos.map(function (u) {
        return chip(
          u.id,
          u.nombre,
          u.id ? conteoUsos[u.id] || 0 : totalUsos,
          u.id === uso,
          "data-uso"
        );
      }).join("");
    }
  }

  function pintarTiles(conteoTipos, conteoUsos, totalTipos, totalUsos) {
    if (tiposLista) {
      var tipos = [{ id: "", nombre: "Todos" }].concat(
        TIPOS.filter(function (t) {
          return t.id && (conteoTipos[t.id] || tipo === t.id);
        })
      );
      tiposLista.innerHTML = tipos.map(function (t) {
        return (
          '<button class="facet-tile" type="button" data-tipo-tile="' + esc(t.id) +
          '" aria-pressed="' + (t.id === tipo) + '" title="' + esc(t.descripcion || "") + '">' +
          esc(t.nombre) + " <b>" + num(t.id ? conteoTipos[t.id] || 0 : totalTipos) + "</b></button>"
        );
      }).join("");
    }

    if (usosLista) {
      var usos = [{ id: "", nombre: "Todos" }].concat(
        USOS.filter(function (u) {
          return u.id && (conteoUsos[u.id] || uso === u.id);
        })
      );
      usosLista.innerHTML = usos.map(function (u) {
        return (
          '<button class="facet-tile" type="button" data-uso-tile="' + esc(u.id) +
          '" aria-pressed="' + (u.id === uso) + '" title="' + esc(u.descripcion || "") + '">' +
          esc(u.nombre) + " <b>" + num(u.id ? conteoUsos[u.id] || 0 : totalUsos) + "</b></button>"
        );
      }).join("");
    }
  }

  function pintarResumen(consultaActual) {
    if (!resumen) return;
    var partes = [];
    if (tipo) partes.push("Tipo: " + nombreTipo(tipo));
    if (uso) partes.push("Uso: " + nombreUso(uso));
    if (q) partes.push("“" + q + "”");
    if (q && consultaActual.intents.length) {
      partes.push(
        "Intención: " + consultaActual.intents.map(function (intent) {
          return intent.nombre;
        }).join(" / ")
      );
    }
    resumen.textContent = partes.length
      ? partes.join(" · ") + (q ? " · por relevancia" : " · por puntuación")
      : "Sin filtros · ordenado por puntuación";

    document.querySelectorAll("[data-limpiar-filtros]").forEach(function (el) {
      el.hidden = !(q || tipo || uso);
    });
  }

  function rango(it, consultaActual) {
    var valor = it.p;
    var tokens = consultaActual.tokensRango;
    var peso = consultaActual.intents.length ? 0.55 : 1;
    for (var i = 0; i < tokens.length; i++) {
      var t = tokens[i];
      if (exacta(it.nn, t)) valor += 120 * peso;
      else if (coincide(it.nn, t)) valor += 60 * peso;
      if (exacta(it.nu, t)) valor += 45 * peso;
      if (exacta(it.nt, t)) valor += 35 * peso;
      if (exacta(it.nk, t)) valor += 35 * peso;
      else if (coincide(it.nk, t)) valor += 15 * peso;
      if (exacta(it.nc, t)) valor += 20 * peso;
      if (exacta(it.nd, t)) valor += 25 * peso;
      if (exacta(it.nf, t)) valor += 10 * peso;
    }

    consultaActual.intents.forEach(function (intent) {
      for (var j = 0; j < intent.usos.length; j++) {
        if (it.ui.indexOf(intent.usos[j]) !== -1) {
          valor += j === 0 ? 45 : 20;
        }
      }
      if (intent.id === "web" && it.ui.indexOf("diseno") !== -1) {
        valor += 60;
        if (coincide(it.nn, "design") || coincide(it.nn, "diseno")) valor += 100;
      }

      var aciertos = 0;
      intent.terminos.forEach(function (term) {
        if (exacta(it.nn, term)) {
          valor += 45;
          aciertos++;
        } else if (exacta(it.nu, term)) {
          valor += 40;
          aciertos++;
        } else if (exacta(it.nt, term)) {
          valor += 30;
          aciertos++;
        } else if (exacta(it.nk, term)) {
          valor += 20;
          aciertos++;
        } else if (exacta(it.nd, term)) {
          valor += 10;
          aciertos++;
        }
      });
      if (aciertos >= 2) valor += 50;

      for (var k = 0; k < intent.frases.length; k++) {
        if (exacta(it.h, intent.frases[k])) {
          valor += 80;
          break;
        }
      }
    });

    return valor;
  }

  function pintarInterpretacion(consultaActual) {
    if (!interpretacion || !intencionesChips) return;
    if (!q || !consultaActual.intents.length) {
      interpretacion.hidden = true;
      intencionesChips.innerHTML = "";
      return;
    }
    interpretacion.hidden = false;
    intencionesChips.innerHTML = consultaActual.intents.map(function (intent) {
      return '<span class="intencion-tag">' + esc(intent.nombre) + "</span>";
    }).join("");
  }

  function pintarPrevia(lista) {
    if (!previaBox || !previaLista) return;
    if (!q) {
      previaBox.hidden = true;
      previaLista.innerHTML = "";
      if (previaN) previaN.textContent = "";
      if (previaVer) previaVer.hidden = true;
      return;
    }

    previaBox.hidden = false;
    if (previaN) {
      previaN.textContent = num(lista.length) + (lista.length === 1 ? " coincidencia" : " coincidencias");
    }

    if (!lista.length) {
      previaLista.innerHTML =
        '<p class="previa-vacio">No hay coincidencias literales. Prueba una intención:</p>' +
        '<div class="previa-sugerencias">' +
          INTENCIONES.slice(0, 3).map(function (intent) {
            return '<button class="btn-mini" type="button" data-intencion="' +
              esc(intent.id) + '">' + esc(intent.nombre) + "</button>";
          }).join("") +
        "</div>";
      if (previaVer) previaVer.hidden = true;
      return;
    }

    previaLista.innerHTML = lista.slice(0, 3).map(function (it) {
      var href = esc(urlOk(it.u));
      return (
        '<a class="previa-item" href="' + href + '" target="_blank" rel="noopener">' +
          '<span class="previa-tipo">' + esc(it.tipo.nombre) + "</span>" +
          '<span class="previa-nombre">' + esc(it.n) + "</span>" +
          '<span class="previa-uso">' + esc(it.usos[0] ? it.usos[0].nombre : "") + "</span>" +
          '<span class="previa-flecha" aria-hidden="true">↗</span>' +
        "</a>"
      );
    }).join("");

    if (previaVer) {
      previaVer.hidden = false;
      previaVer.innerHTML = "Ver " + (lista.length === 1 ? "el resultado" : "los " + num(lista.length) + " resultados") +
        ' <span aria-hidden="true">↓</span>';
    }
  }

  function pintarIntenciones() {
    if (!intencionesBox) return;
    intencionesBox.innerHTML = INTENCIONES.map(function (intent) {
      var n = ITEMS.filter(function (it) {
        return coincideIntencion(it, intent);
      }).length;
      return (
        '<button class="intencion" type="button" data-intencion="' + esc(intent.id) +
        '" aria-label="Explorar ' + esc(intent.nombre) + ": " + num(n) + ' entradas">' +
          '<span class="intencion-head">' +
            '<span class="intencion-nombre">' + esc(intent.nombre) + "</span>" +
            '<span class="intencion-n">' + num(n) + "</span>" +
          "</span>" +
          '<span class="intencion-desc">' + esc(intent.descripcion) + "</span>" +
          '<span class="intencion-ejemplo">“' + esc(intent.consulta) + '” <span aria-hidden="true">→</span></span>' +
        "</button>"
      );
    }).join("");
  }

  function pintar() {
    var consultaActual = consulta();
    var base = porTexto(consultaActual);
    var baseTipo = porTipo(base, tipo);
    var baseUso = porUso(base, uso);
    var conteoTipos = contar(baseUso, "tipo");
    var conteoUsos = contar(baseTipo, "uso");

    var lista = porTipo(baseUso, tipo);
    if (consultaActual.tokens.length || consultaActual.intents.length) {
      lista = lista.slice().sort(function (a, b) {
        return rango(b, consultaActual) - rango(a, consultaActual) ||
          a.n.localeCompare(b.n, "es");
      });
    }

    pintarChips(conteoTipos, conteoUsos, baseUso.length, baseTipo.length);
    pintarTiles(conteoTipos, conteoUsos, baseUso.length, baseTipo.length);
    pintarResumen(consultaActual);
    pintarInterpretacion(consultaActual);
    pintarPrevia(lista);

    grid.innerHTML = lista.length
      ? lista.slice(0, limite).map(tarjeta).join("")
      : '<div class="vacio"><strong>Sin coincidencias.</strong>' +
        "<p>Describe la función con otras palabras o empieza por una intención.</p>" +
        '<div class="vacio-acciones">' +
          '<button class="btn-mini" type="button" data-intencion="web">Diseño web</button>' +
          '<button class="btn-mini" type="button" data-intencion="datos">Base de datos</button>' +
          '<button class="btn-mini" type="button" data-intencion="automatizacion">Automatizar</button>' +
          '<button class="btn-mini" type="button" data-limpiar data-limpiar-filtros>Limpiar búsqueda</button>' +
        "</div></div>";

    if (vivo) {
      vivo.textContent = q || tipo || uso
        ? num(lista.length) + " resultados"
        : num(C.total) + " entradas";
    }

    if (res) {
      res.textContent = lista.length
        ? "Mostrando " + Math.min(limite, lista.length) + " de " + num(lista.length) +
          " resultados · " + num(C.total) + " en el catálogo"
        : "0 resultados · " + num(C.total) + " en el catálogo";
    }
    if (more) more.hidden = lista.length <= limite;

    programarUrl();
  }

  function reiniciar() {
    limite = PASO;
    pintar();
  }

  function programarPintar() {
    if (frame) cancelAnimationFrame(frame);
    frame = requestAnimationFrame(function () {
      frame = 0;
      pintar();
    });
  }

  function programarUrl() {
    clearTimeout(urlTimer);
    urlTimer = setTimeout(function () {
      try {
        var params = new URLSearchParams();
        if (q) params.set("q", q);
        if (tipo) params.set("tipo", tipo);
        if (uso) params.set("uso", uso);
        var query = params.toString();
        history.replaceState(
          null,
          "",
          location.pathname + (query ? "?" + query : "") + location.hash
        );
      } catch (e) {
        return;
      }
    }, 250);
  }

  function leerUrl() {
    try {
      var params = new URLSearchParams(location.search);
      q = (params.get("q") || "").trim();
      tipo = params.get("tipo") || "";
      uso = params.get("uso") || "";
    } catch (e) {
      return;
    }
    if (!TIPOS.some(function (t) { return t.id === tipo; })) tipo = "";
    if (!USOS.some(function (u) { return u.id === uso; })) uso = "";
    if (input) input.value = q;
  }

  function irAlCatalogo() {
    if (catalogo) catalogo.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function aplicarIntencion(id) {
    var intent = intencionPorId(id);
    if (!intent) return;
    q = intent.consulta;
    tipo = "";
    uso = "";
    if (input) input.value = q;
    reiniciar();
    irAlCatalogo();
  }

  function aplicarSugerencia(texto) {
    q = texto;
    if (input) input.value = q;
    reiniciar();
    irAlCatalogo();
  }

  function limpiarTodo(devolverFoco) {
    q = "";
    tipo = "";
    uso = "";
    if (input) {
      input.value = "";
      if (devolverFoco) input.focus({ preventScroll: true });
    }
    reiniciar();
  }

  function cifras() {
    var valores = {
      "[data-total]": num(C.total),
      "[data-tipos-n]": TIPOS.filter(function (t) { return t.n; }).length,
      "[data-usos-n]": USOS.filter(function (u) { return u.n; }).length,
      "[data-fuentes-n]": FUENTES.length
    };
    Object.keys(valores).forEach(function (selector) {
      document.querySelectorAll(selector).forEach(function (el) {
        el.textContent = valores[selector];
      });
    });
    document.querySelectorAll("[data-fecha]").forEach(function (el) {
      el.textContent = C.actualizado || "";
    });
  }

  function enlazarChips(box, atributo, asignar) {
    if (!box) return;
    box.addEventListener("click", function (e) {
      var b = e.target.closest("[" + atributo + "]");
      if (!b || b.disabled) return;
      var id = b.getAttribute(atributo) || "";
      asignar(id);
      reiniciar();
      var nuevo = box.querySelector("[" + atributo + '="' + id + '"]');
      if (nuevo) nuevo.focus({ preventScroll: true });
    });
  }

  enlazarChips(tiposChips, "data-tipo", function (id) {
    tipo = tipo === id ? "" : id;
  });
  enlazarChips(usosChips, "data-uso", function (id) {
    uso = uso === id ? "" : id;
  });
  enlazarChips(tiposLista, "data-tipo-tile", function (id) {
    tipo = tipo === id ? "" : id;
    irAlCatalogo();
  });
  enlazarChips(usosLista, "data-uso-tile", function (id) {
    uso = uso === id ? "" : id;
    irAlCatalogo();
  });

  if (input) {
    input.addEventListener("input", function () {
      q = input.value.trim();
      limite = PASO;
      programarPintar();
    });
  }

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      reiniciar();
      irAlCatalogo();
    });
  }

  document.addEventListener("click", function (e) {
    var limpiar = e.target.closest("[data-limpiar]");
    if (limpiar) {
      limpiarTodo(!limpiar.hasAttribute("data-limpiar-filtros"));
      return;
    }

    var intencion = e.target.closest("[data-intencion]");
    if (intencion) {
      aplicarIntencion(intencion.getAttribute("data-intencion") || "");
      return;
    }

    var sugerencia = e.target.closest("[data-sugerencia]");
    if (sugerencia) {
      aplicarSugerencia(sugerencia.getAttribute("data-sugerencia") || "");
    }
  });

  if (previaVer) previaVer.addEventListener("click", irAlCatalogo);

  if (more) {
    more.addEventListener("click", function () {
      limite += PASO;
      pintar();
    });
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "/" && !/^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName)) {
      e.preventDefault();
      if (input) input.focus();
      return;
    }
    if (e.key === "Escape" && document.activeElement === input) {
      limpiarTodo(false);
    }
  });

  leerUrl();
  cifras();
  pintarIntenciones();
  pintar();
})();
