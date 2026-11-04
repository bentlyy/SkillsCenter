# Herramientas, argumentos y fallback

Tres caminos para el mismo catálogo. Prefiere el primero que tengas disponible:

1. **MCP `skillscenter`** — datos frescos, ficha e histórico.
2. **CLI `skillscenter`** — mismo motor, sin agente MCP.
3. **Script incluido** — sin dependencias, solo stdlib; usa el catálogo
   exportado o SQLite en modo lectura.

## 1. MCP `skillscenter`

Arranque: `skillscenter serve` (stdio). En opencode el nombre real de la
herramienta puede llevar prefijo (`skillscenter_buscar`); los argumentos no
cambian.

| Herramienta | Argumentos | Devuelve |
|-------------|------------|----------|
| `buscar` | `consulta`, `categoria`, `fuente`, `tipo`, `orden`, `limite` | `{total, items[]}` |
| `tendencias` | `periodo` (24h/7d/30d/90d), `fuente`, `categoria`, `orden` (calor/crecimiento/recientes), `limite` | `{total, periodo, items[]}` |
| `novedades` | `dias`, `fuente`, `limite` | `{total, dias, items[]}` |
| `ficha` | `item` (slug, uid, url o nombre) | entrada + `historial` + `puntuaciones` |
| `categorias` | — | secciones con conteos |
| `fuentes` | — | estado, última ejecución y errores por fuente |
| `estadisticas` | — | totales por fuente, tipo y sección |
| `sincronizar` | `fuente`, `limite` | resumen por fuente (1-2 min) |
| `digest` | `dias`, `limite` | informe Markdown |

Notas:

- `buscar.tipo` usa el **tipo de origen** (`repo`, `skill`, `mcp_server`...), no
  la faceta de tipo. Para facetas usa el script.
- `buscar.orden`: `relevancia`, `calor`, `crecimiento`, `recientes`, `estrellas`,
  `descargas`.
- Los errores llegan como `{"error": "..."}` o como texto con el error.
- `sincronizar` puede fallar por límite de GitHub o por falta de credenciales de
  Reddit; revisa `fuentes` y reporta el aviso, no lo ocultes.

### Flujo MCP recomendado

```
estadisticas
  → (si está viejo o vacío) sincronizar
  → novedades(dias=7)          # si pidió "nuevo"
  → buscar(consulta=...)       # literal
  → buscar(consulta=<expansión>)  # conceptual
  → ficha(item=<mejor candidato>)
```

## 2. CLI `skillscenter`

```bash
skillscenter init            # crea la base
skillscenter sync            # rastrea todas las fuentes
skillscenter sync --fuente github --limite 30
skillscenter stats           # totales
skillscenter fuentes         # estado por fuente
skillscenter buscar "mcp servidor" --categoria mcp --limite 10
skillscenter tendencias --periodo 7d --orden crecimiento
skillscenter digest --dias 1 --salida informes/hoy.md
skillscenter serve           # servidor MCP
```

Si el comando no está en PATH: `python -m skillscenter ...`.

## 3. Script `skill_finder.py`

Sin dependencias externas. Python 3.10+.

```bash
python scripts/skill_finder.py "<consulta>" [opciones]
```

### Opciones

| Opción | Efecto |
|--------|--------|
| `consulta` (posicional) | Texto libre; si se omite, usa solo filtros |
| `--catalogo PATH` | Fuerza el archivo `catalogo.js`/JSON |
| `--tipo ID` | Filtra por faceta de tipo (`skill`, `mcp`, `agente`...) |
| `--uso ID` | Filtra por uso (`diseno`, `datos`, `codigo`...) |
| `--fuente ID` | Filtra por fuente (`github`, `npm`...) |
| `--categoria ID` | Filtra por sección (`skills`, `mcp`...) |
| `--concepto ID` | Fuerza una intención y omite la detección automática |
| `--intenciones` | Lista el mapa de intenciones y sale |
| `--orden` | `relevancia` (defecto), `calor`, `nombre` |
| `--limite N` | Máximo de resultados (1-200, defecto 20) |
| `--nuevos DIAS` | Solo altas de los últimos N días (requiere fechas por ítem: SQLite o CSV) |
| `--json` | Salida JSON completa |
| `--stats` | Conteos, fecha del catálogo y aviso de antigüedad |
| `--max-dias N` | Aviso si el catálogo tiene más de N días (defecto 3) |

