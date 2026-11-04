# Taxonomía del catálogo

Hay cuatro ejes independientes. No los mezcles:

| Eje | Pregunta | Valores | Dónde se filtra |
|-----|----------|---------|-----------------|
| **Tipo** | ¿Qué es? | agente, modelo, mcp, skill, prompt, script, paquete, articulo, herramienta, recurso | Script: `--tipo`. MCP: no (ver aviso) |
| **Uso** | ¿Para qué sirve? | codigo, prompts, investigacion, datos, automatizacion, contenido, imagen, audio, video, diseno, infraestructura, evaluacion, integracion, general | Script: `--uso`. MCP: no (ver aviso) |
| **Fuente** | ¿De dónde vino? | github, mcp_registry, awesome, hackernews, reddit, pypi, npm, huggingface | Script: `--fuente`. MCP: `fuente` |
| **Categoría** | ¿En qué sección vive? | mcp, agentes, skills, rag, programacion, imagen, audio, video, datos, infra, modelos, automatizacion, evaluacion, busqueda, otros | Script: `--categoria`. MCP: `categoria` |

## Aviso importante sobre el MCP

La herramienta MCP `buscar` tiene un argumento `tipo` que **no** es el tipo de
artefacto de esta taxonomía. Ese `tipo` es el tipo de origen:

```
repo · skill · mcp_server · post · noticia · paquete · modelo · recurso
```

Si el usuario quiere "un agente" o "una skill", usa el script con `--tipo agente`
o `--tipo skill`, o busca por palabras y revisa la faceta en el resultado.
No pases `tipo="agente"` al MCP: devolverá vacío.

## Tipos (qué es)

| ID | Nombre | Descripción | Alias útiles |
|----|--------|-------------|--------------|
| `agente` | Agente | Frameworks y orquestadores que ejecutan tareas | agent, agents, autonomo, orquestador |
| `modelo` | Modelo | LLMs, embeddings y modelos especializados | model, llm, embeddings |
| `mcp` | MCP | Servidores, clientes y SDKs del protocolo MCP | mcp server, model context protocol |
| `skill` | Skill | Habilidades empaquetadas para agentes | habilidad, skills |
| `prompt` | Prompt | Plantillas y librerías de prompts | prompts, instrucciones |
| `script` | Script / CLI | Herramientas de terminal y automatizaciones | cli, command line, terminal |
| `paquete` | Paquete | Librerías y paquetes instalables | package, libreria, npm, pypi |
| `articulo` | Artículo | Noticias, posts y contenido editorial | noticia, post, blog |
| `herramienta` | Herramienta | Repos y utilidades sin categoría más específica | tool, repo, app |
| `recurso` | Recurso | Enlaces y material de apoyo | resource, material |

Regla práctica:

- "Quiero usar esto" → `herramienta`, `agente`, `mcp`, `paquete`, `script`.
- "Quiero aprender de esto" → `articulo`, `recurso`, `prompt`.

## Usos (para qué sirve)

| ID | Nombre | Descripción | Alias |
|----|--------|-------------|-------|
| `codigo` | Código | Escribir, revisar, probar o desplegar código | programar, desarrollo, developer |
| `prompts` | Prompts | Crear, organizar o mejorar instrucciones | prompt engineering |
| `investigacion` | Investigación | Buscar, leer, recuperar y sintetizar | research, rag, busqueda |
| `datos` | Datos | Analizar, transformar y consultar datos | sql, etl, dataframe |
| `automatizacion` | Automatización | Orquestar tareas, agentes y flujos | workflow, agentes |
| `contenido` | Contenido | Escribir, resumir, traducir y conversar | writing, docs, chat |
| `imagen` | Imagen | Generar, editar o analizar imágenes | vision, image |
| `audio` | Audio y voz | Voz, transcripción, música y sonido | speech, tts |
| `video` | Video | Generar, editar o animar vídeo | animation, film |
| `diseno` | Diseño | Interfaces, componentes y sistemas visuales | ui, ux, frontend |
| `infraestructura` | Infraestructura | Desplegar, servir y operar modelos | gpu, docker, cloud |
| `evaluacion` | Evaluación | Medir, probar y monitorear calidad | benchmark, testing |
| `integracion` | Integración | Conectar APIs, plugins, datos y servicios | api, plugin, webhook |
| `general` | General | Utilidad transversal sin uso dominante | multiproposito |

