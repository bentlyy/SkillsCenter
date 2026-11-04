# Changelog

Todas las versiones notables de este proyecto se documentan aqui.

## [No publicado]

- Skill portable `skills/skill-finder/` para agentes: busqueda de skills y
  herramientas por texto literal y por concepto (14 intenciones con frases y
  sinonimos en espanol e ingles), flujo de frescura, verificacion de fichas y
  reglas para no inventar enlaces.
- Script `skills/skill-finder/scripts/skill_finder.py` sin dependencias: lee
  `landings/assets/catalogo.js`, el CSV exportado o SQLite en modo lectura, y
  explica si respondio por coincidencia literal o por intencion.
- Instalador `scripts/instalar-skill.ps1` para copiar la skill a Claude Code,
  Codex (`~/.agents/skills`) y opencode, con el catalogo offline incluido.
- Instalador multiplataforma `scripts/instalar_skill.py` (stdlib) con scope de
  usuario o de proyecto (`.claude/skills`, `.agents/skills`, `.opencode/skills`).
- Referencias de intenciones, taxonomia (tipo/uso/fuente/categoria) y contrato
  de herramientas MCP/CLI/script.

## [0.1.0] - 2026-11-03

Primera version funcional.

- Proyecto renombrado a SkillsCenter: paquete `skillscenter`, comando
  `skillscenter`, variables `SKILLSCENTER_*` y datos en `%LOCALAPPDATA%\skillscenter`.
- Catalogo SQLite con items, snapshots diarios, puntuaciones, secciones y aportes.
- Ocho fuentes: GitHub, registro MCP, awesome-lists, Hacker News, Reddit (OAuth),
  PyPI (RSS), npm y Hugging Face.
- Deduplicacion por `uid` y por URL canonica; los repos enlazados desde una
  awesome-list se fusionan con su entrada de GitHub.
- Clasificacion automatica en 15 secciones con reglas en espanol e ingles.
- Score de calor (popularidad + crecimiento + frescura + fuente) e historico de
  crecimiento a 7 y 30 dias.
- Servidor MCP con 9 herramientas.
- CLI: `init`, `sync`, `stats`, `fuentes`, `categorias`, `buscar`, `tendencias`,
  `digest`, `serve`.
- Informe diario en Markdown y scripts de tarea programada para Windows.
- Export completo del catalogo a Markdown y CSV.
- 25 landings estaticas de muestra (5 skills x 5 variantes) con datos reales,
  mas 5 indices por skill y una galeria raiz.
- Buscador compacto funcional (`ui-styling/04-compact.html`) sobre las 1.901
  entradas del catalogo: texto libre, dos ejes combinables (tipo y uso), conteos
  facetados, sugerencias, busqueda por intencion con fallback semantico, vista
  previa, URL compartible y enlaces a la fuente.
- Taxonomia de dos ejes en `facetas.py`: tipo (que es) y uso (para que sirve),
  con clasificacion automatica y tests dedicados.
- Export web ligero en `landings/assets/catalogo.js` (solo metadatos) y
  `buscador.js`, separado de la muestra de 70 entradas de las demas landings.
- Tests de scoring, deduplicacion, taxonomia, facetas, capa SQLite y pipeline.
