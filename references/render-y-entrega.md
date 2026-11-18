# Render y entrega

## Proyecto y contrato

Separar docs, src, assets, audio, renders y reviews. Mantener recursos locales y materializar fuentes antes de capturar. Crear `window.videoSpec={width,height,fps,duration}`, `window.seek(t)` determinista y `window.renderReady` como promesa que espere imágenes, fuentes y otros recursos. Cada instante debe poder evaluarse tras cualquier salto temporal.

Resolver dependencias reales antes de prometer una exportación. HTML necesita Node, Playwright, Chromium y FFmpeg. `bash scripts/preparar-entorno.sh --comprobar` dice qué falta; sin la opción instala Playwright y Chromium en `~/.cache/crear-videos-con-codigo`, sin sudo. El renderer resuelve Playwright desde instalación normal, VIDEO_NODE_MODULES, CODEX_PRIMARY_RUNTIME_NODE_MODULES o esa carpeta, y permite VIDEO_CHROMIUM_PATH. No usar una sesión de navegador personal para renderizar. Ejecutar --help antes del primer uso.

La comprobación de determinismo tolera el ruido de antialiasing de texto de Chrome (diferencia máxima 32/255 en menos del 0,2 % de los píxeles). Si falla, hay estado real que depende del orden de los saltos: buscarlo, no relajar la tolerancia.

Para partir del ejemplo Canvas, copiar `assets/base-video/index.html` al proyecto y `assets/motion/motion.mjs` junto a ese HTML. El ejemplo contiene una transformación, no un estilo final. Cambiar diseño y contenido según el brief.

## Exportaciones

Sustituir rutas según proyecto y ubicación real de la skill:

```bash
node /ruta/skill/scripts/render-video.mjs --project /ruta/proyecto --output /ruta/proyecto/renders/prueba.mp4 --start 4 --end 9 --width 540 --height 960 --fps 30 --audio /ruta/proyecto/audio/mezcla.wav
node /ruta/skill/scripts/render-video.mjs --project /ruta/proyecto --output /ruta/proyecto/renders/final.mp4 --fps 60 --audio /ruta/proyecto/audio/mezcla.wav
node /ruta/skill/scripts/render-video.mjs --project /ruta/proyecto --output /ruta/proyecto/renders/portada.png --still 1.8
```

--start/--end seleccionan un intervalo del reloj original y recortan el audio desde el mismo origen. --duration cambia la duración declarada del proyecto; no usarlo como sustituto de --end para inspeccionar un tramo. La duración se redondea a fotogramas completos. --still usa tiempo absoluto. --overwrite permite sustituir una exportación explícitamente.

Para motion blur, añadir --subframes 4 --shutter 0.5. Cada fotograma promedia muestras alrededor de su instante; --subframes 1 es el valor predeterminado. Probar nitidez y coste antes del render completo. No usar supersampling para ocultar movimiento deficiente.

El motor HTML sirve solo archivos del proyecto, bloquea solicitudes externas y verifica seek tras un salto hacia atrás. Empaquetar recursos remotos primero. H.264 y yuv420p requieren dimensiones pares.

## Alternativa SVG

Crear un módulo propio con VIDEO_SPEC y frame(t,width,height) que devuelva el SVG completo. Python calcula el estado; CairoSVG no ejecuta JS ni animaciones SVG. Requiere Python, CairoSVG, FFmpeg y Pillow para desenfoque temporal. Consultar límites de filtros, tipografía y recursos antes de aceptar esta ruta. Mantener la dirección aprobada; no sustituir una escena compleja por tarjetas estáticas sin avisar.

```bash
python3 /ruta/skill/scripts/render-svg.py --scene /ruta/proyecto/scene.py --output /ruta/proyecto/renders/prueba.mp4 --start 1 --end 5 --audio /ruta/proyecto/audio/mezcla.wav --subframes 4
python3 /ruta/skill/scripts/render-svg.py --scene /ruta/proyecto/scene.py --output /ruta/proyecto/renders/final.mp4
```

SVG usa recursos inline y fuentes instaladas; empaquetar o documentar sus dependencias. Probar saltos temporales y cambios de formato. No declarar probado HTML a partir de SVG.

## Referencias y revisión

```bash
python3 /ruta/skill/scripts/extract-reference.py referencia.mp4 --output-dir refs/analisis --interval 0.5
python3 /ruta/skill/scripts/inspect-video.py renders/final.mp4 --output-dir reviews --beats beats.json --strip 4.2
```

Las hojas se paginan. Leer reference.json para saber si el máximo de muestras dejó cobertura incompleta; continuar los tramos necesarios. El extractor no descarga ni acredita acceso a una URL. El inspector no escucha ni reproduce por sí mismo.

## Entrega

Entregar MP4 por formato aprobado y fuentes editables con recursos permitidos, mapa musical, guion, brief/prompts usados, instrucciones reales y revisión. Generar una portada deliberada; no depender del primer fotograma si no representa la pieza. Guardar según el entorno. No incorporar recursos o datos de clientes a esta skill.
