"""Genera 25 landings (5 skills x 5 estilos) y sus galerias."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "landings"

SKILLS = [
    {
        "id": "design",
        "clase": "design",
        "nombre": "design",
        "titulo": "Dirección de arte",
        "acento": "#b3400f",
        "desc": "Cinco direcciones visuales para el mismo catálogo: editorial, glass, brutalista, suizo y lujo.",
        "paginas": [
            {
                "slug": "01-editorial",
                "nombre": "Editorial",
                "kicker": "Skill Radar · Edición 01",
                "h1": "El catálogo de IA, <em>curado</em> como una revista.",
                "lede": "1.901 herramientas, modelos y servidores MCP. Sin ruido, con criterio editorial y datos reales de crecimiento.",
                "placeholder": "Busca una skill, un modelo, un servidor…",
                "lista": "Selección de la semana",
                "nota": "Una lectura curada de lo que está creciendo en el ecosistema.",
                "extra": "",
            },
            {
                "slug": "02-glass",
                "nombre": "Glass",
                "kicker": "Radar en vivo",
                "h1": "Todas las skills de IA.<br>Un solo lugar.",
                "lede": "Rastreamos GitHub, Hugging Face, npm, PyPI, el registro MCP y comunidades para que encuentres lo que importa antes de que se vuelva obvio.",
                "placeholder": "Buscar en 1.901 entradas…",
                "lista": "Lo más caliente ahora",
                "nota": "Ranking por popularidad, crecimiento y frescura.",
                "extra": "",
            },
            {
                "slug": "03-brutalist",
                "nombre": "Brutalist",
                "kicker": "Sin filtros",
                "h1": "SKILLS.<br>SIN RUIDO.",
                "lede": "Un catálogo directo: qué existe, cuánto crece y dónde encontrarlo. Sin tarjetas de marketing.",
                "placeholder": "Buscar…",
                "lista": "Datos duros",
                "nota": "1.901 entradas. 7 fuentes. Cero relleno.",
                "extra": "",
            },
            {
                "slug": "04-swiss",
                "nombre": "Swiss",
                "kicker": "Catálogo sistemático",
                "h1": "1.901 herramientas.<br>14 categorías.<br>Cero ruido.",
                "lede": "La información esencial de cada skill de IA, ordenada para decidir rápido.",
                "placeholder": "Buscar por nombre o categoría…",
                "lista": "Índice del ecosistema",
                "nota": "Orden, jerarquía y datos. Nada más.",
                "extra": "",
            },
            {
                "slug": "05-luxury",
                "nombre": "Luxury",
                "kicker": "Colección 2026",
                "h1": "La colección esencial de herramientas de IA.",
                "lede": "Una selección sobria de lo que merece formar parte de tu stack.",
                "placeholder": "Buscar en la colección…",
                "lista": "Piezas destacadas",
                "nota": "Curaduría mensual del ecosistema.",
                "extra": "",
            },
        ],
    },
    {
        "id": "ui-ux-pro-max",
        "clase": "pro",
        "nombre": "ui-ux-pro-max",
        "titulo": "Patrones de producto",
        "acento": "#4f46e5",
        "desc": "Cinco patrones de producto probados: SaaS, marketplace, herramienta de desarrollo, directorio y búsqueda con IA.",
        "paginas": [
            {
                "slug": "01-saas",
                "nombre": "SaaS",
                "kicker": "Plataforma",
                "h1": "El sistema operativo de tu stack de IA.",
                "lede": "Descubre, compara y adopta skills, modelos y servidores MCP con métricas reales de uso y crecimiento.",
                "placeholder": "Buscar skills, repos, modelos…",
                "lista": "Panorama del ecosistema",
                "nota": "Métricas de 7 fuentes, actualizadas a diario.",
                "extra": """<div class="mock" aria-hidden="true">
        <div class="mock-row"><span class="mock-dot"></span><span>Servidores MCP</span><span>200</span></div>
        <div class="mock-row"><span class="mock-dot"></span><span>Repos GitHub</span><span>428</span></div>
        <div class="mock-row"><span class="mock-dot"></span><span>Modelos Hugging Face</span><span>535</span></div>
        <div class="mock-row"><span class="mock-dot"></span><span>Paquetes npm</span><span>383</span></div>
      </div>""",
            },
            {
                "slug": "02-marketplace",
                "nombre": "Marketplace",
                "kicker": "Marketplace",
                "h1": "Encuentra la skill exacta que necesitas.",
                "lede": "Filtra por categoría, fuente o tracción. Compara opciones y llévate la que encaja.",
                "placeholder": "¿Qué quieres construir?",
                "lista": "Ofertas destacadas",
                "nota": "Explora por categoría y guarda tus favoritas.",
                "extra": "",
            },
            {
                "slug": "03-devtool",
                "nombre": "Devtool",
                "kicker": "developer-first",
                "h1": "Todo lo que tu agente necesita, indexado.",
                "lede": "Un radar que habla tu idioma: repos, paquetes, modelos y servidores MCP con datos verificables.",
                "placeholder": "grep skills…",
                "lista": "Resultados recientes",
                "nota": "Salida limpia para humanos y agentes.",
                "extra": """<div class="terminal" aria-hidden="true">
        <div class="terminal-bar"><i></i><i></i><i></i></div>
        <pre>$ skill-radar sync
