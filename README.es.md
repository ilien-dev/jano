<p align="center"><a href="README.md">English</a> · <b>Español</b></p>

<h1 align="center">Jano: un hero SVG animado para tu README de GitHub</h1>

<p align="center"><b>Un skill para agentes que le dibuja a tu repositorio un hero animado en bucle y escribe el encabezado que va debajo,<br>
para que la primera pantalla del README muestre qué hace el proyecto.</b></p>

<p align="center">Jano lee tu repositorio, decide qué imagen lo explica y la dibuja como un SVG animado en oscuro y en claro. A una herramienta de terminal le pone sus comandos reales, a una aplicación una versión pequeña de su pantalla, a un conversor aquello que convierte. Después añade un logotipo si no tienes uno y el bloque del encabezado: título, eslogan, descripción, etiquetas y menú. Funciona en Claude Code, en Codex y en cualquier agente que lea el formato Agent Skills.</p>

<p align="center">
  <a href="#instalación"><img alt="Skill para Claude Code, Codex y otros agentes" src="https://img.shields.io/badge/agent%20skill-Claude%20Code%20%C2%B7%20Codex-1D6A99?style=flat-square&labelColor=0F1115"></a>
  <a href="#qué-hace-el-build"><img alt="Salida: SVG animado en oscuro y claro" src="https://img.shields.io/badge/salida-SVG%20animado%2C%20oscuro%20%2B%20claro-1D6A99?style=flat-square&labelColor=0F1115"></a>
  <a href="CHANGELOG.md"><img alt="Versión 0.1.0" src="https://img.shields.io/badge/versi%C3%B3n-0.1.0-0F1115?style=flat-square"></a>
  <a href="LICENSE"><img alt="Licencia: MIT" src="https://img.shields.io/badge/licencia-MIT-0F1115?style=flat-square"></a>
</p>

<p align="center">
  <a href="#instalación"><b>Instalación</b></a> ·
  <a href="#uso"><b>Uso</b></a> ·
  <a href="#qué-obtienes"><b>Qué obtienes</b></a> ·
  <a href="#las-reglas-que-sigue"><b>Reglas</b></a> ·
  <a href="#qué-hace-el-build"><b>Build</b></a> ·
  <a href="#límites"><b>Límites</b></a>
</p>

---

Este README todavía no tiene hero. Tendrá uno hecho con Jano.

## Instalación

Con la CLI de [skills](https://skills.sh), que lo instala para Claude Code, Codex, Cursor, Gemini CLI y los demás agentes que soporta:

```sh
npx skills add ilien-dev/jano
```

Como plugin de Claude Code, ejecuta estos dos comandos dentro de Claude Code:

```
/plugin marketplace add ilien-dev/jano
/plugin install jano@jano
```

A mano, copia `skills/jano` a donde tu agente busca los skills: `~/.claude/skills/jano` para Claude Code, `~/.agents/skills/jano` para Codex y otros.

El script de build necesita Python 3.9 o posterior. Con [uv](https://docs.astral.sh/uv/) instala él mismo sus dos dependencias. Sin uv, ejecuta una vez `pip install fonttools brotli`.

## Uso

Jano solo se ejecuta cuando tú lo llamas. El agente nunca lo inicia por su cuenta.

| Agente | Cómo llamarlo |
|---|---|
| Claude Code | `/jano` (como plugin: `/jano:jano`) |
| Codex | `$jano` |
| Otros | «usa el skill jano en este repositorio» |

Abre el agente en el repositorio al que quieres ponerle hero y llama al skill. Puedes añadir lo que quieres ver: `/jano muestra la sincronización entre los dos archivos, conserva nuestro azul`. Escribe los archivos y te enseña una página de vista previa. No hace commit.

## Qué obtienes

```
assets/logo.svg         el logotipo, se conserva si ya tienes uno
assets/hero.src.svg     la fuente que editas tú o el agente
assets/hero-dark.svg    generado desde la fuente
assets/hero-light.svg   generado desde la fuente
README.md               el encabezado reemplazado, el resto intacto
```

El encabezado del README tiene siempre las mismas partes, en este orden: el hero, el selector de idioma si hay un README en español, el título, un eslogan de una frase, una descripción de un párrafo, de tres a cinco etiquetas y un menú con enlaces a las secciones.

## Las reglas que sigue

El encabezado es igual en todos los repositorios. El hero no: dos heroes hechos con Jano no deben parecerse, porque la composición sale del proyecto.

- **La imagen explica la herramienta.** Quien no lea nada debería adivinar qué hace. Solo entran datos que el repositorio respalda, nunca una cifra inventada.
- **Nunca se detiene ni vuelve a empezar.** Cada animación se repite sin fin y cierra sobre sí misma. No hay entrada ni salida, y tampoco una escena que se arma y se reinicia, así que se ve como un lugar en marcha y no como un video.
- **Algo se mueve en todas partes, una sola cosa manda.** La imagen de la herramienta lleva el movimiento y lo demás se queda discreto.
- **El texto se puede leer.** El título y el eslogan no se mueven. El texto que se desplaza lo hace a velocidad constante y lenta.
- **Tu identidad manda.** Se reutilizan el logotipo y los colores que ya existen. Si no hay, elige un color de acento y deja lo demás neutro.

## Qué hace el build

GitHub muestra un SVG como imagen, así que no cargan scripts ni archivos externos, y un navegador dibuja a saltitos el texto que se mueve despacio. `build.py` resuelve las dos cosas:

- Escribe el archivo oscuro y el claro desde una sola fuente, con una paleta de colores con nombre.
- Incrusta solo las letras usadas de Space Grotesk y JetBrains Mono, para que el hero se vea igual en cualquier equipo.
- Convierte en trazos el texto que se mueve, que así se desliza donde el texto normal iría a tirones.
- Añade la regla que detiene el movimiento a quien pide menos movimiento en su sistema.
- Rechaza animaciones que se reproducen una sola vez, scripts y archivos externos, y avisa de contraste bajo, texto pequeño y archivos pesados.
- Escribe una página de vista previa con los dos temas, al ancho del README y al de un teléfono.

Un hero hecho así pesa entre 50 y 80 KB.

## Límites

- Esta es la versión 0.1.0. Se ha probado en tres repositorios y la ha usado una sola persona.
- El resultado depende del modelo que lo ejecuta. Un modelo más débil dibuja un hero más débil.
- El agente ve cuadros fijos de su propio trabajo. El movimiento lo revisas tú, en la vista previa.
- Las fuentes son fijas: Space Grotesk y JetBrains Mono. Un proyecto con tipografías propias no las tendrá en el hero.
- El hero está en inglés. El README en español usa el mismo.

## Licencia

MIT, ver [LICENSE](LICENSE). Las dos fuentes incluidas están bajo la SIL Open Font License, y sus archivos de licencia están junto a ellas en `skills/jano/assets`.