Un ítem puede tener hasta **3 usos**. Filtra por el uso dominante, no por todos.

## Fuentes (de dónde vino)

| ID | Nombre | Qué aporta |
|----|--------|-----------|
| `github` | GitHub | Repos, estrellas, forks, lenguaje, licencia |
| `mcp_registry` | Registro MCP | Servidores publicados en el registro oficial |
| `awesome` | Listas curadas | Enlaces de awesome-mcp-servers, awesome-ai-agents, etc. |
| `hackernews` | Hacker News | Lanzamientos y discusión |
| `reddit` | Reddit | Posts de r/LocalLLaMA, r/mcp, r/AIAgents |
| `pypi` | PyPI | Paquetes Python |
| `npm` | npm | Paquetes JavaScript |
| `huggingface` | Hugging Face | Modelos por descargas, likes y novedad |

Uso de la fuente:

- Para **producción**, prioriza `github`, `mcp_registry`, `pypi`, `npm`.
- Para **descubrir**, `hackernews`, `reddit`, `awesome`, `huggingface`.
- Si el usuario pide "lo más usado", ordena por `estrellas` o `descargas`.

## Categorías (secciones del catálogo)

| ID | Nombre | Qué contiene |
|----|--------|--------------|
| `mcp` | MCP | Servidores, clientes y SDKs |
| `agentes` | Agentes | Frameworks y orquestadores autónomos |
| `skills` | Skills y prompts | Skills, prompts y librerías de instrucciones |
| `rag` | RAG y memoria | Recuperación, embeddings, bases vectoriales |
| `programacion` | Programación | Asistentes de código, IDE, generación de software |
| `imagen` | Imagen | Generación y edición de imagen |
| `audio` | Audio y voz | Voz, transcripción, música |
| `video` | Video | Generación y edición de video |
| `datos` | Datos y análisis | Análisis, BI, scraping, procesamiento |
| `infra` | Infraestructura | Despliegue, GPU, serving, observabilidad |
| `modelos` | Modelos | LLMs, modelos especializados, pesos |
| `automatizacion` | Automatización | Workflows, RPA, integraciones |
| `evaluacion` | Evaluación | Benchmarks, testing, evaluación de modelos |
| `busqueda` | Búsqueda y navegación | Búsqueda, crawling y navegación para agentes |
| `otros` | Otros | Lo que aún no encaja |

## Cómo combinar filtros

| Objetivo | Consulta + filtros |
|----------|--------------------|
| Skill de diseño web | `--uso diseno --tipo skill` |
| Servidor MCP de base de datos | `base datos --tipo mcp` |
| Agente de código con tracción | `coding agent --tipo agente --orden calor` |
| Modelo de voz reciente | `speech --tipo modelo --nuevos 30` |
| Paquete Python para RAG | `rag --tipo paquete --fuente pypi` |
| Prompts de marketing | `marketing prompts --tipo prompt --uso contenido` |
| Lo mejor de evaluación | `--uso evaluacion --orden calor` |

## Errores comunes

- Cruzar `tipo` (qué es) con `categoria` (dónde vive) y esperar el mismo resultado.
- Filtrar por `general`: casi todo lo tiene como uso de relleno; no discrimina.
- Pedir `--tipo skill` cuando el usuario quiere "una capacidad" pero el catálogo
  la guarda como `herramienta` o `agente`. Si no hay resultados, quita el filtro.
- Asumir que `awesome` es una fuente de calidad: es una lista curada, no una
  garantía de mantenimiento.
