<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
    <img src="assets/hero-light.svg" alt="Jano: una pared de ocho pequeñas imágenes en movimiento, cada una de un proyecto distinto (una app, una forma de pasar un muro, un chat, una memoria, una herramienta de sonido, un conversor de libros, un mapa, un juego), alrededor del símbolo de Jano y la frase: cada proyecto tiene su propia imagen en movimiento." width="100%">
  </picture>
</p>

<p align="center"><a href="README.md">English</a> · <b>Español</b></p>

<h1 align="center">Jano: un hero SVG animado para tu README de GitHub</h1>

<p align="center"><b>Un skill para agentes que le dibuja a tu repositorio un hero animado en bucle,<br>
para que la primera pantalla del README muestre qué hace el proyecto.</b></p>

<p align="center">Jano lee tu repositorio, decide qué imagen lo explica y la dibuja como un SVG animado en oscuro y en claro. A una herramienta de terminal le pone sus comandos reales, a una aplicación una versión pequeña de su pantalla, a un conversor aquello que convierte. Añade un logotipo si no tienes uno y no toca el texto de tu README. Funciona en Claude Code, en Codex y en cualquier agente que lea el formato Agent Skills.</p>

<p align="center">
  <a href="#instalación"><img alt="Skill para Claude Code, Codex y otros agentes" src="https://img.shields.io/badge/agent%20skill-Claude%20Code%20%C2%B7%20Codex-1D6A99?style=flat-square&labelColor=0F1115"></a>
  <a href="#qué-hace-el-build"><img alt="Salida: SVG animado en oscuro y claro" src="https://img.shields.io/badge/salida-SVG%20animado%2C%20oscuro%20%2B%20claro-1D6A99?style=flat-square&labelColor=0F1115"></a>
  <a href="https://github.com/ilien-dev/jano/releases"><img alt="Última versión" src="https://img.shields.io/github/v/release/ilien-dev/jano?style=flat-square&label=versi%C3%B3n&color=0F1115"></a>
  <a href="LICENSE"><img alt="Licencia: MIT" src="https://img.shields.io/badge/licencia-MIT-0F1115?style=flat-square"></a>
</p>

<p align="center">
  <a href="#galería"><b>Galería</b></a> ·
  <a href="#instalación"><b>Instalación</b></a> ·
  <a href="#uso"><b>Uso</b></a> ·
  <a href="#qué-obtienes"><b>Qué obtienes</b></a> ·
  <a href="#las-reglas-que-sigue"><b>Reglas</b></a> ·
  <a href="#qué-hace-el-build"><b>Build</b></a> ·
  <a href="#límites"><b>Límites</b></a>
</p>

---

## Galería

Heros hechos con Jano para repositorios reales. Cada uno lo dibujó un agente que solo tenía el repositorio y el skill. Abre un repositorio para ver su hero en su sitio.

