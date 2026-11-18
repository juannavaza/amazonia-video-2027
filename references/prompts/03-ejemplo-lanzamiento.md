# Ejemplo completo · Película de lanzamiento

La plantilla `02` rellenada para un producto **ficticio**: un recepcionista con IA que atiende por chat a los clientes de un negocio mientras está cerrado. Está basado en una película real de 1:36, con el producto, las marcas y los datos cambiados.

**Úsalo así:** cambia el producto por el tuyo (o pídele a Claude: «adapta este prompt a [mi producto] con lo que sabes de él»), revisa el bloque `<truth>` línea a línea y pégalo en una conversación nueva.

**Por qué funciona:**
- Cuenta una historia (una noche en la recepción, de 23:47 a la mañana), no una lista de funciones.
- Cada función es una acción del cursor con su resultado: «Cita reservada ✓».
- El drop de la música cae en el primer gran zoom y el breakdown en el «mundo real».
- El último fotograma es igual que el primero: el vídeo hace bucle en redes.

---

```text
<inputs>
Pídeme: el wordmark en una sola palabra (recomendado: «atiende.», que es un verbo y dice lo que hace); 6-10 capturas reales de la demo y del panel de contactos (si no las hay, recrea la interfaz en HTML con los textos y colores de abajo); una pista libre de derechos de unos 120 BPM y al menos 1:30, con drop y un breakdown tranquilo (Mixkit, uso comercial gratuito); y un clip gratuito de stock de un mostrador de recepción a oscuras, de noche, con un móvil que se ilumina sobre la mesa (Pexels).
</inputs>

<direction>
Película de lanzamiento al estilo de una keynote de Apple, solo 2D y en un único plano continuo: cada escena sale de la anterior, sin fundidos, desenfoques ni cortes. Las cosas se transforman unas en otras. Los textos suben desde una línea de máscara, los iconos brotan desde cero con efecto muelle, las barras se dibujan de lado a lado, las páginas empujan hacia delante y una forma negra llena la pantalla antes de encogerse en la escena siguiente.
Fondo blanco roto cálido (#FAFAF7), interfaz en negro tinta (#0A0A0A) y un único acento naranja mandarina (#FF6A2B) solo para badges, confirmaciones y el punto del wordmark. Liquid glass de iOS 26 sobre la interfaz y el vídeo. Archivo (ancho 125, peso 800) para el wordmark, Inter Tight para la interfaz y JetBrains Mono para horas y datos.
Un cursor dispara cada cambio con clics, arrastres y pulsaciones largas reales. La cámara hace zoom al estilo Screen Studio para que cada momento llene el encuadre vertical, y el cursor escala con ella.
Cada función se presenta con un titular corto que sube desde la máscara (2-4 palabras, Inter Tight 800) y se transforma en el siguiente elemento, nunca con un fundido.
Prohibido: fundidos encadenados, entradas con desenfoque, «revelados» por brillo, giros 3D, partículas, brillos, pausas de más de 1 s y cualquier cosa que huela a plantilla.
</direction>

<truth>
Solo funciones reales del recepcionista:
- responde con la información del negocio (horarios, precios, servicios);
- consulta huecos libres y reserva, cambia o cancela citas (una sola cita por hueco);
- entiende notas de voz;
- apunta en lista de espera cuando no hay hueco;
- contesta en el idioma de quien escribe;
- pasa a una persona las urgencias, con un resumen, y se pausa;
- guarda el contacto en el CRM sin duplicarlo;
- canales: web, WhatsApp, Instagram y email;
- cada acción queda registrada.
Etiquetas literales de la interfaz: «Consulta de información», «Hueco comprobado», «Cita reservada», «Cita cambiada», «Contacto guardado», «En lista de espera», «Pasado a una persona».
Datos ficticios: Clínica Veterinaria Olivo, mascotas «Kira» y «Bruno». Ningún cliente real ni dato personal. Sin URL. Llamada a la acción final: «Pide tu demo».
</truth>

<structure>
120 BPM, 160 pulsos (1:20), con algo pasando en cada pulso. Vertical 1080×1920; toda la acción dentro de la zona segura (deja libres los 220 px de arriba y los 380 px de abajo). Ajusta los límites de cada tramo a los tiempos medidos de la pista: el drop, el breakdown y la vuelta del ritmo mandan.

1 · Apertura (pulsos 1-16): el wordmark «atiende.» se comprime como un acordeón dentro de su propio punto. El punto se expande en una píldora negra y dentro sube «23:47 · recepción cerrada». Sobre la píldora brota un badge que cuenta mensajes, uno por pulso (1→6), cada uno con el icono de su canal asomando.

2 · Canales (17-24): clic: seis láminas de iris se cierran sobre la etiqueta y se abren de golpe sobre una conversación. El círculo se convierte en una tarjeta de chat y encoge. Detrás se despliega una cuadrícula como un mapa de papel (centro, cruz, esquinas): web, WhatsApp, Instagram, email, agenda y CRM. Se reordena en mosaico y un clic hace zoom en WhatsApp, aterrizando justo en el DROP.

3 · Contesta y agenda (25-56): llega «¿Tenéis hueco mañana para vacunar a Kira?». Brota el chip «Consulta de información» y la respuesta con el precio sube desde la máscara. El chip se derrite en una gota que se estira hasta formar una barra de herramientas de cristal (información, agenda, CRM, persona). El icono de agenda la convierte en un deslizador de horas (16:30 · 17:15 · 18:00). Al arrastrar, el pomo sostenido se convierte en una lupa de cristal sobre 17:15. Suelta: «Cita reservada ✓». Un segundo cursor fantasma intenta coger el mismo hueco y rebota contra un candado: «Un hueco, una cita».

4 · Entiende audios (57-72): la lupa sube como un orbe de cristal y crece hasta una pantalla de bloqueo con un reloj de cristal (00:32). La barra de inicio se estira en un reproductor de nota de voz: la onda bota al pulso y se convierte en texto que sube desde la máscara («¿Me pasas la cita de Bruno al viernes?»). La tarjeta se arrastra de JUE a VIE: «Cita cambiada ✓».

5 · Idiomas y lista de espera (73-88): el reloj se funde en una burbuja de cristal donde la palabra cambia letra a letra en cada pulso: Hola → Hi! → Ciao. La burbuja cae sobre la fila «Sábado», que se llena de negro hasta «Completo». El cursor pulsa «Avisarme» y una ficha sube a la lista de espera con un contador que salta a +1: «En lista de espera ✓».

6 · Sabe cuándo parar (89-100): la ficha se estira en un mensaje urgente («Mi perro se ha comido uvas»). El borde de la forma negra se vuelve rojo (#E5383B) y brota «Pasado a una persona». Una tarjeta de resumen se despliega como un acordeón y un interruptor de cristal pone el asistente «En pausa».

7 · Tu CRM (101-124): la escena retrocede y revela un móvil; el bisel crece desde el borde de la pantalla. La Dynamic Island se estira como un líquido, se separa, cruza volando y se expande en una ventana de ordenador con el CRM. Pulsación larga sobre la conversación y arrastre a la ventana: al soltar se convierte en la ficha de contacto. Los campos se dibujan uno por pulso: Interés · Canal · Estado: interesado; después «Sin duplicados ✓». Scroll: la ficha se transforma en el registro de actividad y cada fila brota con su etiqueta y su hora.

8 · Con control (125-136): una única forma negra que no deja de transformarse: Confirma antes de actuar ✓ → Una cita por hueco ✓ → Todo queda registrado ✓ → Activo 24/7 ✓.

9 · Mundo real (137-152, en el BREAKDOWN): el círculo final se expande hasta que el negro llena la pantalla, aguanta un pulso y se encoge sobre el clip real del mostrador a oscuras, con el móvil iluminándose. El mismo iris se abre sobre la pantalla del móvil y los contadores brotan uno por pulso: «Mientras dormías: 6 conversaciones · 2 citas · 1 en espera · 1 urgencia atendida», y se vuelve a cerrar.

10 · Cierre (153-160, con la VUELTA del ritmo): todo se contrae en la píldora, luego en el punto, y las letras de «atiende.» vuelven a brotar en el pulso de regreso. Debajo sube «Pide tu demo». El último fotograma es igual que el primero (salvo esa línea).
</structure>

<build>
1. Un solo HTML vertical de 1080×1920. Todo se calcula a partir del tiempo dentro de un async seek(t): sin transiciones CSS, sin temporizadores y sin estado que pase de un fotograma a otro. Expón window.videoSpec y window.renderReady.
2. Muelles con fórmula cerrada. Si un valor cambia de objetivo varias veces, suma un muelle por cada cambio para que siga siendo función del tiempo. Los contadores también.
3. Liquid glass: cada cristal lleva una copia de la escena que tiene detrás, deformada con un mapa de desplazamiento SVG (feImage con el campo de distancia de un rectángulo redondeado) en tres feDisplacementMap a escalas un poco distintas, más una luz de borde. Para el reloj de cristal, un campo de distancia por cifra hecho en canvas.
4. Efecto gota (goo): desenfoque más umbral de alfa, con el original encima para que el cristal siga nítido.
5. Iris de 6 láminas alrededor de una apertura hexagonal.
6. Compresión del wordmark: cada letra se acerca al punto en la misma proporción y se estrecha para seguir tocando a la siguiente.
7. Vídeo de stock: recodificado todo intra (ffmpeg -g 1), cargado como blob URL y esperando a «seeked» en cada fotograma.
8. Sonido: un efecto descargado (Mixkit) por cada evento, colocado por su pico medido.
   - Una lista única de eventos (tiempo, tipo) de la que salen a la vez la animación y los efectos.
   - La canción arranca en tiempo fuerte; el zoom a WhatsApp cae en el drop, el mundo real en el breakdown y el wordmark vuelve con el ritmo.
   - Si la pista es corta, se alarga repitiendo frases enteras de 8 compases, nunca a mitad de frase.
   - Normaliza a −14 LUFS.
9. Render con Playwright a 60 fps mezclando 4 subfotogramas por fotograma. Revisa un fotograma por pulso y busca saltos de un solo fotograma.
</build>

<gotchas>
- backdrop-filter: url() no aplica bien los mapas de desplazamiento en Chromium: clona la escena.
- Una inundación de color tiene que pasar de las esquinas y durar unos 0,3 s.
- Un hijo con visibility: visible se ve a través de un padre oculto: usa inherit.
- El texto que cambia dentro de una forma que se transforma necesita su propia máscara.
- Chrome varía el antialiasing del texto entre dos capturas iguales: compara fotogramas con tolerancia, no byte a byte.
- Horas y contadores en JetBrains Mono, para que no bailen.
- Los iconos de canal son simplificados, no logos oficiales.
</gotchas>

<start>
Pídeme los inputs y después enséñame el mapa de pulsos y 6 fotogramas (apertura, contesta y agenda, entiende audios, tu CRM, con control, mundo real) antes de escribir la película entera.
</start>
```
