# Ejemplo completo · Película que EXPLICA

La misma estructura que el `03`, pero pensada para que quien la vea **una sola vez pueda contar qué hace el producto**. Producto **ficticio**: un asistente que prepara facturas por chat, lee las facturas de proveedor que llegan por email y convierte la foto de un ticket en un gasto. Está basado en una película real de 1:37, con el producto, las marcas y los datos cambiados.

**Lo que añade respecto al `03`** (cópialo en tus prompts cuando el vídeo tenga que vender un servicio, no solo lucir):
- **Un raíl de 4 pasos** arriba que se rellena según avanza: Pides · Revisas · Te llega · Lo sabes. El espectador siempre sabe en qué parte está.
- **Números que cuadran.** Base + IVA = total; la suma de los tramos = el pendiente. Si un número no cuadra, alguien lo ve.
- **Lo que NO hace**, escrito en `<truth>`. Así nunca sale un fotograma prometiendo de más.
- **El gancho en el fotograma 0**: el caos (documentos acumulados) y la marca antes de los 4 segundos, con el drop justo ahí.

---

```text
<inputs>
Pídeme:
- el formato: vertical 1080×1920 para anuncios y reels (recomendado) u horizontal 1920×1080 para web;
- el wordmark en una sola palabra (recomendado: «factura.», que es a la vez verbo y sustantivo);
- 6-10 capturas reales: el chat preparando una factura, el borrador en el programa de facturación (cuenta de pruebas, nunca datos de clientes), la bandeja de correo con las etiquetas Facturas/* y la foto de un ticket convertida en gasto (si no las hay, recrea la interfaz en HTML con los textos y colores de abajo);
- una pista libre de derechos de unos 120 BPM y al menos 1:50, con drop y un breakdown tranquilo (Mixkit, uso comercial gratuito);
- un clip gratuito de stock de un escritorio a oscuras de noche, con papeles y tickets amontonados y un móvil que se ilumina sobre la mesa (Pexels).
</inputs>

<direction>
Película de lanzamiento al estilo de una keynote de Apple, solo 2D y en un único plano continuo: cada escena sale de la anterior, sin fundidos, desenfoques ni cortes. Las cosas se transforman unas en otras. Los textos suben desde una línea de máscara, los iconos brotan desde cero con efecto muelle, las barras y las líneas de factura se dibujan de lado a lado, las páginas empujan hacia delante y una forma tinta llena la pantalla antes de encogerse en la escena siguiente.
Tiene que EXPLICAR, no solo lucir: quien la vea una vez debe poder contar qué hace. Para eso:
- Arriba, dentro de la zona segura, hay un raíl de 4 pasos que se rellena según avanza: Pides · Revisas · Te llega · Lo sabes. El paso activo se pinta con el color de acento.
- Cada número que aparece cuadra con los demás (base + IVA = total; la suma de los tramos = el pendiente).
- Cada función se presenta con un titular corto que sube desde la máscara (2-4 palabras, Geist 800), dice lo que pasa en pantalla y se transforma en el siguiente elemento, nunca con un fundido.
Paleta: fondo papel #F6F4EE, tarjetas #FFFFFF, interfaz en tinta #14161A, texto secundario #6B6F76 y bordes #E4E1D8. Acento azul eléctrico #3B5BFF solo en badges, confirmaciones, el punto del wordmark y el paso activo del raíl. Alerta en #C2185B sobre #FDECF2 (duplicado bloqueado, IVA no válido). Liquid glass de iOS 26 sobre la interfaz y el vídeo. Bricolage Grotesque 800 para el wordmark, Geist para la interfaz y Geist Mono para importes, fechas y datos.
Un cursor dispara cada cambio con clics, arrastres y pulsaciones largas reales. La cámara hace zoom al estilo Screen Studio para que cada momento llene el encuadre, y el cursor escala con ella.
Prohibido: fundidos encadenados, entradas con desenfoque, «revelados» por brillo, líneas de escaneo brillantes, giros 3D, partículas, brillos, pausas de más de 1 s y cualquier cosa que huela a plantilla.
</direction>

<truth>
El servicio: un asistente que prepara facturas por chat + facturas de proveedor que llegan por email + tickets con una foto, todo dentro del programa de facturación del cliente. Solo funciones reales:
- El asistente busca al cliente, prepara la factura de venta EN BORRADOR, consulta lo facturado en un periodo y lo pendiente de cobro por antigüedad.
- Si hay varios clientes que encajan con el nombre, los enseña y pregunta; no elige él.
- Pide confirmación antes de preparar la factura.
- NUNCA aprueba una factura: la emisión definitiva la firma una persona.
- Validaciones en el código, no en la IA: importes positivos, IVA solo de 21, 10, 4 o 0 % y fechas válidas.
- Si se pide dos veces la misma factura, no crea otra.
- Facturas de proveedor por email: llega el correo, la IA lee el PDF, crea el proveedor si no existe y deja la compra en borrador con el PDF adjunto. El correo pasa de «Facturas/Pendiente» a «Facturas/Procesado»; si no es una factura, a «Facturas/NoFactura». Reenviar el mismo correo no duplica nada.
- Tickets: foto o PDF del ticket → gasto en borrador con la imagen adjunta.
NO mostrar: que el asistente apruebe o envíe facturas, que reclame cobros a los clientes ni ninguna aprobación automática.
Chips de la película: «Buscando cliente», «Borrador listo», «Sin duplicados», «IVA validado», «PDF adjunto», «Pendiente de cobro».
Datos ficticios: empresa «Estudio Lince» (estudio de diseño); clientes «Panadería Roble, S.L.» y «Roble Hermanos, C.B.»; proveedor «Imprenta Faro». Ningún cliente real. Sin URL. Llamada a la acción final: «Pide tu demo».
</truth>

<structure>
120 BPM, 176 pulsos (1:28), con algo pasando en cada pulso. Vertical 1080×1920; toda la acción dentro de la zona segura (deja libres los 220 px de arriba y los 380 px de abajo; el raíl de pasos va justo debajo de los 220 px). Ajusta los límites de cada tramo a los tiempos medidos de la pista: el drop, el breakdown y la vuelta del ritmo mandan.

1 · Gancho (pulsos 1-8): fotograma 0 = el caos: una pila de documentos (facturas, PDFs, tickets) y el titular «A mano, otra vez.». Un contador de pendientes sube a 29. La pila se absorbe en el punto del wordmark y el contador cae a «0 por hacer» justo cuando entra el DROP (antes de los 4 s): aparece «factura.».

2 · Todo entra en un sitio (9-24): el punto se expande en una píldora tinta con «Día 30 · 19:48 · cierre de mes». Clic: seis láminas de iris se cierran sobre la píldora y se abren de golpe sobre la lista de ventas. Detrás se despliega una cuadrícula como un mapa de papel: el programa de facturación en el centro y, alrededor, chat, email, foto de ticket, PDF, contactos, IVA, borrador y cobros. Se reordena en mosaico y un clic hace zoom en el chat. El raíl enciende «Pides».

3 · Pídela por chat (25-56): llega «Factura a Panadería Roble: 1.000 € + IVA por el diseño de etiquetas». Brota «Buscando cliente» y aparecen dos candidatos (Panadería Roble, S.L. · Roble Hermanos, C.B.). Sube la pregunta «¿Cuál de los dos?». El cursor toca S.L.
El chip se derrite en una gota que se estira hasta formar una barra de cristal con las 4 funciones (Cliente · Factura · Facturado · Pendiente). El icono Factura se abre en una factura cuyas líneas se dibujan una por pulso: Diseño de etiquetas · Base 1.000,00 € · IVA 21 % 210,00 € · Total 1.210,00 €. El asistente pregunta «¿La preparo?»; pulsación larga en «Sí»: la factura vuela a la lista y aterriza con «Borrador listo ✓».
Un cursor fantasma vuelve a mandar el mismo mensaje y rebota contra un candado: «Ya existe · sin duplicados».

4 · Tú la apruebas (57-72): el raíl pasa a «Revisas». Una lupa de cristal se posa sobre el campo IVA. Alguien escribe 18 %: el campo tiembla en color de alerta y brota «IVA válido: 21 · 10 · 4 · 0»; vuelve a 21 % y aparece «IVA validado ✓». Junto al asistente brota un candado: «Nunca aprueba». El cursor humano pulsa «Aprobar»; titular: «La firma una persona».

5 · Te llegan por email (73-96): el raíl pasa a «Te llega». La factura aprobada se pliega en un sobre que vuela a la bandeja de correo; la etiqueta «Facturas/Pendiente» se dibuja de lado a lado. Se abre el correo de Imprenta Faro con su PDF. La lupa recorre el documento y cada dato se subraya, uno por pulso: NIF · Base 300,00 € · IVA 21 % · Total 363,00 €. Los datos vuelan al formulario de compra, el PDF se engancha como un clip («PDF adjunto ✓») y aparece «Borrador listo ✓». La etiqueta se desliza a «Facturas/Procesado». Un segundo correo, un boletín sin factura, se desliza solo a «Facturas/NoFactura».

6 · Ticket: una foto (97-108): la etiqueta se estira hasta formar el visor de la cámara del móvil. El disparador sobre un ticket de gasolinera (45,60 €). La foto da la vuelta y se convierte en un gasto en borrador con la imagen adjunta.

7 · ¿Quién te debe? (109-132): el raíl pasa a «Lo sabes». El visor se encoge en el chat. Pregunta: «¿Qué tengo pendiente de cobro?». Brota «Pendiente de cobro» y las barras se dibujan por antigüedad: 0-30 días 2.140 € · 31-60 días 980 € · más de 60 días 360 €. Abajo sube «4 facturas · 3.480 €». Segunda pregunta: «¿Cuánto he facturado este trimestre?». Un contador en Geist Mono rueda hasta 18.450 € y brota una barra por mes.

8 · Con control (133-144): una única forma tinta que no deja de transformarse: Nunca aprueba ✓ → Si duda, pregunta ✓ → Sin duplicados ✓ → IVA validado ✓ → Cada gasto con su PDF ✓.

9 · Mundo real (145-168, en el BREAKDOWN): el círculo final se expande hasta que la tinta llena la pantalla, aguanta un pulso y se encoge sobre el clip real del escritorio a oscuras, con el móvil iluminándose. El mismo iris se abre sobre la pantalla del móvil y los contadores brotan uno por pulso: «Este mes: 12 facturas preparadas · 23 gastos con su PDF · 0 tecleadas a mano · 1 clic para aprobar», y se vuelve a cerrar.

10 · Cierre (169-176, con la VUELTA del ritmo): todo se contrae en la píldora, luego en el punto, y las letras de «factura.» vuelven a brotar en el pulso de regreso. Debajo sube «Pide tu demo». El último fotograma es igual que el primero (salvo esa línea y el raíl completo).
</structure>

<build>
1. Un solo HTML vertical de 1080×1920. Todo se calcula a partir del tiempo dentro de un async seek(t): sin transiciones CSS, sin temporizadores y sin estado que pase de un fotograma a otro. Expón window.videoSpec y window.renderReady.
2. Muelles con fórmula cerrada. Si un valor cambia de objetivo varias veces, suma un muelle por cada cambio para que siga siendo función del tiempo. Los contadores (pendientes, 18.450 €, los del mundo real) también.
3. Liquid glass: cada cristal lleva una copia de la escena que tiene detrás, deformada con un mapa de desplazamiento SVG (feImage con el campo de distancia de un rectángulo redondeado) en tres feDisplacementMap a escalas un poco distintas, más una luz de borde.
4. Efecto gota (goo): desenfoque más umbral de alfa, con el original encima para que el cristal siga nítido.
5. Iris de 6 láminas alrededor de una apertura hexagonal.
6. Compresión del wordmark: cada letra se acerca al punto en la misma proporción y se estrecha para seguir tocando a la siguiente. Si la tipografía no tiene eje de anchura, estrecha con scaleX por letra y, por debajo de 0,6, baja el peso.
7. Vídeo de stock: recodificado todo intra (ffmpeg -g 1), cargado como blob URL y esperando a «seeked» en cada fotograma.
8. Sonido: un efecto descargado (Mixkit) por cada evento, colocado por su pico medido.
   - Una lista única de eventos (tiempo, tipo) de la que salen a la vez la animación y los efectos.
   - Mide el BPM real de la pista antes de fijar pulsos («unos 120» puede ser 129,8) y edita la música para que el drop caiga en el gancho.
   - El mundo real va en el breakdown y el wordmark vuelve con el ritmo.
   - Si la pista es corta, se alarga repitiendo frases enteras de 8 compases, nunca a mitad de frase.
   - Normaliza a −14 LUFS.
9. Render con Playwright a 60 fps mezclando 4 subfotogramas por fotograma, en paralelo con pocos procesos. Revisa un fotograma por pulso y busca saltos de un solo fotograma.
</build>

<gotchas>
- backdrop-filter: url() no aplica bien los mapas de desplazamiento en Chromium: clona la escena.
- Una inundación de color tiene que pasar de las esquinas y durar unos 0,3 s.
- Un hijo con visibility: visible se ve a través de un padre oculto: usa inherit.
- El texto que cambia dentro de una forma que se transforma necesita su propia máscara.
- Chrome varía el antialiasing del texto entre dos capturas iguales: compara fotogramas con tolerancia, no byte a byte.
- Importes en formato español (1.210,00 €) y en Geist Mono con cifras tabulares, para que no bailen al rodar.
- Nunca un fotograma en el que el asistente aparezca aprobando o enviando una factura.
- Revisa el clip de stock entero: puede llevar textos o notificaciones en inglés que contradigan el mensaje; si es así, tápalos o cambia de clip.
</gotchas>

<start>
Pídeme los inputs y después enséñame el mapa de pulsos y 6 fotogramas (gancho, pídela por chat, tú la apruebas, te llegan por email, quién te debe, mundo real) antes de escribir la película entera.
</start>
```