<span class="ok">✓</span> 7 fuentes indexadas
<span class="ok">✓</span> 1.901 entradas únicas
<span class="ok">✓</span> scores calculados · 03/11/2026</pre>
      </div>""",
            },
            {
                "slug": "04-directory",
                "nombre": "Directory",
                "kicker": "Directorio",
                "h1": "El directorio definitivo de skills de IA.",
                "lede": "1.901 entradas verificadas, ordenadas y listas para explorar. Sin duplicados, sin ruido.",
                "placeholder": "Buscar en el directorio…",
                "lista": "Listado completo",
                "nota": "Vista compacta para comparar rápido.",
                "extra": "",
            },
            {
                "slug": "05-ai-search",
                "nombre": "AI Search",
                "kicker": "Búsqueda semántica",
                "h1": "Pregunta. Encuentra. Construye.",
                "lede": "Describe lo que necesitas y el radar te muestra las herramientas con más tracción del ecosistema.",
                "placeholder": "Ej. servidor MCP para bases de datos",
                "lista": "Recomendado para ti",
                "nota": "Resultados según popularidad, crecimiento y frescura.",
                "extra": "",
            },
        ],
    },
    {
        "id": "ui-styling",
        "clase": "ui",
        "nombre": "ui-styling",
        "titulo": "shadcn / Tailwind",
        "acento": "#0a84ff",
        "desc": "Cinco variantes del mismo sistema limpio: light, dark, aireado, compacto y degradado.",
        "paginas": [
            {
                "slug": "01-light",
                "nombre": "Light",
                "kicker": "Catálogo abierto",
                "h1": "Skills de IA, listas para usar.",
                "lede": "Un directorio limpio y verificable de herramientas, modelos y servidores MCP.",
                "placeholder": "Buscar…",
                "lista": "Explorar el catálogo",
                "nota": "Filtra por categoría y encuentra tu próxima herramienta.",
                "extra": "",
            },
            {
                "slug": "02-dark",
                "nombre": "Dark",
                "kicker": "Radar",
                "h1": "Tu radar de herramientas de IA.",
                "lede": "Métricas diarias de las fuentes que importan. Todo en un solo panel.",
                "placeholder": "Buscar…",
                "lista": "Tendencias",
                "nota": "Lo que más crece en las últimas 24 horas.",
                "extra": "",
            },
            {
                "slug": "03-airy",
                "nombre": "Airy",
                "kicker": "Comunidad",
                "h1": "Descubre lo que la comunidad está construyendo.",
                "lede": "Repos, modelos y skills con tracción real, seleccionados para que no pierdas tiempo.",
                "placeholder": "Buscar una herramienta…",
                "lista": "Nuevo y relevante",
                "nota": "Una mirada fresca cada día.",
                "extra": "",
            },
            {
                "slug": "04-compact",
                "nombre": "Compact",
                "kicker": "Modo denso",
                "h1": "1.901 skills. Filtra en segundos.",
                "lede": "Toda la información en tarjetas compactas: fuente, métricas, categoría y enlace.",
                "placeholder": "Filtrar…",
                "lista": "Catálogo",
                "nota": "Densidad para usuarios avanzados.",
                "extra": "",
            },
            {
                "slug": "05-gradient",
                "nombre": "Gradient",
                "kicker": "En tiempo real",
                "h1": "El radar de la IA, en tiempo real.",
                "lede": "Sigue el pulso de GitHub, Hugging Face, npm y el registro MCP desde un solo lugar.",
                "placeholder": "Buscar en el radar…",
                "lista": "Ahora mismo",
                "nota": "Actualizado hoy a las 08:00.",
                "extra": "",
            },
        ],
    },
    {
        "id": "design-system",
        "clase": "ds",
        "nombre": "design-system",
        "titulo": "Sistemas y tokens",
        "acento": "#0ea5e9",
        "desc": "Cinco formas de demostrar un sistema: retícula, monocromo, bento, especimen tipográfico y tokens.",
        "paginas": [
            {
                "slug": "01-grid",
                "nombre": "Grid",
                "kicker": "Sistema 01",
                "h1": "Un catálogo.<br>Un sistema.",
                "lede": "Cada entrada respeta la misma retícula, jerarquía y escala tipográfica.",
                "placeholder": "Buscar…",
                "lista": "Retícula del catálogo",
                "nota": "Consistencia antes que decoración.",
                "extra": "",
            },
            {
                "slug": "02-monochrome",
                "nombre": "Monochrome",
                "kicker": "Datos",
                "h1": "Datos, no decoración.",
                "lede": "Sin color innecesario: nombre, fuente, métricas y categoría. Lo que necesitas para decidir.",
                "placeholder": "Buscar…",
                "lista": "Registro",
                "nota": "Escala tipográfica y contraste.",
                "extra": "",
            },
            {
                "slug": "03-bento",
                "nombre": "Bento",
                "kicker": "Vista general",
                "h1": "Todo el ecosistema, en una vista.",
                "lede": "Un tablero modular con las señales que importan: popularidad, crecimiento y frescura.",
                "placeholder": "Buscar…",
                "lista": "Módulos destacados",
                "nota": "Cada bloque, una señal.",
                "extra": "",
            },
            {
                "slug": "04-type",
                "nombre": "Typographic",
                "kicker": "Especimen",
                "h1": "Las herramientas hablan por sí solas.",
                "lede": "Tipografía grande, datos precisos y espacio para leer. El catálogo como texto.",
                "placeholder": "Buscar…",
                "lista": "Índice tipográfico",
                "nota": "Jerarquía editorial aplicada al catálogo.",
                "extra": "",
            },
            {
                "slug": "05-tokens",
                "nombre": "Tokens",
                "kicker": "Design tokens",
                "h1": "Diseñado para escalar.",
                "lede": "Colores, espacios y tipos definidos como tokens. La misma base para web, app y agentes.",
                "placeholder": "Buscar…",
                "lista": "Componentes del sistema",
                "nota": "Cada tarjeta usa los mismos tokens.",
                "extra": """<div class="swatches" aria-hidden="true">
        <span class="swatch" style="background:#e0f2fe">sky-100</span>
        <span class="swatch" style="background:#0ea5e9;color:#fff">sky-500</span>
        <span class="swatch" style="background:#6366f1;color:#fff">indigo</span>
        <span class="swatch" style="background:#f97316;color:#fff">orange</span>
        <span class="swatch" style="background:#10b981;color:#fff">emerald</span>
        <span class="swatch" style="background:#0f172a;color:#fff">slate-900</span>
      </div>""",
            },
        ],
    },
    {
        "id": "brand",
        "clase": "br",
        "nombre": "brand",
        "titulo": "Identidad y marca",
        "acento": "#ff4d00",
        "desc": "Cinco expresiones de marca: wordmark, manifiesto, historia de color, geometría y comunidad.",
        "paginas": [
            {
                "slug": "01-wordmark",
                "nombre": "Wordmark",
                "kicker": "Identidad",
                "h1": "skill<span>radar</span>",
                "lede": "El pulso del ecosistema de IA: 1.901 herramientas, modelos y servidores en un solo lugar.",
                "placeholder": "Buscar…",
                "lista": "La marca en acción",
                "nota": "Un sistema de identidad simple y reconocible.",
                "extra": "",
            },
            {
                "slug": "02-manifesto",
                "nombre": "Manifesto",
                "kicker": "Manifiesto",
                "h1": "Creemos en las herramientas que la gente elige.",
                "lede": "No rankeamos por marketing. Rankeamos por uso, crecimiento y lo que la comunidad construye.",
                "placeholder": "Buscar…",
                "lista": "Lo que la comunidad elige",
                "nota": "Datos abiertos, criterio claro.",
                "extra": "",
            },
            {
                "slug": "03-color",
                "nombre": "Color story",
                "kicker": "Color",
                "h1": "Un catálogo con carácter.",
                "lede": "Una paleta cálida para un ecosistema que no para de moverse.",
                "placeholder": "Buscar…",
                "lista": "Explora por categoría",
                "nota": "Cada categoría, un acento.",
                "extra": """<div class="blocks" aria-hidden="true">
        <span style="background:#ff6b35"></span><span style="background:#ffd6a5"></span>
        <span style="background:#cdeac0"></span><span style="background:#ffadad"></span>
        <span style="background:#241a12"></span>
      </div>""",
            },
            {
                "slug": "04-geometric",
                "nombre": "Geometric",
                "kicker": "Señal",
                "h1": "Señales claras en un ruido infinito.",
                "lede": "Filtramos el ruido del ecosistema y mostramos solo lo que tiene tracción real.",
                "placeholder": "Buscar…",
                "lista": "Señales detectadas",
                "nota": "Formas simples, información precisa.",
                "extra": "",
            },
            {
                "slug": "05-community",
                "nombre": "Community",
                "kicker": "Comunidad",
                "h1": "Hecho por y para quienes construyen.",
                "lede": "Un catálogo abierto, alimentado por fuentes públicas y por los aportes de la comunidad.",
                "placeholder": "Buscar…",
                "lista": "Lo que están usando",
                "nota": "Abre un PR o envía tu skill.",
                "extra": """<blockquote class="quote">“Encontré tres servidores MCP que no sabía que necesitaba. Ahora son parte de mi stack diario.”
        <footer>— Ana R., desarrolladora</footer></blockquote>""",
            },
        ],
    },
]


def pagina(skill, p, v):
    extra = p["extra"]
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{p["nombre"]} · Skill Radar — {skill["nombre"]}</title>
  <meta name="description" content="{p["lede"]}">
  <link rel="stylesheet" href="../assets/base.css">
  <link rel="stylesheet" href="style.css">
</head>
<body class="{skill["clase"]} v{v}">
  <a class="skip" href="#catalogo">Saltar al catálogo</a>

  <header class="nav wrap">
    <a class="logo" href="../index.html" aria-label="Volver a la galería">
      <span class="logo-dot" aria-hidden="true"></span>
      <span class="logo-text">skill<b>radar</b></span>
    </a>
    <nav class="nav-links" aria-label="Principal">
      <a href="#catalogo">Catálogo</a>
      <a href="#categorias">Categorías</a>
      <a href="#fuentes">Fuentes</a>
    </nav>
    <a class="nav-cta" href="#catalogo">Explorar <span aria-hidden="true">→</span></a>
  </header>

  <main>
    <section class="hero wrap">
      <p class="kicker">{p["kicker"]}</p>
      <h1>{p["h1"]}</h1>
      <p class="lede">{p["lede"]}</p>
      <form class="search" role="search" onsubmit="return false">
        <input data-buscar type="search" placeholder="{p["placeholder"]}" aria-label="Buscar en el catálogo">
        <button type="submit">Buscar</button>
      </form>
      <div class="hero-actions">
        <a class="btn" href="#catalogo">Ver catálogo</a>
        <a class="btn ghost" href="#fuentes">Cómo funciona</a>
      </div>
      {extra}
    </section>

    <section class="stats wrap" id="fuentes" aria-label="Cifras del catálogo">
      <div class="stat"><strong data-total>1.901</strong><span>entradas</span></div>
      <div class="stat"><strong data-fuentes>7</strong><span>fuentes</span></div>
      <div class="stat"><strong data-categorias>14</strong><span>categorías</span></div>
      <div class="stat"><strong data-nuevos>+1.901</strong><span>nuevas hoy</span></div>
    </section>

    <section class="catalogo wrap" id="catalogo">
      <div class="section-head">
        <div>
          <p class="eyebrow">Catálogo vivo</p>
          <h2>{p["lista"]}</h2>
        </div>
        <p class="section-note">{p["nota"]}</p>
      </div>
      <div class="chips" data-chips aria-label="Filtrar por categoría"></div>
      <div class="grid" data-items="9"></div>
      <div class="lista-pie">
        <p class="resultado" data-resultado aria-live="polite"></p>
        <button class="btn ghost" type="button" data-vermas>Ver más</button>
      </div>
    </section>

    <section class="banda wrap" id="categorias">
      <div class="section-head">
        <div>
          <p class="eyebrow">Secciones</p>
          <h2>Explora por categoría</h2>
        </div>
      </div>
      <div class="cats-grid" data-cats-lista></div>
    </section>

    <section class="cta wrap">
      <div>
        <p class="eyebrow">Aporta</p>
        <h2>¿Construiste algo con IA?</h2>
        <p class="section-note">Añade tu skill, modelo o servidor MCP al radar. La comunidad decide con datos, no con marketing.</p>
      </div>
      <div class="actions">
        <a class="btn" href="#catalogo">Explorar catálogo</a>
        <a class="btn ghost" href="../index.html">Ver las 25 landings</a>
      </div>
    </section>
  </main>

  <footer class="footer wrap">
    <p><strong>skillradar</strong> · Catálogo abierto de herramientas de IA</p>
    <nav aria-label="Pie">
      <a href="#catalogo">Catálogo</a>
      <a href="#categorias">Categorías</a>
      <a href="#fuentes">Fuentes</a>
      <a href="../index.html">Galería</a>
    </nav>
    <p>Datos al <span data-fecha>2026-11-03</span> · 7 fuentes · 1.901 entradas</p>
  </footer>

  <script src="../assets/datos.js"></script>
  <script src="../assets/app.js"></script>
</body>
</html>
"""


