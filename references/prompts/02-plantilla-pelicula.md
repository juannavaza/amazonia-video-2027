# Plantilla · Película de lanzamiento por bloques

Esta es la estructura que más «wow» ha dado. Sale de un prompt de película de lanzamiento que circulaba por X en octubre de 2026, reescrita y ampliada con lo que aprendimos al producir dos películas reales con ella.

**Cómo usarla:**
1. Rellena todo lo que está entre `[corchetes]`. Si no sabes algo, déjalo y pídele a Claude: «rellena esta plantilla con lo que sabes de [producto] y pregúntame lo que falte».
2. Pega el resultado en una conversación nueva con la skill instalada.
3. Claude te pedirá los inputs y te enseñará el mapa de pulsos y unos fotogramas **antes** de escribir la película. Ahí es donde corriges.

Tienes dos ejemplos completos ya rellenados en `03-ejemplo-lanzamiento.md` y `04-ejemplo-explicativo.md`.

---

## Qué hace cada bloque

| Bloque | Para qué sirve | Si lo quitas… |
| --- | --- | --- |
| `<inputs>` | Lista lo que Claude tiene que pedirte antes de empezar | Se inventa logos, capturas y música |
| `<direction>` | El lenguaje visual: qué se transforma en qué, colores, letras, cámara y lo prohibido | Sale un «PowerPoint animado» con fundidos |
| `<truth>` | Lo que tu producto hace DE VERDAD, con los textos literales de la interfaz | Aparecen funciones que no existen |
| `<structure>` | El guion por pulsos de música: qué pasa en cada tramo | Ritmo plano, todo dura lo mismo |
| `<build>` | Cómo se construye por dentro (lo lee Claude, no tú) | Saltos, parpadeos y audio desfasado |
| `<gotchas>` | Trampas conocidas del navegador y reglas de tu marca | Repite errores que ya nos costaron horas |
| `<start>` | Obliga a enseñarte un avance antes de producir | Te encuentras 2 minutos de vídeo que no querías |

---

## La plantilla

