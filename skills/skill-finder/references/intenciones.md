# Intenciones y expansión conceptual

Una **intención** es la tarea que el usuario quiere resolver, no el nombre del
producto. El buscador literal no la entiende; esta tabla la traduce a términos
que sí existen en el catálogo.

## Cómo usar esta tabla

1. Escucha la **función**, no el sustantivo: "necesito ordenar mis PDFs" es
   `investigacion`, no "PDF".
2. Elige **1 o 2 intenciones** como máximo. Dos intenciones contradictorias
   ensucian el ranking.
3. Toma sus `términos` y arma una consulta de 2 a 5 palabras.
4. Si hay un eje claro, filtra también por `uso` y `tipo`
   (ver `taxonomia.md`).
5. Verifica con la ficha antes de recomendar.

El script `scripts/skill_finder.py` aplica esta misma tabla automáticamente y
reporta qué intención detectó.

---

## `web` — Diseñar una web

- **El usuario dice**: "quiero una web", "landing page", "página web", "sitio",
  "interfaz", "frontend", "diseño de páginas web", "componentes".
- **Términos**: `web`, `landing`, `frontend`, `front-end`, `html`, `css`, `react`,
  `vue`, `svelte`, `tailwind`, `figma`, `interfaz`, `componente`, `ui`, `ux`,
  `design`, `diseno`, `disenar`, `shadcn`.
- **Usos**: `diseno`, `codigo`.
- **Tipos**: `skill`, `herramienta`, `agente`.
- **Consulta literal sugerida**: `diseno web frontend ui`.
- **Cuidado**: "web" también aparece en "web search" (RAG). Si el usuario dice
  "buscar en la web", la intención es `investigacion`, no `web`.

## `datos` — Modelar o analizar datos

- **El usuario dice**: "base de datos", "SQL", "esquema", "ETL", "analizar datos",
  "dashboards", "BI", "consultas".
- **Términos**: `sql`, `database`, `postgres`, `postgresql`, `mysql`, `sqlite`,
  `mongodb`, `esquema`, `schema`, `etl`, `dataframe`, `datos`, `analitica`,
  `duckdb`, `bigquery`, `pandas`, `consulta`, `vector database`.
- **Usos**: `datos`, `investigacion`.
- **Tipos**: `mcp`, `herramienta`, `script`, `paquete`.
- **Consulta literal sugerida**: `base de datos sql etl`.
- **Cuidado**: "vector database" suele ser `investigacion`/RAG, no BI.

## `automatizacion` — Automatizar tareas

- **El usuario dice**: "automatizar", "flujo de trabajo", "workflow", "agentes
  autónomos", "orquestar", "que haga todo solo".
- **Términos**: `automatizar`, `automatizacion`, `automation`, `workflow`,
  `orquestador`, `orquestar`, `orchestration`, `agente`, `agentes`, `agents`,
  `agentic`, `n8n`, `zapier`, `make`, `pipeline`, `tarea`, `tareas`, `rpa`.
- **Usos**: `automatizacion`.
- **Tipos**: `agente`, `herramienta`, `script`, `mcp`.
- **Consulta literal sugerida**: `automatizar workflow agentes`.
- **Cuidado**: un framework de agentes no siempre automatiza un proceso de
  negocio; revisa la descripción.

## `codigo` — Escribir, revisar o probar código

- **El usuario dice**: "programar", "escribir código", "revisar código", "tests",
  "refactorizar", "asistente de código", "IDE".
- **Términos**: `codigo`, `programar`, `programacion`, `code`, `coding`,
  `developer`, `dev`, `ide`, `vscode`, `copilot`, `testing`, `refactor`, `debug`,
  `software`, `code review`, `unit test`, `sdk`.
- **Usos**: `codigo`.
- **Tipos**: `agente`, `skill`, `herramienta`, `paquete`.
- **Consulta literal sugerida**: `coding assistant code review`.

## `prompts` — Crear u organizar prompts

- **El usuario dice**: "prompts", "instrucciones", "plantillas", "system prompt",
  "prompt engineering".
- **Términos**: `prompt`, `prompts`, `instrucciones`, `plantilla`, `plantillas`,
  `system prompt`, `prompt library`, `prompt engineering`, `few shot`,
  `prompt management`.
- **Usos**: `prompts`.
- **Tipos**: `prompt`, `skill`, `herramienta`.
- **Consulta literal sugerida**: `prompt library system prompt`.

## `skills` — Encontrar o crear skills

- **El usuario dice**: "una skill", "habilidad para el agente", "claude skill",
  "agent skill", "pack de skills", "cómo empaquetar una skill".
- **Términos**: `skill`, `skills`, `habilidad`, `habilidades`, `agent skill`,
  `claude skill`, `skill manager`, `plugin`, `extension`, `tool use`.
- **Usos**: `prompts`, `automatizacion`.
- **Tipos**: `skill`.
- **Consulta literal sugerida**: `agent skills claude skill`.
- **Cuidado**: "skill" es un término muy amplio; acompáñalo con el dominio
  ("skill de diseño", "skill de datos").

## `investigacion` — Investigar, RAG y memoria

- **El usuario dice**: "investigar", "buscar información", "RAG", "base de
  conocimiento", "leer PDFs", "resumir documentos", "memoria".
- **Términos**: `rag`, `retrieval`, `embedding`, `embeddings`, `vector`,
  `busqueda`, `search`, `web search`, `investigacion`, `research`, `pdf`,
  `documento`, `documentos`, `knowledge base`, `memoria`, `memory`, `crawler`,
  `scraper`.
