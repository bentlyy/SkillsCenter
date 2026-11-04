# SkillsCenter

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io)

> Motor de descubrimiento de **skills y herramientas de IA**: rastrea GitHub,
> Reddit, Hacker News, el registro MCP, awesome-lists y registros de paquetes,
> normaliza todo en un catalogo SQLite y lo expone por **MCP** para que una IA
> busque y detecte tendencias con datos reales, no inventados.

## Por que existe

Cada semana aparece un framework de agentes, un servidor MCP, una skill de Claude
o un modelo nuevo. Buscarlo a mano en GitHub, Reddit, Hacker News y npm no escala,
y una IA sin acceso a datos frescos tiende a recomendar lo mismo de siempre o a
inventarse enlaces.

SkillsCenter resuelve tres cosas:

1. **Recolecta** de fuentes publicas con APIs estables (no scraping fragil).
2. **Normaliza y deduplica**: un repositorio de GitHub enlazado desde tres
   awesome-lists es una sola entrada en el catalogo.
3. **Puntua y guarda historico**: snapshots diarios de estrellas, descargas y
   puntos, para calcular crecimiento real en 7 y 30 dias.

El objetivo final es una **pagina web con secciones** donde cualquiera pueda
explorar el catalogo y aportar entradas. Esta primera version deja la base de
datos y el motor listos; la web se construye encima sin migrar el esquema
(la tabla `aportes` ya existe).

## Como funciona

```
 fuentes publicas              motor                      consumidores
┌──────────────────┐   ┌────────────────────┐   ┌────────────────────┐
│ GitHub           │   │                    │   │ Servidor MCP       │
│ Registro MCP     │──▶│  normalizar        │──▶│ (buscar, tendencias│
│ awesome-lists    │   │  deduplicar        │   │  ficha, sincronizar)│
│ Hacker News      │   │  clasificar        │   ├────────────────────┤
│ Reddit (OAuth)   │   │  puntuar + snapshot│   │ CLI + informe .md  │
│ PyPI / npm       │   │                    │   ├────────────────────┤
│ Hugging Face     │   └─────────┬──────────┘   │ Web (siguiente)    │
└──────────────────┘             ▼              └────────────────────┘
                             SQLite (radar.db)
```

## Fuentes

| Fuente | Que aporta | Credenciales |
|--------|-----------|--------------|
| **GitHub** | Repos por topic (`mcp`, `ai-agents`, `rag`...), estrellas, forks, lenguaje, licencia | `GITHUB_TOKEN` opcional (muy recomendado) |
| **Registro MCP** | Servidores publicados en el registro oficial | Ninguna |
| **Listas curadas** | `awesome-mcp-servers`, `awesome-ai-agents`, `awesome-claude-skills`, `anthropics/skills` | Ninguna |
| **Hacker News** | Lanzamientos y discusion (API de Algolia) | Ninguna |
| **Reddit** | Posts de `r/LocalLLaMA`, `r/mcp`, `r/AIAgents`... | `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` |
| **PyPI** | Paquetes Python nuevos/actualizados (RSS) filtrados por palabras clave | Ninguna |
| **npm** | Paquetes por `keywords:mcp`, `keywords:ai-agent`... | Ninguna |
| **Hugging Face** | Modelos por descargas, likes y novedad | Ninguna |

Reddit bloquea el JSON publico sin autenticacion. Crea una app tipo **script** en
<https://www.reddit.com/prefs/apps> y exporta las dos variables; si no existen,
la fuente se omite con un aviso en lugar de fallar.

GitHub sin token permite 10 busquedas por minuto; el motor espacia las consultas.
Con token sube a 30/min y 5.000 peticiones/hora.

## Instalacion

```bash
pip install -e .
```

Dependencias: `httpx` y `mcp`. Sin pandas, sin navegador, sin base de datos externa.

Si el comando `skillscenter` no queda en el PATH, usa `python -m skillscenter ...`
(ambos son equivalentes).

## Configuracion

| Variable | Para que | Por defecto |
|----------|----------|-------------|
| `SKILLSCENTER_DB` | Ruta del archivo SQLite | `%LOCALAPPDATA%\skillscenter\radar.db` |
| `SKILLSCENTER_DIR` | Directorio de datos | igual que arriba |
| `GITHUB_TOKEN` / `GH_TOKEN` | Eleva el limite de la API de GitHub | sin token |
| `REDDIT_CLIENT_ID` | Activa la fuente Reddit | desactivada |
| `REDDIT_CLIENT_SECRET` | Activa la fuente Reddit | desactivada |
| `SKILLSCENTER_SUBREDDITS` | Lista de subreddits separada por comas | 8 por defecto |
| `SKILLSCENTER_UA` | User-Agent de las peticiones | `skillscenter/0.1` |

La base vive fuera del repositorio a proposito: **SQLite sobre OneDrive puede
corromperse** con los archivos WAL. Si quieres moverla, apunta `SKILLSCENTER_DB`
a una carpeta local.

## Uso

```bash
skillscenter init                      # crea la base y siembra secciones
skillscenter sync                      # rastrea todas las fuentes
skillscenter sync --fuente github --limite 30
skillscenter stats                     # totales por fuente/tipo/seccion
skillscenter fuentes                   # estado y ultimo error de cada fuente
skillscenter buscar "mcp servidor" --categoria mcp --limite 10
skillscenter tendencias --periodo 7d --orden crecimiento
skillscenter digest --dias 1 --salida informes/hoy.md
skillscenter serve                     # servidor MCP por stdio
```