```text
<inputs>
Pídeme:
- el formato: vertical 1080×1920 para reels y anuncios (recomendado) u horizontal 1920×1080 para web o YouTube;
- el wordmark en una sola palabra (recomendado: [un verbo o palabra corta que resuma lo que hace, con punto final: «atiende.», «factura.», «publica.»]);
- 6-10 capturas reales de [producto] ([qué pantallas]); si no las hay, recrea la interfaz en HTML con los textos y colores reales de abajo;
- [mi logo / el kit de marca de una herramienta que salga en el vídeo, solo si tengo permiso para usarlo];
- una pista libre de derechos de unos 120 BPM y al menos [duración + 10 s], con un drop y un breakdown tranquilo (Mixkit, uso comercial gratuito);
- un clip gratuito de stock de [una escena del mundo real donde se note el resultado: un mostrador a oscuras, un escritorio con papeles, una tienda cerrada…] (Pexels).
</inputs>

<direction>
Película de lanzamiento al estilo de una keynote de Apple, solo 2D y en un único plano continuo: cada escena sale de la anterior, sin fundidos, desenfoques ni cortes. Las cosas se transforman unas en otras. Los textos suben desde una línea de máscara, los iconos brotan desde cero con efecto muelle, las barras se dibujan de lado a lado, las páginas empujan hacia delante y una forma [negra / de tu color oscuro] llena la pantalla antes de encogerse en la escena siguiente.
[Si tiene que EXPLICAR y no solo lucir: «Quien la vea una vez debe poder contar qué hace. Arriba hay un raíl de [3-4] pasos que se rellena según avanza: [Paso 1 · Paso 2 · Paso 3 · Paso 4]. Cada número que aparece cuadra con los demás.»]
Cada función se presenta con un titular corto que sube desde la máscara (2-4 palabras, [tipografía] 800), dice lo que pasa en pantalla y se transforma en el siguiente elemento, nunca con un fundido.
Paleta: fondo [#color], interfaz en [#color], acento [#color] solo para [badges, confirmaciones y el punto del wordmark], estado de alerta [#color]. Liquid glass de iOS 26 sobre la interfaz y el vídeo. Tipografías: [una con mucha personalidad] para el wordmark, [una limpia] para la interfaz y [una monoespaciada] para horas, importes y datos.
Un cursor dispara cada cambio con clics, arrastres y pulsaciones largas reales. La cámara hace zoom al estilo Screen Studio para que cada momento llene el encuadre, y el cursor escala con ella.
Prohibido: fundidos encadenados, entradas con desenfoque, «revelados» por brillo, giros 3D, partículas, brillos decorativos, pausas de más de 1 s y cualquier cosa que huela a plantilla.
</direction>

<truth>
Solo funciones reales de [producto]:
- [función 1];
- [función 2];
- [función 3 …];
Etiquetas literales de la interfaz: «[texto exacto 1]», «[texto exacto 2]», «[texto exacto 3]».
Datos ficticios ([nombre de empresa inventada], [personas inventadas]). Ningún cliente real ni dato personal. Sin URL. Llamada a la acción final: «[CTA exacta]».
[Reglas de veracidad propias: «el asistente nunca aparece aprobando un pago», «el precio no sale en pantalla»…]
</truth>

<structure>
120 BPM, [N] pulsos ([duración]), con algo pasando en cada pulso. [Formato]; toda la acción dentro de la zona segura (en vertical, deja libres los 220 px de arriba y los 380 px de abajo). Ajusta los límites de cada tramo a los tiempos medidos de la pista: el drop, el breakdown y la vuelta del ritmo mandan.

1 · Apertura (pulsos 1-16): [el wordmark se comprime dentro de su propio punto; el punto se expande en una píldora y dentro sube «[la situación de partida, con hora o cifra]»]. [Algo que cuente o se acumule, un pulso cada vez].
2 · [Nombre del tramo] (17-24): [qué acción del cursor provoca qué cambio]. Termina con un zoom que aterriza justo en el DROP.
3 · [Función principal] (25-56): [mensaje o petición que llega] → [qué hace el producto, con su etiqueta literal] → [resultado visible ✓].
4 · [Función] ([pulsos]): […]
5 · [Función] ([pulsos]): […]
6 · [Función] ([pulsos]): […]
[…]
N-2 · Con control ([pulsos]): una única forma que no deja de transformarse: [garantía 1 ✓] → [garantía 2 ✓] → [garantía 3 ✓].
N-1 · Mundo real ([pulsos], en el BREAKDOWN): el círculo se expande hasta llenar la pantalla, aguanta un pulso y se encoge sobre el clip real. Se abre un iris sobre [la pantalla del móvil / el resultado] y los contadores brotan uno por pulso: «[resumen del resultado con números]».
N · Cierre ([pulsos], con la VUELTA del ritmo): todo se contrae en la píldora, luego en el punto, y las letras del wordmark vuelven a brotar. Debajo sube «[CTA]». El último fotograma es igual que el primero (salvo esa línea).
</structure>

<build>
1. Un solo HTML de [ancho×alto]. Todo se calcula a partir del tiempo dentro de un async seek(t): sin transiciones CSS, sin temporizadores y sin estado que pase de un fotograma a otro. Expón window.videoSpec y window.renderReady.
2. Muelles con fórmula cerrada. Si un valor cambia de objetivo varias veces, suma un muelle por cada cambio para que siga siendo función del tiempo. Los contadores también.
3. Liquid glass: cada cristal lleva una copia de la escena que tiene detrás, deformada con un mapa de desplazamiento SVG (feImage con el campo de distancia de un rectángulo redondeado) en tres feDisplacementMap a escalas un poco distintas para que los bordes separen colores, más una luz de borde. Para letras de cristal, un campo de distancia por letra hecho en canvas.
4. Efecto gota (goo): desenfoque más umbral de alfa, con el original encima para que el cristal siga nítido.
5. Iris de 6 láminas alrededor de una apertura hexagonal.
6. Vídeo de stock: recodificado todo intra (ffmpeg -g 1), cargado como blob URL y esperando a «seeked» en cada fotograma.
7. Sonido: un efecto descargado (Mixkit) por cada evento, colocado por su pico medido.
   - Una lista única de eventos (tiempo, tipo) de la que salen a la vez la animación y los efectos.
   - La canción arranca en tiempo fuerte; el primer gran zoom cae en el drop, el mundo real en el breakdown y el wordmark vuelve con el ritmo.
   - Si la pista es corta, se alarga repitiendo frases enteras de 8 compases, nunca a mitad de frase.
   - Normaliza a −14 LUFS.
8. Render con Playwright a 60 fps mezclando 4 subfotogramas por fotograma. Revisa un fotograma por pulso y busca saltos de un solo fotograma.
</build>

<gotchas>
- backdrop-filter: url() no aplica bien los mapas de desplazamiento en Chromium: clona la escena.
- Una inundación de color tiene que pasar de las esquinas y durar unos 0,3 s.
- Un hijo con visibility: visible se ve a través de un padre oculto: usa inherit.
- El texto que cambia dentro de una forma que se transforma necesita su propia máscara.
- Chrome varía el antialiasing del texto entre dos capturas iguales: compara fotogramas con tolerancia, no byte a byte.
- Importes y horas en fuente monoespaciada o con cifras tabulares, para que no bailen.
- Revisa el clip de stock entero: puede llevar textos o marcas que no te interesan.
- [Reglas de tu marca: «el logo de [herramienta] solo en el sello de partner», «nunca un fotograma con datos de un cliente»…]
</gotchas>

<start>
Pídeme los inputs y después enséñame el mapa de pulsos y [4-6] fotogramas ([apertura], [función principal], [otra función], [mundo real]) antes de escribir la película entera.
</start>
```

---

## Consejos para rellenarla

- **Los pulsos son tu guion.** A 120 BPM, 2 pulsos = 1 segundo. 112 pulsos ≈ 56 s (redes); 192 pulsos ≈ 1:36 (que se vea todo).
- **Escribe acciones, no pantallas.** Mal: «pantalla de agenda». Bien: «el cursor arrastra la cita de jueves a viernes y brota «Cita reprogramada ✓»».
- **Un hilo conductor.** Algo que esté al principio y al final: el punto del wordmark, una píldora, un móvil.
- **El bloque `<truth>` es innegociable.** Pon los textos exactos de tu interfaz. Es lo que hace que el vídeo parezca tu producto y no uno genérico.
- **No necesitas entender `<build>`.** Déjalo como está: es para Claude.