- **Usos**: `investigacion`.
- **Tipos**: `mcp`, `herramienta`, `modelo`, `agente`.
- **Consulta literal sugerida**: `rag retrieval embeddings documents`.
- **Cuidado**: "search" también aparece en buscadores de código; mira el uso.

## `integracion` — Conectar herramientas

- **El usuario dice**: "conectar", "API", "MCP", "servidor MCP", "plugin",
  "webhook", "Slack", "Notion", "base de datos remota".
- **Términos**: `mcp`, `model context protocol`, `api`, `integracion`,
  `integrar`, `conectar`, `connector`, `plugin`, `webhook`, `slack`, `notion`,
  `github`, `sdk`, `adapter`, `server`, `servidor`.
- **Usos**: `integracion`.
- **Tipos**: `mcp`.
- **Consulta literal sugerida**: `mcp server connector api`.
- **Cuidado**: "MCP" puede ser un servidor, un cliente o un SDK. Filtra por tipo
  si el usuario necesita uno concreto.

## `imagen` — Generar, editar o analizar imagen

- **El usuario dice**: "generar imágenes", "diseño gráfico", "fotos", "visión",
  "OCR", "texto a imagen".
- **Términos**: `imagen`, `imagenes`, `image`, `images`, `vision`, `diffusion`,
  `stable diffusion`, `midjourney`, `dalle`, `flux`, `comfyui`, `ocr`, `foto`,
  `fotos`, `text to image`, `segmentation`, `object detection`.
- **Usos**: `imagen`.
- **Tipos**: `modelo`, `herramienta`, `skill`.
- **Consulta literal sugerida**: `image generation diffusion`.

## `audio` — Voz y audio

- **El usuario dice**: "voz", "hablar", "transcribir", "TTS", "speech", "música".
- **Términos**: `audio`, `voz`, `voice`, `speech`, `tts`, `asr`, `whisper`,
  `music`, `transcription`, `text to speech`, `speech recognition`, `sound`.
- **Usos**: `audio`.
- **Tipos**: `modelo`, `herramienta`, `mcp`.
- **Consulta literal sugerida**: `speech transcription tts`.

## `video` — Generar o editar video

- **El usuario dice**: "video", "animar", "texto a video", "avatar".
- **Términos**: `video`, `videos`, `animation`, `avatar`, `text to video`,
  `video generation`, `film`.
- **Usos**: `video`.
- **Tipos**: `modelo`, `herramienta`.
- **Consulta literal sugerida**: `video generation animation`.

## `infraestructura` — Desplegar y operar

- **El usuario dice**: "desplegar", "servir modelos", "GPU", "Docker",
  "Kubernetes", "local LLM", "cuantización".
- **Términos**: `inference`, `serving`, `gpu`, `cuda`, `deploy`, `deployment`,
  `docker`, `kubernetes`, `observability`, `llmops`, `local llm`,
  `quantization`, `fine tuning`, `cloud`, `self hosted`.
- **Usos**: `infraestructura`.
- **Tipos**: `herramienta`, `paquete`, `modelo`, `script`.
- **Consulta literal sugerida**: `inference serving docker llmops`.

## `evaluacion` — Medir y probar calidad

- **El usuario dice**: "evaluar", "benchmark", "testing", "guardrails",
  "monitorear", "métricas", "trazabilidad".
- **Términos**: `eval`, `evaluation`, `benchmark`, `benchmarks`, `testing`,
  `test`, `guardrails`, `red teaming`, `monitoring`, `metrics`, `tracing`.
- **Usos**: `evaluacion`.
- **Tipos**: `herramienta`, `paquete`, `skill`.
- **Consulta literal sugerida**: `evaluation benchmark guardrails`.

## `contenido` — Escribir, resumir, traducir

- **El usuario dice**: "redactar", "resumir", "traducir", "documentación",
  "marketing", "SEO", "presentaciones", "chat".
- **Términos**: `writing`, `content`, `blog`, `copywriting`, `documentation`,
  `docs`, `chat`, `assistant`, `presentation`, `slides`, `seo`, `marketing`,
  `summarization`, `translation`, `text generation`, `question answering`.
- **Usos**: `contenido`.
- **Tipos**: `modelo`, `skill`, `herramienta`, `prompt`.
- **Consulta literal sugerida**: `writing summarization translation`.

---

## Combinaciones útiles

| Necesidad real | Intención | Filtros sugeridos |
|----------------|-----------|-------------------|
| "Una skill que diseñe landings" | `web` | `--tipo skill --uso diseno` |
| "Un MCP para consultar Postgres" | `datos` + `integracion` | `--tipo mcp` |
| "Algo para leer contratos en PDF" | `investigacion` | `--uso investigacion` |
| "Automatizar respuestas de Slack" | `automatizacion` + `integracion` | `--tipo agente` |
| "Un modelo para transcribir reuniones" | `audio` | `--tipo modelo` |
| "Probar prompts antes de producción" | `prompts` + `evaluacion` | `--uso evaluacion` |
| "Desplegar un LLM en mi GPU" | `infraestructura` | `--uso infraestructura` |
| "Un agente que revise pull requests" | `codigo` + `automatizacion` | `--tipo agente` |

## Señales de una mala expansión

- La consulta expandida tiene más de 5 términos: el ranking se vuelve difuso.
- Elegiste 3+ intenciones: estás adivinando, no escuchando.
- Los resultados no comparten ni el tipo ni el uso: vuelve a la intención.
- La intención no aparece en la descripción de ningún resultado: dilo y
  ofrece el resultado más cercano, sin disfrazarlo.
