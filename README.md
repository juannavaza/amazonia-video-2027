# Amazonia · Propuesta digital 2027 · vídeo

Proyecto de PSWorks para el vídeo de la propuesta 2027 de Amazonia Fruit (entrega 20/11/2026).

## Qué hay aquí
- `build/`: el código que genera el vídeo (Python + PIL + ffmpeg). `borrador.py` es el principal: una función por escena (s01…s32), tiempos de voz desde `audio/tiempos.json`.
- `audio/`: locuciones de Alba (ElevenLabs), efectos y `tiempos.json` con los tiempos de palabra.
- `borrador/cambios_pendientes.md`: registro de cambios y pendientes, escena a escena.
- `material/**/notas.txt`: indicaciones por escena.

## Qué NO está (se queda en local, `~/Desktop/Projectos/video-codigo`)
- Vídeos renderizados y tramos (`borrador/`), material de vídeo e imagen de terceros (`material/`), música (`audio/musica/`) y tipografías con licencia (`fonts/`: Komu, Proxima Nova).

## Cómo se monta
```bash
python3 build/borrador.py            # renderiza tramos
# montaje completo: ver unir() en build/borrador.py
```

## Copia completa y cómo regenerar desde cero
La carpeta entera (con vídeos, material, música y tipografías) está en Google Drive: **Mi unidad › Videos-Claude › video-codigo.zip** (copia del 18/11/2026).

1. Descomprime `video-codigo.zip` en `~/Desktop/Projectos/video-codigo`.
2. Si hay cambios en GitHub posteriores al zip, copia encima `build/`, `audio/` y `borrador/cambios_pendientes.md` de este repo.
3. Requisitos: Python 3 con Pillow y numpy (y opencv-python para la portada), ffmpeg.
4. `python3 build/borrador.py` renderiza los tramos; el montaje completo se hace con `unir()`.
