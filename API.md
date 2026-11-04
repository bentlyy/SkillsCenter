# API

## Servidor MCP

Servidor `skill-radar`, transporte stdio. Arranque: `skill-radar serve`.

Todas las herramientas devuelven JSON en texto, salvo `digest`, que devuelve
Markdown. Los errores se devuelven como `{"error": "..."}` cuando aplica.

### `buscar`

```
buscar(consulta="", categoria=None, fuente=None, tipo=None,
       orden="relevancia", limite=20) -> JSON
```

- `consulta`: texto libre. Se normaliza (sin acentos) y se busca por prefijos.
- `categoria`: `mcp`, `agentes`, `skills`, `rag`, `programacion`, `imagen`,
  `audio`, `video`, `datos`, `infra`, `modelos`, `automatizacion`, `evaluacion`,
  `busqueda`, `otros`.
- `fuente`: `github`, `mcp_registry`, `awesome`, `hackernews`, `reddit`, `pypi`,
  `npm`, `huggingface`.
- `tipo`: `repo`, `skill`, `mcp_server`, `post`, `noticia`, `paquete`, `modelo`,
  `recurso`.
- `orden`: `relevancia`, `calor`, `crecimiento`, `recientes`, `estrellas`,
  `descargas`.
- `limite`: 1-200.

Respuesta: `{"total": n, "items": [resumen...]}`.

### `tendencias`

```
tendencias(periodo="7d", fuente=None, categoria=None,
           orden="calor", limite=20) -> JSON
```

`periodo`: `24h`, `7d`, `30d`, `90d`. `orden`: `calor`, `crecimiento`, `recientes`.

### `novedades`

```
novedades(dias=1, fuente=None, limite=20) -> JSON
```

Entradas con `primera_vez_visto` dentro de la ventana.

### `ficha`

```
ficha(item="<slug|uid|url|nombre>") -> JSON
```

Incluye `historial` (snapshots de metricas) y `puntuaciones` (score y crecimiento).

### `categorias`, `fuentes`, `estadisticas`

Sin argumentos. Devuelven JSON con conteos y estado.

### `sincronizar`

```
sincronizar(fuente=None, limite=None) -> JSON
```

Ejecuta el rastreo. `fuente` limita a una sola. Puede tardar 1-2 minutos.
Devuelve un resumen por fuente con `estado`, `items`, `nuevas`, `ms` y `avisos`
o `error`.

### `digest`

```
digest(dias=1, limite=15) -> Markdown
```

## API de Python

```python
from skill_radar import db
from skill_radar.pipeline import sincronizar

conn = db.conectar()          # ruta de SKILL_RADAR_DB o la de por defecto
db.inicializar(conn)          # idempotente

resumen = sincronizar(conn, fuentes=["github"], limite=25)

items = db.buscar(conn, "agentes", categoria="mcp", orden="calor", limite=10)
detalle = db.ficha(conn, items[0]["slug"])
stats = db.estadisticas(conn)

conn.close()
```

### Funciones utiles de `db`

| Funcion | Descripcion |
|---------|-------------|
| `conectar(ruta=None)` | Abre SQLite con WAL y foreign keys |
| `inicializar(conn)` | Crea el esquema y siembra fuentes/secciones |
| `upsert_item(conn, item, categorias)` | Alta/actualizacion deduplicada por `uid` |
| `guardar_snapshot` / `guardar_puntuacion` | Series temporales por dia |
| `buscar` / `tendencias` / `nuevos` / `ficha` | Consultas del catalogo |
| `listar_fuentes` / `listar_categorias` / `estadisticas` | Metadatos |
| `crear_aporte` / `listar_aportes` / `marcar_aporte` | Aportes de usuarios para la web |
| `reindexar_fts` | Reconstruye el indice de texto completo |

### Modelo `Item`

```python
Item(
    uid="github:owner/repo",      # obligatorio y estable
    fuente="github",
    tipo="repo",
    nombre="owner/repo",
    url="https://github.com/owner/repo",
    descripcion="...",
    autor=None,
    homepage=None,
    licencia="MIT",
    lenguaje="Python",
    topics=["mcp", "agents"],
    metricas={"estrellas": 1234},
    creado_en="2026-01-01T00:00:00Z",
    actualizado_fuente="2026-11-01T00:00:00Z",
    estado="activo",
)
```

## Crear una fuente nueva

1. Crea `src/skill_radar/sources/mi_fuente.py` con una clase que herede de
   `Fuente` e implemente `recolectar(cliente, limite) -> Resultado`.
2. Devuelve objetos `Item` con `uid` estable.
3. Registra la clase en `FABRICAS` de `sources/__init__.py`.
4. Añade sus metadatos en `fuentes.py`.
5. Añade un test si la logica de parseo es no trivial.