def pagina_compacta(skill, p, v):
    return """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Buscador compacto · Skill Radar</title>
  <meta name="description" content="Busca 1.901 entradas de IA por función, nombre, tipo o uso. Describe lo que necesitas y el radar interpreta la intención en tiempo real.">
  <link rel="stylesheet" href="../assets/base.css">
  <link rel="stylesheet" href="style.css">
  <link rel="stylesheet" href="../assets/compacto.css">
</head>
<body class="ui v4">
  <a class="skip" href="#catalogo">Saltar al catálogo</a>

  <header class="nav wrap">
    <a class="logo" href="../index.html" aria-label="Volver a la galería">
      <span class="logo-dot" aria-hidden="true"></span>
      <span class="logo-text">skill<b>radar</b></span>
    </a>
    <nav class="nav-links" aria-label="Principal">
      <a href="#catalogo">Catálogo</a>
      <a href="#necesidades">Necesidades</a>
      <a href="#tipos">Tipos</a>
      <a href="#usos">Usos</a>
      <a href="#fuentes">Fuentes</a>
    </nav>
    <a class="nav-cta" href="#catalogo">Explorar <span aria-hidden="true">→</span></a>
  </header>

  <main>
    <section class="hero wrap">
      <p class="kicker">Buscador compacto</p>
      <h1><span data-total>1.901</span> entradas.<br>Encuentra la que sirve.</h1>
      <p class="lede">Describe lo que necesitas, aunque no sepas el nombre. El radar traduce la función a tipos, usos y tecnologías, y actualiza los resultados mientras escribes.</p>
      <div class="buscador-panel">
        <div class="buscador-barra">
          <span class="live"><i aria-hidden="true"></i> Búsqueda en vivo</span>
          <span class="live-cuenta" data-resultado-vivo aria-hidden="true">1.901 entradas</span>
          <span class="buscador-ayuda" id="ayuda-buscador">Escribe una necesidad, no solo un nombre.</span>
        </div>
        <form class="search" role="search" data-buscador onsubmit="return false">
          <div class="buscador-campo">
            <svg class="buscador-icono" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="m20 20-3.5-3.5"></path></svg>
            <input data-buscar type="search" placeholder="Ej.: diseño de páginas web, base de datos, automatizar tareas…" aria-label="Buscar en el catálogo por función o nombre" aria-describedby="ayuda-buscador" autocomplete="off" spellcheck="false" enterkeyhint="search">
          </div>
          <button type="button" data-limpiar>Limpiar</button>
        </form>
        <div class="interpretacion" data-interpretacion hidden>
          <span class="interpretacion-label">Entendemos</span>
          <div class="chips" data-intenciones-chips></div>
        </div>
        <div class="vista-previa" data-previa hidden aria-label="Vista previa de resultados">
          <div class="vista-previa-head">
            <span>Coincidencias en vivo</span>
            <span data-previa-n></span>
          </div>
          <div class="vista-previa-lista" data-previa-lista></div>
          <button class="btn-mini" type="button" data-ver-resultados>Ver todos los resultados <span aria-hidden="true">↓</span></button>
        </div>
        <p class="sugerencias">Prueba:
          <button type="button" data-sugerencia="diseño de páginas web">diseño de páginas web</button>
          <button type="button" data-sugerencia="base de datos">base de datos</button>
          <button type="button" data-sugerencia="automatizar tareas">automatizar tareas</button>
          <button type="button" data-sugerencia="crear prompts">crear prompts</button>
          <button type="button" data-sugerencia="rag">RAG</button>
        </p>
      </div>
      <div class="hero-actions">
        <a class="btn" href="#catalogo">Ver catálogo</a>
        <a class="btn ghost" href="#necesidades">Explorar por necesidad</a>
      </div>
    </section>

    <section class="stats wrap" id="fuentes" aria-label="Cifras del catálogo">
      <div class="stat"><strong data-total>1.901</strong><span>entradas</span></div>
      <div class="stat"><strong data-tipos-n>9</strong><span>tipos</span></div>
      <div class="stat"><strong data-usos-n>14</strong><span>usos</span></div>
      <div class="stat"><strong data-fuentes-n>7</strong><span>fuentes</span></div>
    </section>

    <section class="necesidades wrap" id="necesidades">
      <div class="section-head">
        <div>
          <p class="eyebrow">Si no sabes el nombre</p>
          <h2>Empieza por lo que necesitas.</h2>
        </div>
        <p class="section-note">Elige una intención y el buscador la convierte en una consulta con tipos, usos y tecnologías afines.</p>
      </div>
      <div class="intenciones-grid" data-intenciones></div>
    </section>

    <section class="catalogo wrap" id="catalogo">
      <div class="section-head">
        <div>
          <p class="eyebrow">Catálogo completo</p>
          <h2>Filtra por lo que es y por lo que hace.</h2>
        </div>
        <div class="section-acciones">
          <p class="section-note" data-filtro-resumen>Sin filtros · ordenado por puntuación</p>
          <button class="btn-mini" type="button" data-limpiar data-limpiar-filtros hidden>Limpiar filtros</button>
        </div>
      </div>

      <div class="filtros">
        <div class="filtro-grupo">
          <span class="filtro-label">Tipo</span>
          <div class="chips" data-tipos-chips aria-label="Filtrar por tipo"></div>
        </div>
        <div class="filtro-grupo">
          <span class="filtro-label">Uso</span>
          <div class="chips" data-usos-chips aria-label="Filtrar por uso"></div>
        </div>
      </div>

      <div class="grid" data-items="24"></div>
      <div class="lista-pie">
        <p class="resultado" data-resultado aria-live="polite"></p>
        <button class="btn ghost" type="button" data-vermas>Ver más</button>
      </div>
    </section>

    <section class="facetas wrap" id="tipos">
      <div class="section-head">
        <div>
          <p class="eyebrow">Dos ejes, mismo nivel</p>
          <h2>Explora por tipo o por uso</h2>
        </div>
        <p class="section-note">El tipo dice qué es. El uso dice para qué sirve. Puedes combinarlos: un agente también puede servir para código.</p>
      </div>
      <div class="facetas-grid">
        <div class="facet-col">
          <h3>Por tipo</h3>
          <p>Qué es</p>
          <div class="facet-tiles" data-tipos-lista></div>
        </div>
        <div class="facet-col" id="usos">
          <h3>Por uso</h3>
          <p>Para qué sirve</p>
          <div class="facet-tiles" data-usos-lista></div>
        </div>
      </div>
    </section>

    <section class="cta wrap">
      <div>
        <p class="eyebrow">Aporta</p>
        <h2>¿Construiste algo con IA?</h2>
        <p class="section-note">Añade tu skill, modelo o servidor MCP al radar. La comunidad decide con datos, no con marketing.</p>
      </div>
      <div class="actions">
        <a class="btn" href="#catalogo">Explorar catálogo</a>
        <a class="btn ghost" href="../index.html">Ver las 25 landings</a>
      </div>
    </section>
  </main>

  <footer class="footer wrap">
    <p><strong>skillradar</strong> · Catálogo abierto de herramientas de IA</p>
    <nav aria-label="Pie">
      <a href="#catalogo">Catálogo</a>
      <a href="#necesidades">Necesidades</a>
      <a href="#tipos">Tipos</a>
      <a href="#usos">Usos</a>
      <a href="../index.html">Galería</a>
    </nav>
    <p>Datos al <span data-fecha>2026-11-03</span> · <span data-total>1.901</span> entradas · <span data-tipos-n>9</span> tipos · <span data-usos-n>14</span> usos · <span data-fuentes-n>7</span> fuentes</p>
    <p>Solo metadatos y enlaces; el contenido vive en su fuente.</p>
  </footer>

  <script src="../assets/catalogo.js"></script>
  <script src="../assets/buscador.js"></script>
</body>
</html>
"""


