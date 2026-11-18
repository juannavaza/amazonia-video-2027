# Voz, sonido y sincronía

Se lee cuando el vídeo lleva voz, o cuando lleva solo música y efectos y hay que sintetizarlos. Es el método con el que
se hicieron los vídeos de venta y de bienvenida de IA Masters OS.

## 0 · La primera pregunta: ¿con voz o solo con sonido?

No se da por hecho que haya voz. Antes que nada:

> «¿Lo quieres **con voz** (narrado: tu voz clonada, una voz de ElevenLabs o tu propia grabación) o **solo dinámico
> con música y efectos**, sin voz?»

- **Con voz** → guion (con `/reel` si es pieza corta de venta o redes), voz, imagen atada a cada palabra, mezcla con
  la música por debajo.
- **Solo sonido** → la música lleva el ritmo: reloj común con `beat-grid.py` o con la música sintetizada de
  `mezcla.py`, y efectos en las acciones. Sin `voz.py`.

## 1 · Guion → `guion.json`

```json
{"id": "venta", "pausa": 0.2, "hueco_bloques": 0.6,
 "diccionario": [["Skool", "Skul"]],
 "bloques": [{"id": "todo", "frases": [{"id": "hook", "texto": "…"}, {"id": "cero", "texto": "Cero teoría."}]}]}
```

- Una frase = un instante al que atar la imagen. Los `id` cortos y con significado (`hook`, `dia1`, `consultora`).
- Pieza corta: un solo bloque, una sola toma (la entonación sale mejor). Pieza larga: un bloque por capítulo, con
  `hueco_bloques` ~1 s para las tarjetas de capítulo.
- `pausa`: 0,2 s en venta (rápido), ~0,3 s en explicativo (respira).

## 2 · Voz → `scripts/voz.py`

```bash
python3 scripts/voz.py --proyecto P P/guiones/venta.json --simular        # cuenta caracteres, no gasta
python3 scripts/voz.py --proyecto P P/guiones/venta.json --tope 15000     # genera (con caché por bloque)
```

- **Gasto:** nunca sin OK. Se pregunta el tope de caracteres y se pasa en `--tope`; el script lleva la cuenta en
  `P/voz/gasto.json` y para antes de pasarse. Cambiar una frase solo regenera su bloque.
- **La voz:** la que la persona eligió en el Estudio de Vídeos (`~/.estudio-de-videos/voz.json`, se elige una vez con
  `node <estudio-de-videos>/herramientas/voces.mjs`). Para un vídeo concreto, `"voz": {"id": "…"}` en el guion. Receta
  que mejor ha sonado en las pruebas A/B (mejor que Multilingual v2): `eleven_v4`, estabilidad 0,35, similitud 0,7,
  estilo 0, velocidad 1, una toma por bloque y silencios largos acortados.
- **Clave:** `ELEVENLABS_API_KEY` del entorno, del `.env.local` del proyecto o de `~/.estudio-de-videos/.env.local` (la
  que guarda la página de la clave del Estudio: `node <estudio-de-videos>/herramientas/clave.mjs`). Nunca en el chat.
- **Pronunciación:** el texto en pantalla y el que se da a la voz son distintos. `DICCIONARIO` (en el script) y
  `diccionario` (en el guion) cambian «Claude» → «Clod», «IA» → «i a», «LLM» → «ele ele eme»,
  «/automatiza» → «barra automatiza». Las cifras, en letra.
- **Comprobar:** transcribir `voz.wav` con Whisper local (`faster_whisper`, modelo `medium`) y comparar con el guion. Si
  una palabra sale rara en el pase completo, transcribir ese trozo aislado antes de regenerar: Whisper se equivoca
  más que la voz («instalar» oído como «descargar»).
- **Salida:** `P/voz/<id>/voz.wav`, `tiempos.json` y `tiempos.js` (`window.TIEMPOS`).

## 3 · Imagen atada a la voz → `assets/voz-sync/`

Copiar `engine.mjs`, `declarativo.mjs` y `motion.mjs` al proyecto. Cargar `tiempos.js` antes del módulo.

- `ini('frase')`, `fin('frase')`, `pal('frase', 'palabra', n)`: el instante exacto en que se dice algo.
- `Film`: escenas con `[inicio, fin)` y `render(t)`. `arrancar(film)` crea `videoSpec`, `seek` y `renderReady`.
- `pop`, `win`, `ease`, `sp`, `count`, `type`, `tap`, `fill`: entradas, presencia, muelles, contadores, tecleo,
  pulsaciones y barras, todo en función de `t`.
- `chat(view, col)`: conversación que baja sola (mensajes con `data-t`); `subtitulos(box, {max, clase})`: subtítulos
  palabra a palabra (`max: 4` para venta; `max: 7, clase: 'sobrio'` para explicativo).
- **Declarativo** (`preparar(raiz)`), para piezas largas: cada elemento dice en el HTML cuándo entra.
  `data-in="midia-11@rutina"` = cuando dice «rutina» en esa frase; `data-out`, `data-a="up|left|right|scale|fade"`,
  `data-on` (añade la clase `on`). Admite `+.3`, `-.2`, `:fin` y `#2` (segunda aparición).
- Si una palabra del guion cambia y un `pal()` o `data-in` ya no la encuentra, el render falla diciendo cuál.

Reglas que salieron de las revisiones:
- **Fotograma 0 con contenido** (titular y protagonista ya en pantalla): es la miniatura antes de darle al play.
- Pegatinas y rótulos **dentro del encuadre** (comprobar el borde derecho), y nunca encima de los subtítulos.
- Caso inventado siempre con etiqueta visible («Caso de ejemplo»).
- Portada sin subtítulos: copiar la entrada a `portada.html` y ocultarlos si `location.pathname` termina así.

## 4 · Sonido → `scripts/mezcla.py`

```bash
python3 scripts/mezcla.py --proyecto P --id venta --musica energica              # con voz
python3 scripts/mezcla.py --proyecto P --id teaser --duracion 30 --musica energica   # solo sonido
```

- Música original sintetizada (energica 120 BPM, tranquila 84 BPM) o `--pista` propia con licencia.
- **Con voz: la música va muy por debajo** — 24 dB bajo la voz mientras se habla (`--bajo-voz`), sube 10 dB en los
  huecos (`--agache`), voz comprimida. Con la música más alta, la voz se pierde: no subirla sin que la persona lo pida.
- Efectos en `P/audio/<id>/eventos.json` con los mismos tiempos que la imagen (`"t": "instala@dos"`): whoosh en
  cambios de bloque, pop en pegatinas, click en botones, ding en confirmaciones, impacto en golpes. Pocos y con motivo.
- Sonoridad final: −14 LUFS venta, −16 explicativo; pico verdadero ≤ −1,5 dB (el limitador lo garantiza tras el AAC).

## 5 · Render → `scripts/render-tramos.sh`

```bash
bash scripts/render-tramos.sh P venta/index.html P/renders/venta.mp4 91.633 P/audio/venta/mezcla.wav
```

Por tramos de 60 s: no hace falta tener libres los ~1,7 GB de fotogramas de un vídeo de 9 min. Si se corta, se relanza
y sigue donde iba. Si Playwright dice que falta el navegador (pasa tras limpiar cachés del disco), ejecutar
`bash scripts/preparar-entorno.sh`.

## 6 · Entregar

MP4 + portada + guion junto al MP4; proyecto editable con README y `render.sh`. Por WhatsApp como documento (más de
30 MB no se ven en el móvil desde la app, pero sí por WhatsApp). Nada se publica sin OK.