## Servidor MCP

Con el paquete instalado, el servidor se arranca con `skillscenter serve` (o
`python -m skillscenter serve`). Ejemplo de configuracion para opencode:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "skillscenter": {
      "type": "local",
      "command": ["skillscenter", "serve"],
      "enabled": true,
      "environment": {
        "GITHUB_TOKEN": "ghp_..."
      }
    }
  }
}
```

Herramientas expuestas:

| Herramienta | Para que |
|-------------|----------|
| `buscar` | Texto libre + filtros por seccion, fuente, tipo y orden |
| `tendencias` | Lo mas caliente o lo que mas crece en 24h/7d/30d/90d |
| `novedades` | Entradas vistas por primera vez en los ultimos dias |
| `ficha` | Detalle por slug/uid/url con historico de metricas y puntuaciones |
| `categorias` | Secciones del catalogo con conteos |
| `fuentes` | Estado, ultima ejecucion y errores por fuente |
| `estadisticas` | Totales por fuente, tipo y seccion |
| `sincronizar` | Dispara el rastreo ahora |
| `digest` | Informe Markdown listo para leer |

## Puntuacion

El "calor" mezcla cuatro senales en una escala 0-100:

```
score = 100 * (0.45*popularidad + 0.30*crecimiento + 0.15*frescura + 0.10*fuente)
```

- **Popularidad**: `log10(metrica + 1)` normalizado a 1M (estrellas, descargas o puntos).
- **Crecimiento**: variacion frente al snapshot de hace 7 dias, mapeada de -25%..+125%.
- **Frescura**: decaimiento exponencial con vida media de 90 dias.
- **Fuente**: GitHub y el registro MCP pesan algo mas que un post suelto.

El crecimiento no se inventa: si no hay snapshot de hace 7 dias, se usa un valor
neutro. Por eso el radar mejora cuanto mas tiempo lleve corriendo.

## Rastreo diario en Windows

```powershell
# ejecuta sync + digest diario
.\scripts\radar-diario.ps1

# registra la tarea programada a las 08:00
.\scripts\instalar-tarea.ps1
```

Los informes quedan en `informes/` (ignorado por git).

## Esquema de datos

| Tabla | Contenido |
|-------|-----------|
| `items` | Catalogo unico: `uid`, `slug`, `fuente`, `tipo`, `topics`, `metricas` (JSON) |
| `snapshots` | Metricas por item y dia (crecimiento real) |
| `puntuaciones` | Score y crecimiento 7d/30d por item y dia |
| `categorias` + `item_categorias` | Secciones de la web (muchos a muchos) |
| `fuentes` | Estado del rastreo por fuente |
| `aportes` | Entradas propuestas por usuarios (pendiente/aprobado/rechazado) |
| `eventos` | Log de ejecuciones y errores |
| `items_fts` | Indice de texto completo sin acentos para busqueda |

`uid` es la clave estable (`github:owner/repo`, `mcp:nombre`, `npm:paquete`...) y
`slug` es la URL legible que usara la web.

## Landings de muestra

`landings/` contiene **25 prototipos estaticos** (5 skills de diseno x 5 variantes)
para elegir la direccion visual de la web. La mayoria usa una muestra de 70
entradas reales; **`ui-styling/04-compact.html` es el buscador funcional** sobre
las 1.901 entradas del catalogo (`assets/catalogo.js`). Filtra por dos ejes
independientes y combinables: **tipo** (que es) y **uso** (para que sirve).
Todo funciona sin internet, sin frameworks y sin fuentes externas.

El buscador incluye texto libre con acentos y prefijos, busqueda por intencion
en lenguaje natural (por ejemplo, "diseno de paginas web" o "arquitectura de
base de datos"), conteos facetados, sugerencias, vista previa, atajo `/`,
`Escape` para limpiar, URL compartible con `?q=...&tipo=...&uso=...` y enlaces
directos a la fuente original. Si la busqueda literal no encuentra nada, aplica
una intencion detectada en lugar de dejar la pagina vacia. Solo carga metadatos:
no copia ni ejecuta el contenido de las skills.

| Skill | Variantes |
|-------|-----------|
| `design` | editorial, glass, brutalist, swiss, luxury |
| `ui-ux-pro-max` | saas, marketplace, devtool, directory, ai-search |
| `ui-styling` | light, dark, airy, compact, gradient |
| `design-system` | grid, monochrome, bento, type, tokens |
| `brand` | wordmark, manifesto, color, geometric, community |

```bash
# refresca datos.js (muestra), catalogo.js (1.901) y regenera las 31 paginas
python scripts/generar-datos-landings.py
python scripts/generar-landings.py
```

Abre `landings/index.html` para ver la galeria completa.

## Desarrollo

```bash
python -m pytest -q
python -m ruff check .
python -m ruff format .
```

## Que no es

- No es un buscador web en vivo: trabaja sobre su catalogo, que se actualiza al
  sincronizar.
- No descarga ni ejecuta las herramientas que descubre.
- No requiere claves de IA ni embeddings; la similitud es textual (FTS5).
- No es aun la web publica: `landings/` son prototipos visuales con datos de
  muestra, salvo el buscador compacto, que ya usa el catalogo completo.