### Salida

Texto (defecto): encabezado con catálogo, fecha, intenciones detectadas y una
tabla Markdown con:

```
# | Nombre (URL) | Fuente | Tipo | Uso | Score | Por qué
```

JSON (`--json`):

```json
{
  "consulta": "quiero armar una pagina web",
  "catalogo": {"ruta": "...", "actualizado": "2026-11-03", "total": 1901},
  "modo": "concepto",
  "nuevos": null,
  "intenciones": [{"id": "web", "nombre": "Diseñar una web", "puntos": 13}],
  "total": 10,
  "items": [
    {
      "nombre": "ui-styling",
      "url": "https://...",
      "fuente": "github",
      "tipo": "skill",
      "usos": ["diseno", "codigo"],
      "categoria": "skills",
      "score": 72,
      "metrica": "★ 1.2k",
      "descripcion": "...",
      "topics": ["ui", "tailwind"],
      "motivo": "intencion:web"
    }
  ]
}
```

### Resolución del catálogo

En este orden, el primero que exista:

1. `--catalogo PATH`
2. `SKILLSCENTER_CATALOGO` (variable de entorno)
3. `SKILLSCENTER_DB` o `%LOCALAPPDATA%\skillscenter\radar.db` (SQLite, solo lectura)
4. `assets/catalogo.js` de la skill instalada (lo copia el instalador)
5. `landings/assets/catalogo.js` del repositorio (autodetectado desde la skill)
6. `informes/catalogo-completo.csv` en el directorio actual

`catalogo.js` es la fuente preferida sin MCP: ya trae tipo, uso y fecha de
exportación, y no requiere instalar el paquete.

### Códigos de salida

| Código | Significado | Qué hacer |
|--------|-------------|-----------|
| `0` | Búsqueda ejecutada | Leer resultados (puede haber 0 ítems) |
| `2` | No se encontró catálogo, filtro o concepto inválido | Sincronizar/exportar o corregir el argumento; no inventar |
| `1` | Error de lectura del catálogo | Revisar la ruta y el formato |

### Ejemplos

```bash
# literal
python scripts/skill_finder.py "mcp postgres" --limite 5

# conceptual: el usuario no sabe el nombre
python scripts/skill_finder.py "quiero que mi agente lea contratos pdf" --limite 5

# forzar concepto y filtrar por tipo/uso
python scripts/skill_finder.py "componentes" --concepto web --tipo skill --limite 5

# estado del catálogo
python scripts/skill_finder.py --stats

# frescura (solo SQLite/CSV: catalogo.js no trae fecha por ítem)
python scripts/skill_finder.py --nuevos 30 --limite 10

# JSON para post-procesar
python scripts/skill_finder.py "evaluar prompts" --json --limite 3
```

## Frescura: qué es "actualizado"

- MCP: la fecha real de la última sincronización (`fuentes`/`estadisticas`).
- `catalogo.js`: campo `actualizado` del encabezado.
- SQLite: `MAX(ultima_vez_visto)` de los ítems.
- CSV: `MAX(ultima_vez_visto)`.

Si supera `--max-dias` (3 por defecto), el script imprime un aviso. Traslada ese
aviso a la respuesta: "el catálogo es del <fecha>; para lo último, sincroniza".

## Cuando una fuente falla

- Reddit sin credenciales: la fuente se omite, no rompe el resto.
- GitHub sin token: menos búsquedas por minuto; puede tardar más.
- `sincronizar` devuelve `estado` y `avisos` por fuente: cita el aviso.
- Si el catálogo local está vacío: pide `skillscenter init && skillscenter sync`
  o `python scripts/generar-datos-landings.py`.

Nunca rellenes un fallo de fuente con resultados de otra búsqueda no relacionada.
