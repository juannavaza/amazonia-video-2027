# Prompt de película

Formato para entregar un encargo completo que otra conversación pueda producir sin contexto previo. Sirve para películas de lanzamiento, demos y explicaciones de producto. Al adaptar uno existente, conservar la estructura y sustituir todo el contenido; no arrastrar marcas, datos ni recursos del original.

## Bloques

| Bloque | Contenido obligatorio |
| --- | --- |
| `<inputs>` | Qué pedir antes de empezar: formato, wordmark, capturas reales, pista (BPM aproximado, duración mínima, drop y breakdown), clip de stock y su licencia. Ofrecer recrear la interfaz si no hay capturas. |
| `<direction>` | Lenguaje visual: plano continuo o cortes, qué se transforma en qué, paleta con códigos, tipografías con peso, cámara, cursor, titulares y lista de prohibiciones. |
| `<truth>` | Funciones reales y etiquetas literales de la interfaz, datos ficticios declarados, nada de clientes reales, CTA exacta. Es el bloque que impide inventar. |
| `<structure>` | BPM, número de pulsos y duración; formato y zona segura; tramos numerados con su rango de pulsos y qué acción visible ocurre en cada uno. Marcar dónde caen drop, breakdown y vuelta del ritmo. |
| `<build>` | Contrato técnico: un HTML, `seek(t)` puro, `window.videoSpec` y `window.renderReady`, muelles en forma cerrada, técnica de cada efecto, sonido desde una lista única de eventos, render y revisión. |
| `<gotchas>` | Fallos conocidos del navegador y del material, y reglas de veracidad propias del encargo. |
| `<start>` | Puerta de aprobación: pedir los inputs y enseñar el mapa de pulsos y 4–6 fotogramas clave antes de escribir la película entera. |

## Reglas que han dado buen resultado

- Escribir cada tramo como acción con causa y consecuencia («el cursor arrastra la cita de JUE a VIE: «Cita reprogramada ✓»»), no como pantalla.
- Un objeto persistente atraviesa la película: el punto del wordmark, una píldora negra, un orbe. El último fotograma repite el primero.
- Duración según contenido: 50–60 s para redes; 90–110 s si debe verse todo lo que hace el producto. Ajustar los límites de tramo a los tiempos medidos de la pista.
- Si la pieza debe explicar, añadir un raíl de 3–4 pasos que se rellena según avanza y titulares de 2–4 palabras que digan lo que pasa en pantalla.
- Los números en pantalla cuadran entre sí (base + IVA = total; la suma de tramos = el pendiente) y son función del tiempo.
- El gancho de 0–3 s enseña el problema o la marca en el fotograma 0; el drop de la música cae sobre la primera revelación.
- Medir el BPM real de la pista antes de fijar pulsos: «unos 120» puede ser 129,8.
- Editar la música solo en límites de frase (8 compases) y nunca a mitad de frase.

## Advertencias técnicas

- `backdrop-filter: url()` no aplica bien mapas de desplazamiento en Chromium: para cristal, clonar la escena de detrás y filtrar el clon.
- Una inundación de color debe sobrepasar las esquinas y durar unos 0,3 s; si no, media pantalla cambia en un fotograma.
- `visibility: visible` en un hijo se ve a través de un padre oculto: usar `inherit`.
- El texto que cambia dentro de una forma que se transforma necesita su propia máscara.
- Vídeo dentro del HTML: recodificar todo intra (`ffmpeg -g 1`), cargar como blob URL y esperar `seeked` antes de dibujar; un servidor sin peticiones por rangos no permite buscar.
- Una tipografía sin eje `wdth` se estrecha con `scaleX` por letra; por debajo de 0,6, compensar bajando el peso.
- Cifras en fuente monoespaciada o tabular para que no bailen al rodar.
- Revisar los clips de stock fotograma a fotograma: pueden llevar textos, marcas o notificaciones que contradicen el mensaje.
- Renderizar en paralelo con pocos procesos: con demasiados, uno puede colgarse al cargar el vídeo.

## Entrega del prompt

Entregar el prompt entero en un único bloque de texto, seguido de una lista breve de lo que se ha cambiado respecto al original y de lo que necesita la otra conversación (pista, clip, efectos o permiso para buscarlos). Guardarlo en el proyecto como fuente de la producción.
