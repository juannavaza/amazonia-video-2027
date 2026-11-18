# Prompts rápidos

Son prompts que se han usado en producciones reales con esta skill. Solo se han cambiado los nombres de productos y marcas por `[corchetes]`. Cópialos, rellena los corchetes y pégalos en la pestaña **Code** de Claude, con la sesión abierta en la carpeta de tu proyecto.

No hace falta escribir bien ni técnico: la skill hace las preguntas que faltan y te enseña una prueba antes del vídeo largo.

---

## 1 · Dale el material primero

Antes de pedir el vídeo, haz que Claude lea todo lo que hay sobre lo que quieres enseñar. Cuanto más real sea el material, menos se inventa.

```text
Busca toda la información que tienes de [producto] en [el repositorio de GitHub / esta carpeta / esta web / Notion / Drive]. Resúmeme qué hace de verdad, para quién es y qué se puede enseñar en pantalla.
```

---

## 2 · El primer vídeo (largo, que se entienda todo)

```text
Con toda la información que tienes de [producto], utiliza la skill crear-videos-con-codigo para generar el mejor vídeo posible. Tiene que ser largo y que se entienda todo lo que hace. Tiene que tener sonido y todo también.
```

---

## 3 · La versión para redes (vertical, muy dinámica)

Este es el prompt que mejor funcionó para pasar de «vídeo explicativo» a «vídeo que para el scroll». Fíjate en tres cosas: la sincronía del sonido, la duración máxima y los 3 primeros segundos.

```text
Ahora hazme otro que sea mucho más dinámico y en vertical para redes sociales. Tiene que ser muy llamativo, y la música y los efectos de sonido tienen que ir ajustados a los movimientos y a cada una de las imágenes, transiciones, etcétera. O sea, que los golpes de sonido tengan sentido con lo que se ve en la imagen. Tiene que ser muy atractivo y muy dinámico, para que la gente, en un máximo de 2 minutos, pueda ver realmente el potencial de todo esto. Que sea muy movido y dé la sensación de ser muy profesional. Es importante que en los primeros 3 segundos llame la atención.
```

---

## 4 · Copiar el estilo de un vídeo que te ha gustado

Si ves en X o en LinkedIn un vídeo hecho con código y su autor comparte el prompt, no lo copies tal cual: pide que te adapte la **estructura** a tu producto.

```text
Te voy a dar el prompt de un vídeo que he visto y que ha quedado espectacular. Ajusta lo que hemos hecho a este estilo de prompt y crea algo parecido pero con [producto]. Dame primero el prompt entero para poder pegarlo en otra conversación:

[pega aquí el prompt]
```

Y si se queda corto:

```text
Puedes hacerlo más largo si quieres. Hazlo lo largo que consideres para que se vea todo lo que hace.
```

---

## 5 · Reutilizar un prompt que ya te funcionó

```text
Te voy a dar un prompt que me sirvió muchísimo para hacer un vídeo explicativo sobre otra cosa. Quiero utilizar esta estructura de prompt: coge simplemente la estructura, obviamente no el contenido. Adapta todo el contenido para hacer un vídeo de [tema] con todo lo que hemos hablado. Primero devuélveme el prompt adaptado y explícamelo todo. Después, en otra sesión, crearé el vídeo con código.

[pega aquí el prompt]
```

Las plantillas `02` a `04` de esta carpeta son justo eso: estructuras probadas para que las adaptes.

---

## 6 · Arrancar la producción con un prompt largo

```text
Crea este vídeo en [carpeta del proyecto]:

[pega aquí el prompt de película]
```

La skill te pedirá los inputs (logo, capturas, música, clip) y te enseñará el mapa de pulsos y unos fotogramas clave antes de escribir la película entera.

---

## 7 · Afinar el gancho

El gancho es lo que más se itera. Pídelo concreto: qué tiene que salir y por qué.

```text
Es importante que el hook sea muy bueno. Como vamos a hablar de [herramienta o marca], es importante que también salga al principio, junto a [tu marca]. Arréglatelo de la mejor manera posible para que el hook visual sea muy, muy bueno y retenga.
```

Cuando te convenza:

```text
El hook me vale: produce la película vertical entera con este arranque.
```

---

## 8 · Variantes y autonomía

```text
Ahora saca la versión horizontal 1920×1080 del mismo código, recomponiendo el encuadre: no estires ni recortes la vertical.
```

```text
Tira hasta el final con lo que tú creas conveniente.
```

Úsalo cuando ya hayas aprobado la dirección y no quieras más preguntas.

---

## Variantes nuevas para probar

Estas no salen de producciones anteriores: son puntos de partida sugeridos para otros tipos de vídeo que cubre la skill.

**Explicar un repositorio de GitHub**
```text
Lee el repositorio [URL o carpeta] y usa la skill crear-videos-con-codigo para hacer un vídeo de 60 segundos que explique qué hace y por qué es útil, para gente que no programa. Enséñame solo lo que esté implementado de verdad, no el roadmap.
```

**Demo de una app con capturas reales**
```text
En [carpeta] tienes capturas reales de [app]. Usa crear-videos-con-codigo para hacer una demo vertical de 45 segundos: problema, acción en la app, resultado y llamada a la acción. Anima las capturas con zoom y cursor; no inventes pantallas que no estén en las capturas.
```

**Datos que cuentan una historia**
```text
Con los datos de [fichero.csv], usa crear-videos-con-codigo para hacer un vídeo de 30 segundos que cuente una sola conclusión. Las barras y los números se transforman unos en otros, con las unidades siempre visibles. Música tranquila, sin efectos en cada barra.
```

**Anuncio con tu propia voz**
```text
Tengo esta locución grabada: [audio.wav]. Usa crear-videos-con-codigo para montar encima un anuncio vertical de motion graphics. Mide la voz antes de cerrar tiempos: cada idea que digo tiene que aparecer en pantalla justo cuando la digo.
```