**[Svipall](https://github.com/ilien-dev/svipall)**: Tu asistente lee la página real, no la pantalla de «comprobando tu navegador».

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="examples/svipall/hero-dark.svg">
    <img src="examples/svipall/hero-light.svg" alt="Svipall: un asistente pide un precio a un sitio web. Sin Svipall vuelve una pantalla de espera; con él llega la página real." width="100%">
  </picture>
</p>

**[Muninn](https://github.com/ilien-dev/muninn)**: Tu asistente recuerda tus decisiones y suelta las que cambiaste.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="examples/muninn/hero-dark.svg">
    <img src="examples/muninn/hero-light.svg" alt="Muninn: unas notas viajan de una persona a su asistente a través de un anillo llamado la memoria; una decisión reemplazada se tacha y se guarda." width="100%">
  </picture>
</p>

**[Anzu](https://github.com/ilien-dev/anzu)**: Tus libros de Kindle, abiertos en cualquier lector.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="examples/anzu/hero-dark.svg">
    <img src="examples/anzu/hero-light.svg" alt="Anzu: libros de Kindle con candado pasan bajo el logo de Anzu, pierden el candado y llegan a un lector, un teléfono y una tableta." width="100%">
  </picture>
</p>

**[Quirón](https://github.com/ilien-dev/quiron)**: Hace que el borrador de un chatbot se lea como escrito por una persona, y lo mide.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="examples/quiron/hero-dark.svg">
    <img src="examples/quiron/hero-light.svg" alt="Quirón: páginas escritas por un chatbot cruzan una línea bajo una estrella y salen reescritas; una regla pasa de 13 de 23 a 23 de 23." width="100%">
  </picture>
</p>

**[themis](https://github.com/ilien-dev/themis)**: La página de reglas que das a tus asistentes de IA, corta e idéntica en sus dos copias.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="examples/themis/hero-dark.svg">
    <img src="examples/themis/hero-light.svg" alt="themis: una página larga de reglas se filtra línea por línea; solo salen las que importan, en dos páginas cortas e idénticas." width="100%">
  </picture>
</p>

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
README.md               el hero colocado arriba, el resto intacto
```

Jano hace la imagen y nada más. Tu título, tu descripción, tus etiquetas y tus enlaces se quedan como los escribiste.

## Las reglas que sigue

Dos heroes hechos con Jano no deben parecerse, porque la composición sale del proyecto. Lo que comparten son estas reglas.

- **La imagen explica el repositorio.** El hero muestra lo que hace el proyecto como un flujo: qué entra, por qué pasos pasa y qué sale. Una aplicación se dibuja como su propia pantalla en esqueleto, con su flujo principal en marcha; una herramienta de terminal, como su terminal y lo que provoca el comando; un servicio, como una petición seguida de principio a fin. Quien no lea nada debería saber qué hace. Solo entran datos que el repositorio respalda, nunca una cifra inventada.
- **El logotipo y el nombre van primero, sin gritar.** Van juntos y no se mueven. El nombre es el texto más grande del lienzo, dentro de un rango fijo de tamaños.
- **Nunca se detiene ni retrocede.** Cada animación se repite sin fin y cierra sobre sí misma. Un flujo corre como un ciclo corto que termina donde empezó, y las cosas se van porque terminan, así que se ve como un lugar en marcha y no como un video.
- **Una sola cosa manda.** Lo que recorre el flujo lleva el movimiento y lo demás se queda discreto.
- **El texto se puede leer.** El título y el eslogan no se mueven. El texto que se desplaza lo hace a velocidad constante y lenta.
- **Tu identidad manda.** Se reutilizan el logotipo y los colores que ya existen. Si no hay, elige un color de acento y deja lo demás neutro.

Las reglas de movimiento vienen de gente que anima SVG e interfaces como oficio. Están, con sus fuentes, en [`skills/jano/references/motion.md`](skills/jano/references/motion.md), y qué dibujar para cada tipo de repositorio está en [`skills/jano/references/pictures.md`](skills/jano/references/pictures.md). Las dos están en inglés.

## Qué hace el build

GitHub muestra un SVG como imagen, así que no cargan scripts ni archivos externos, y un navegador dibuja a saltitos el texto que se mueve despacio. `build.py` resuelve las dos cosas:

- Escribe el archivo oscuro y el claro desde una sola fuente, con una paleta de colores con nombre.
- Incrusta solo las letras usadas de Space Grotesk y JetBrains Mono, para que el hero se vea igual en cualquier equipo.
- Convierte en trazos el texto que se mueve, que así se desliza donde el texto normal iría a tirones.
- Añade la regla que detiene el movimiento a quien pide menos movimiento en su sistema.
- Mide el dibujo antes de escribir nada: dónde cae cada forma y cada línea de texto en el lienzo (el texto se mide con las fuentes reales), cuánto y a qué velocidad se desplaza cada animación, y si cada bucle cierra sobre sí mismo.
- Rechaza lo que seguro está mal: texto que se sale de su caja, del lienzo o que pisa otro texto, un bucle que salta hacia atrás a la vista, parpadeos, una animación que se reproduce una sola vez, scripts y archivos externos.
- Avisa, con la solución, de lo que probablemente está mal: texto pequeño o con poco contraste, un nombre demasiado grande o demasiado pequeño, una imagen que ocupa muy poco lienzo, demasiadas palabras, movimiento demasiado rápido para seguirlo o demasiado pequeño para verlo, y archivos pesados.
- Imprime las medidas del hero: los tamaños del nombre, el logotipo y el eslogan, la parte del lienzo que ocupa la imagen, las palabras, la duración de los bucles y la velocidad máxima.
- Toma dos capturas si el equipo tiene Chrome, Chromium o Edge: el bucle detenido en ocho momentos, y el hero como lo muestra GitHub (los dos temas, un teléfono, desenfocado y sin movimiento). El agente las lee, así que revisa su propio movimiento y no un solo cuadro fijo.
- Escribe una página de vista previa con los dos temas, al ancho del README y al de un teléfono.

`check.py`, junto a él, hace solo las mediciones: `uv run skills/jano/scripts/check.py assets/hero.src.svg --json`.

Un hero hecho así pesa entre 50 y 80 KB.

## Límites

- Es una versión temprana. Se ha probado en tres repositorios y la ha usado una sola persona.
- El resultado depende del modelo que lo ejecuta. Un modelo más débil dibuja un hero más débil.
- El agente ve el bucle como ocho cuadros detenidos, no en movimiento. Cómo se siente lo juzgas tú, en la vista previa.
- Las comprobaciones miden posiciones, tamaños y tiempos. No saben si la imagen explica bien tu proyecto; eso sigue siendo trabajo del modelo y tuyo.
- Las capturas necesitan un navegador de la familia Chromium en el equipo. Sin él, el agente abre las páginas de vista previa con una herramienta de navegador, o las miras tú.
- Las fuentes son fijas: Space Grotesk y JetBrains Mono. Un proyecto con tipografías propias no las tendrá en el hero.
- El hero está en inglés. El README en español usa el mismo.

## Contribuir

Se aceptan issues y pull requests, un cambio a la vez. Las reglas están en [CONTRIBUTING.md](CONTRIBUTING.md), en inglés. El número de versión lo calcula el workflow de release a partir de los títulos de los pull requests, así que nadie lo escribe a mano.

## Licencia

MIT, ver [LICENSE](LICENSE). Las dos fuentes incluidas están bajo la SIL Open Font License, y sus archivos de licencia están junto a ellas en `skills/jano/assets`.
