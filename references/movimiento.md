# Movimiento y continuidad

Hacer que el movimiento cambie una relación: conexiones, transformación o causa y resultado. Planificar geometría y ritmo antes del adorno. Dar a la cámara un objetivo y una trayectoria; no aplicar un zoom global como sinónimo de dinamismo.

| Mecanismo | Uso | Condición |
| --- | --- | --- |
| Objeto persistente | Botón que se expande en panel; dato que se convierte en resultado | Conservar identidad geométrica |
| Ensamblaje | Partes que forman una solución | Mostrar dependencias |
| Reencuadre | De detalle a sistema y viceversa | Aterrizar en un foco legible |
| Máscara y cambio de forma | Tarjeta que se vuelve gráfica | Coordinar geometría y contenido |
| Tipografía cinética | Mensaje convertido en acción | Alinear movimiento y significado |
| Trazado | Recorridos y conexiones | Orden causal y velocidad perceptible |

Variar curvas y velocidades con intención. Evitar rebotes en texto que deba asentarse rápido. Dar tiempo al resultado de una acción rápida.

## Utilidad opcional

Copiar `assets/motion/motion.mjs` al proyecto. Exporta `spring`, `track`, `mix`, `clamp`, `morphBox`, `camera` y `noise`. Son funciones de tiempo sin estado acumulado. `spring` resuelve amortiguación baja, crítica y alta; `track` suma respuestas a cambios de objetivo. Usar segundos absolutos.

```js
import {track, morphBox} from './motion.mjs';
const states = [
  {t: 0, x: 160, y: 320, w: 180, h: 80, r: 40},
  {t: 1.1, x: 70, y: 240, w: 360, h: 260, r: 24},
  {t: 2.7, x: 130, y: 300, w: 240, h: 100, r: 16}
];
const box = morphBox(t, states, {frequency: 2.4, damping: 1});
const focus = track(t, [[0, 0], [1.2, 1], [2.6, 0]], {damping: 1});
```

La base Canvas transforma una forma en gráfica y resultado; la base SVG demuestra un mecanismo equivalente. Son ejemplos de movimiento, no estilos predeterminados. Adaptar composición, recursos y curvas al brief.

## Cámara y texto

Diseñar en coordenadas de escena y aplicar la cámara una vez. Usar una capa posterior para texto que deba permanecer nítido cuando corresponda. Recalcular layout por aspecto, sin estirar ni recortar una composición ajena al formato.

Ordenar cambios: iniciar geometría, retirar contenido, revelar contenido nuevo y dejarlo asentarse. Hacer entrar el texto en una ventana de baja velocidad. Mantener posiciones continuas al cambiar objetivo.

## Desenfoque temporal

Los renderers admiten `--subframes 1|2|4|8` y `--shutter 0..1`. Probar una acción con 1 y 4 muestras. El promedio temporal aumenta el coste aproximadamente por el número de muestras y puede ensuciar texto. Usarlo solo si mejora el movimiento observado.
