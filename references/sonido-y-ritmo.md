# Sonido y ritmo

## Música como parte de la historia

Elegir pista aportada, recurso con licencia adecuada o composición original con una herramienta disponible. En síntesis por código, diseñar estructura, armonía, instrumentación y mezcla; un bucle de percusión no garantiza una dirección musical. No activar pagos, clonar voces o asumir créditos sin autorización y capacidad real.

Crear apertura, desarrollo, contraste y cierre. No cortar frases musicales al alcanzar la duración. Separar voz, música y efectos cuando existan stems. Ligar efectos a acciones significativas; evitar un whoosh en cada objeto. Dejar espacio a la lectura y la voz.

## Reloj común

Para composición nueva con tempo y origen conocidos:

```bash
python3 scripts/beat-grid.py --bpm 128 --duration 30 --offset 0 --output beats.json
```

Para pista existente:

```bash
python3 scripts/beat-grid.py --audio audio/track.wav --output beats.json
```

La detección mediante librosa es una estimación. Comprobar fase, silencios y cambios de tempo escuchando la pista. El script deja `downbeats` vacío hasta recibir `--downbeat-index N` en audio analizado; no adivina el primer pulso de compás. `--meter` indica pulsos por compás. Para tempo variable, conservar las marcas medidas y corregirlas según la escucha, sin imponer una rejilla uniforme.

El JSON registra procedencia, BPM, pulsos, compases y onsets candidatos. Los onsets no son necesariamente golpes de batería: elegir los útiles. Hacer que animación y síntesis lean las mismas marcas. Guardar eventos con tiempo, objeto, acción y efecto. Al renderizar un fragmento, recortar audio y vídeo desde el mismo origen.

## Sincronía y mezcla

Ubicar el momento perceptivo importante sobre el acento elegido; no todo movimiento debe empezar en un golpe. Variar energía y dejar pausas útiles. Escuchar comienzo, resolución, transiciones, balance y clics.

Medir nivel integrado y pico verdadero tras codificar. Como punto de partida para una pieza social, considerar alrededor de −14 LUFS y al menos 1 dB de margen de pico verdadero; ajustar al material, plataforma y brief. Una medición no sustituye la escucha.

```bash
ffmpeg -hide_banner -i final.mp4 -vn -af ebur128=peak=true -f null -
```

No acreditar sincronía audible por BPM declarado, metadatos o imágenes. Si no hay escucha disponible, dejarlo pendiente y entregar la pieza como prueba con esa limitación.