def tarjeta(skill, p, v, prefijo=""):
    url = f"{prefijo}{p['slug']}.html"
    funcional = p["slug"] == "04-compact"
    etiqueta = f"0{v} · Buscador" if funcional else f"0{v}"
    accion = "Abrir buscador →" if funcional else "Abrir landing →"
    return f"""      <article class="card">
        <a class="frame" href="{url}" aria-label="Abrir {p["nombre"]}">
          <iframe src="{url}" title="Vista previa de {p["nombre"]}" loading="lazy"></iframe>
        </a>
        <div class="card-info"><h3>{p["nombre"]}</h3><span>{etiqueta}</span></div>
        <a class="card-link" href="{url}">{accion}</a>
      </article>"""


def cabecera_galeria(volver, kicker, titulo, lede, pills):
    return f"""  <header class="top wrap">
    <a class="back" href="{volver}">← Volver</a>
    <span class="brand"><i aria-hidden="true"></i> skillradar · landings</span>
  </header>

  <section class="hero wrap">
    <p class="kicker">{kicker}</p>
    <h1>{titulo}</h1>
    <p class="lede">{lede}</p>
    <div class="meta-row">{pills}</div>
  </section>
"""


def indice_skill(skill):
    tarjetas = []
    for v, p in enumerate(skill["paginas"], 1):
        tarjetas.append(tarjeta(skill, p, v))
    contenido = cabecera_galeria(
        "../index.html",
        skill["nombre"],
        skill["titulo"],
        skill["desc"],
        '<span class="pill"><b>5</b> variantes</span>'
        '<span class="pill"><b>70</b> entradas reales</span>'
        '<span class="pill"><b>1.901</b> en el catálogo</span>',
    )
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{skill["nombre"]} · Landings — Skill Radar</title>
  <link rel="stylesheet" href="../assets/galeria.css">
