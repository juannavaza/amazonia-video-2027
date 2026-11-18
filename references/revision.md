# Revisión con evidencia

## Comparar la prueba con el encargo

Observar muestras a tamaño móvil y secuencias consecutivas alrededor de acciones difíciles. Reproducir y escuchar cuando sea posible. No continuar a producción completa solo por una nota autoasignada.

| Criterio | Evidencia | Problema que requiere corrección |
| --- | --- | --- |
| Gancho | Apertura y primer resultado visible | Inicio vacío o tardío |
| Claridad | Acción y consecuencia reconocibles | Decoración que no explica |
| Continuidad | Secuencia alrededor del cambio | Saltos o pérdida de identidad |
| Variedad | Comparación de planos | Misma composición repetida sin intención |
| Lectura | Imágenes a 360 px y tiempo asentado | Texto cortado, diminuto o fugaz |
| Movimiento | Reproducción y tiras | Aceleración abrupta o falta de foco |
| Marca/contenido | Recursos y fuentes contrastados | UI inventada presentada como real |
| Sonido | Escucha, marcas y nivel | Desfase, final truncado o mala mezcla |

En movimiento continuo, una sucesión de pantallas independientes falla aunque el archivo sea correcto. En una explicación sobria, respetar pausas útiles y no forzar efectos.

## Registro

Guardar tiempo, observación, consecuencia, gravedad, corrección y estado. Separar hechos de hipótesis. Priorizar contenido falso, ilegibilidad, desfase y discontinuidad. Corregir hasta tres problemas principales por ronda y verificar lo afectado. Tras tres rondas sin resolver una causa, cambiar planteamiento o recurso.

## Niveles separados

1. Archivo: metadatos, duración, fotogramas, audio y decodificación.
2. Muestras: hojas paginadas, apertura, cierre y momentos críticos.
3. Movimiento: reproducción continua con revisión de lectura y continuidad.
4. Escucha: música, voz, balance y sincronía percibida.

Registrar realizado, fallido o pendiente. No marcar movimiento o sonido como revisados por leer código. Completar campos de `inspection.json` solo con acciones realizadas. Si faltan reproducción o escucha, presentar una prueba pendiente de esa revisión, no un acabado creativo validado.

## Comandos

```bash
python3 scripts/inspect-video.py final.mp4 --output-dir reviews --samples 12
python3 scripts/inspect-video.py final.mp4 --output-dir reviews-beats --beats beats.json
python3 scripts/inspect-video.py fragmento.mp4 --output-dir reviews-tramo --beats beats.json --timeline-start 8 --strip 9.2
```

`--strip` añade doce fotogramas alrededor de un tiempo del proyecto; puede repetirse. `--times 0,1.5,7.9` añade tiempos específicos. El informe enumera todas las hojas. Extraerlas no acredita haberlas observado.