</head>
<body style="--accent:{skill["acento"]}">
{contenido}
  <main class="wrap">
    <div class="grid">
{chr(10).join(tarjetas)}
    </div>
  </main>

  <footer class="footer wrap">
    <span>Skill Radar · {skill["nombre"]}</span>
    <span>Generado desde el catálogo local · 2026</span>
  </footer>
</body>
</html>
"""


def indice_raiz():
    bloques = []
    for skill in SKILLS:
        tarjetas = []
        for v, p in enumerate(skill["paginas"], 1):
            tarjetas.append(tarjeta(skill, p, v, skill["id"] + "/"))
        bloques.append(
            f"""    <section class="skill-block" style="--accent:{skill["acento"]}">
      <div class="skill-head">
        <div>
          <p class="tag">{skill["nombre"]}</p>
          <h2>{skill["titulo"]}</h2>
        </div>
        <p>{skill["desc"]} <a class="card-link" href="{skill["id"]}/index.html">Ver colección →</a></p>
      </div>
      <div class="grid">
{chr(10).join(tarjetas)}
      </div>
    </section>"""
        )
    contenido = cabecera_galeria(
        "index.html",
        "Galería de estilos",
        "25 landings. 5 sistemas. Un catálogo.",
        "Cinco skills de diseño, cinco variantes cada una. Todas usan las mismas 70 entradas reales del catálogo: cambia el estilo, no los datos.",
        '<span class="pill"><b>25</b> páginas</span>'
        '<span class="pill"><b>5</b> skills</span>'
        '<span class="pill"><b>70</b> entradas reales</span>'
        '<span class="pill"><b>1.901</b> catálogo</span>',
    )
    contenido = contenido.replace("← Volver", "⟳ Actualizar")
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Landings · Skill Radar</title>
  <meta name="description" content="25 landings en 5 sistemas de diseño para el catálogo Skill Radar.">
  <link rel="stylesheet" href="assets/galeria.css">
</head>
<body>
{contenido}
  <main class="wrap">
{chr(10).join(bloques)}
  </main>

  <footer class="footer wrap">
    <span>Skill Radar · landings estáticas con datos reales</span>
    <span>31 páginas HTML · sin frameworks ni dependencias</span>
  </footer>
</body>
</html>
"""


def main():
    SALIDA.mkdir(exist_ok=True)
    total = 0
    for skill in SKILLS:
        carpeta = SALIDA / skill["id"]
        carpeta.mkdir(exist_ok=True)
        for v, p in enumerate(skill["paginas"], 1):
            destino = carpeta / f"{p['slug']}.html"
            funcional = skill["id"] == "ui-styling" and p["slug"] == "04-compact"
            html = pagina_compacta(skill, p, v) if funcional else pagina(skill, p, v)
            destino.write_text(html, encoding="utf-8")
            total += 1
        (carpeta / "index.html").write_text(indice_skill(skill), encoding="utf-8")
    (SALIDA / "index.html").write_text(indice_raiz(), encoding="utf-8")
    print(f"{total} landings + {len(SKILLS)} índices + 1 galería -> {SALIDA}")


if __name__ == "__main__":
    main()
