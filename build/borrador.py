"""Borrador (animatic) · Amazonia Propuesta Digital 2027.

Genera un tramo por slide en borrador/tramos/sNN.mp4 y los une en borrador/amazonia_2027_borrador_v1.mp4.

Uso:
  .venv/bin/python -I build/borrador.py                 # todos los tramos + unión
  .venv/bin/python -I build/borrador.py s06 s13         # solo esos tramos + unión
  .venv/bin/python -I build/borrador.py --sin-etiqueta  # sin el rótulo «S06 · Street» de arriba a la izquierda
  .venv/bin/python -I build/borrador.py --frames s01:2,s06:3   # solo PNG de revisión (borrador/frames/)
  .venv/bin/python -I build/borrador.py --solo-unir     # vuelve a unir los tramos que ya existen

Para sustituir un hueco por la pieza real, rellena "ruta" en la tabla TRAMOS (vídeo o imagen) y regenera ese tramo.
El material vertical se encaja entero dentro del hueco sobre fondo verde (nunca se recorta).
"""
import json, math, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops, ImageFilter

import os
VOCES = {"alba": ("audio", "_alba"), "juaniyo": ("audio/juaniyo", "_juaniyo")}   # carpeta de pistas y sufijo de salida
VOZ = sys.argv[sys.argv.index("--voz") + 1] if "--voz" in sys.argv else "alba"   # voz elegida: Alba
os.environ["AMAZONIA_AUDIO"] = VOCES[VOZ][0]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fase1 as A   # animaciones finales de las slides 12-17 y 24, fuentes y utilidades
from fase1 import F, GREEN, CREAM, YELLOW, BLACK, seg, eo, eio, mix, draw_text, cap_h, text_w

ROOT = A.ROOT
OUTDIR = ROOT / "borrador"
# --hq: exportación de alta calidad desde las fuentes (30 fps, CRF 18, preset slow; audio sin pérdidas
# en los tramos y una sola codificación AAC al final). No toca los tramos ni el MP4 normales.
HQ = "--hq" in sys.argv
TRAMOS_DIR = OUTDIR / ("tramos" + VOCES[VOZ][1] + ("_hq" if HQ else ""))
FINAL = OUTDIR / f"amazonia_2027_borrador_v5{VOCES[VOZ][1]}{'_HQ' if HQ else ''}.mp4"
W, H, FPS = 1920, 1080, (30 if HQ else 25)
VCODEC = ["-c:v", "libx264", "-preset", "slow", "-crf", "18"] if HQ else ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20"]
EXT = ".mov" if HQ else ".mp4"   # en HQ el audio de cada tramo va en PCM (sin pérdidas) dentro de .mov
HUECO = (0x3D, 0x4A, 0x31)
PRE, POST = 0.5, 0.7          # silencio antes y después de la voz
FUNDIDO = 0.15                # fundido de entrada y de salida de cada tramo (0,3 s entre tramos)
GRID_ANTIGUO = OUTDIR / "entradas/grid_antiguo_v2.png"
MUSICA = ROOT / "audio/musica/same_kind_of_paradise_borrador.wav"   # Artlist · Dan Zeitune · licencia de la cuenta de Artlist del cliente · "" = sin música
MUSICA_DB = 8.0                                       # +8 dB sobre -36 LUFS → música a -28 LUFS (12 dB por debajo de la voz)
CAJA_SUB = (0x2F, 0x3B, 0x26, 225)                    # caja verde detrás del subtítulo blanco

# Paleta: manda el beige de marca; el verde se intercala en los tramos de cifras/pregunta y en portada y cierre
VERDES = {"s02", "s13", "s15", "s18b", "s03", "s19", "s01", "s12", "s14", "s16", "s17", "s30", "s31", "s32"}
def tema(k): return "verde" if k in VERDES else "crema"

# ------------------------------------------------------------------ guion (tal cual la tabla «Guiones»)
GUION = {
    "s01": "Amazonia en 2027. Es otra historia.",
    "s02": "A inicios de 2025, Amazonia tenía 185 seguidores en Instagram y ninguna cuenta en TikTok.",
    "s03": "Desde abril de 2025, empezamos a contar otra historia.",
    "s04": "Identidad. Contenido propio. TikTok. Influencers. Paid media. Comunidad. Seis palancas para darle la vuelta a la cuenta.",
    "s05": "Creamos una identidad propia y adaptamos la nueva imagen al entorno digital: un código visual que se reconoce en Instagram y TikTok.",   # nueva (17/11/2026)
    "s06": "Salimos a la calle con el producto y pusimos a gente real delante de la marca.",
    "s07": "Recetas con el producto como protagonista: Platanitos y agua de coco en momentos de consumo reales.",
    "s08": "Abrimos TikTok desde cero, con formatos propios de la plataforma. Hoy, 7.823 seguidores.",
    "s09": "Elegimos a los mejores creadores para llevar Amazonia a nuevas audiencias. Esta colaboración llegó a 847.000 reproducciones.",
    "s10": "Paid media. En 2025, campañas de awareness para darnos a conocer. En 2026, introducimos campañas de interacción para empezar a construir comunidad.",   # nueva (17/11/2026)
    "s11": "Activamos a la comunidad con dinámicas y sorteos. El único premio, nuestro propio producto. Y lo más importante: los seguidores que ganamos se quedan.",   # nueva (17/11/2026)
    "s12": "Y los resultados llegaron.",
    "s13": "53,5 millones de impactos y 200.367 interacciones. 18.011 seguidores en Instagram, y 7.823 en TikTok, partiendo de cero.",   # nueva (11/11/2026)
    "s14": "El encargo de notoriedad está cumplido.",
    "s15": "Los impactos al mes se multiplican por tres. Las interacciones, por siete. Y el engagement rate, por dos coma cuatro.",   # nueva (17/11/2026)
    "s16": "Y en 2027, ¿qué pasa?",
    "s17": "En 2027 pasamos de notoriedad a comunidad.",
    "s18": "Esa comunidad ya existe. Nos escribe, comenta y participa sin sorteo de por medio. Ahora toca potenciarla.",
    "s18b": "Hoy, el contenido de las marcas se ve más que nunca, pero se responde menos. Las audiencias no están saturadas: están aburridas.",   # 18/11, grabada
    "s18c": "Lo que funciona: cercanía y realismo, una comunidad que participa, creadores que multiplican la interacción y experiencias físicas.",   # 18/11, grabada
    "s19": "¿Cómo lo haremos? Con cinco palancas para construir comunidad.",   # 17/11, PENDIENTE de grabar
    "s19a": "Caras y un host en la calle: gente real, con rostro y emoción, y un presentador fijo que conversa en la calle y en redes.",   # palanca 1 (17/11), PENDIENTE de grabar
    "s19b": "Una comunidad que participa: la gente decide con votaciones de sabores, retos y comentarios que se convierten en contenido.",   # palanca 2 (17/11), PENDIENTE de grabar
    "s19c": "Paid en dos: notoriedad e interacción, medidas por separado.",   # palanca 3 (17/11), PENDIENTE de grabar
    "s19d": "Embajadores todo el año: caras reconocibles que asociaremos con Amazonia.",   # palanca 4 (17/11), PENDIENTE de grabar
    "s19e": "Amazonia Club, Friends First: un espacio propio donde la comunidad tiene prioridad. Y activaciones para pasar del feed a la quedada: running, yoga y deporte en grupo.",   # palanca 5 (17/11), PENDIENTE de grabar
    "s20": "Mismos modelos reales, ahora con rostro y emoción.",
    "s21": "Una cara fija que conversa en la calle y en redes: el host de Amazonia.",
    "s22": "Los mismos creadores durante doce meses, para que la gente los asocie a Amazonia.",
    "s23": "La comunidad decide. Dos sabores, dos creadores, y cada comentario es un voto.",
    "s24": "Notoriedad e interacción, medidas por separado.",
    "s25": "El sampling ya no basta. Las marcas están creando clubs: running, yoga, deporte en grupo.",
    "s26": "Amazonia Club, Friends First. Un espacio propio donde la comunidad tiene prioridad.",
    "s27": "Marcas en las que nos tenemos que fijar.",
    "s29": "La Generación Z ha cambiado el plan. Menos copas y más quedadas. Es el momento de Amazonia.",
    "s30": "En 2027, Amazonia es otra historia.",
}

# ------------------------------------------------------------------ TABLA DE TRAMOS
# audio: archivo en ./audio/ ("" = falta la locución → tramo mudo con duración estimada)
# huecos: cada uno con su rótulo de hueco, un pie opcional (rótulo de la pieza) y "ruta" de la pieza real.
#   formato "9:16" (por defecto) o "16:9". En "ciclo": True los huecos se muestran de uno en uno, frase a frase.
def H_(label, pie=None, ruta="", formato="9:16", cuenta=None):
    """cuenta=(valor, rótulo): el pie se convierte en un contador que sube desde 0 al entrar las piezas."""
    return {"label": label, "pie": pie, "ruta": ruta, "formato": formato, "cuenta": cuenta}

TRAMOS = {
    "s01": {"nombre": "Portada", "audio": "", "dur_estimada": 4.3, "local": "s01"},   # solo texto animado (versión con los cortes del Manifiesto descartada)
    "s02": {"nombre": "Grid 2024", "audio": "s02_v01_grid_2024.mp3", "local": "s02"},   # cifras grandes (antes: scroll del grid)
    "s03": {"nombre": "Transición grid", "audio": "s03_v01_transicion_grid.mp3", "local": "s03"},   # texto grande
    "s04": {"nombre": "Palancas", "audio": "s04_v01_montaje_palancas.mp3", "ciclo": True, "omitir": True,   # quitado del montaje a petición del cliente
            "huecos": [H_("IDENTIDAD · PENDIENTE"), H_("CONTENIDO PROPIO · PENDIENTE"), H_("TIKTOK · PENDIENTE"),
                       H_("INFLUENCERS · PENDIENTE"), H_("PAID MEDIA · PENDIENTE"), H_("COMUNIDAD · PENDIENTE")]},
    "s05": {"nombre": "Grid antes / después", "palanca": ("1.", ["IDENTIDAD", "PROPIA"], None), "audio": "s05_v01_grid_antes_despues.mp3", "local": "s05",   # mockup de dos teléfonos
            "huecos": [H_("GRID ANTES", "ANTES", ruta=str(GRID_ANTIGUO)), H_("GRID DESPUÉS · PENDIENTE", "DESPUÉS")]},
    "s06": {"nombre": "Street", "palanca": ("2.", ["CONTENIDO", "PROPIO"], "EN LA CALLE"), "audio": "s06_v01_street.mp3",
            # cortes: oct 11-13 s · maxi 12-14 s · agosto 3-5 s (arrancan al entrar las piezas y congelan el último plano)
            # cuenta 3.500: cifra PROVISIONAL a petición del cliente (pendiente de los datos reales de cada vídeo)
            "huecos": [H_(f"STREET {i}", "reproducciones", ruta=str(OUTDIR / f"entradas/s06_street{i}.mp4"),
                          cuenta=(3500, "reproducciones")) for i in (1, 2, 3)]},
    "s07": {"nombre": "Recetas", "palanca": ("2.", ["CONTENIDO", "PROPIO"], "RECETAS"), "audio": "s07_v01_receta.mp3",
            # cortes de: receta_amazonia_sept (final con Platanitos y brindis, desde 18,6 s; 17/11) · Receta-platanitos · cafe amazonia mayo. Cifras 3.500 PROVISIONALES
            "huecos": [H_("RECETA + GUARDADOS", ruta=str(OUTDIR / "entradas/s07_receta1.mp4"), cuenta=(3500, "guardados")),
                       H_("RECETA PLATANITOS", ruta=str(OUTDIR / "entradas/s07_receta2.mp4"), cuenta=(3500, "reproducciones")),
                       H_("RECETA AGUA DE COCO", ruta=str(OUTDIR / "entradas/s07_receta3.mp4"), cuenta=(3500, "reproducciones"))]},
    "s08": {"nombre": "TikTok", "palanca": ("3.", ["TIKTOK"], None), "audio": "s08_v01_tiktok.mp3", "local": "s08",
            # mockup de app: feed con «GIF LATAS AMAZONIA V2» (1 s → final) y, en «Hoy», perfil con 0 → 7.823 seguidores
            "huecos": []},
    "s09": {"nombre": "Colaboraciones", "palanca": ("4.", ["INFLUENCERS"], None), "audio": "s09_v01_colab.mp3", "local": "s09",
            # colaboración de @jordirodriguezmoreno (descargada de TikTok), 0:00-0:04, en el feed + 1.200.000 reproducciones
            "huecos": []},
    "s10": {"nombre": "Paid", "palanca": ("5.", ["PAID", "MEDIA"], None), "audio": "s10_v01_paid.mp3", "local": "s10",
            # sin piezas: texto 2025 → 2026 del cliente; locución regrabada (15,7 s), columnas sincronizadas con los años
            "huecos": []},
    "s11": {"nombre": "Sorteos", "palanca": ("6.", ["COMUNIDAD"], None), "audio": "s11_v01_sorteo.mp3", "local": "s11",
            # 3 sorteos (imágenes) + texto literal del cliente; locución regrabada (21,8 s) y sincronizada
            "huecos": []},
    "s12": {"nombre": "Resultados", "audio": "s12_v01_contador_53M.mp3", "local": "s12"},   # solo texto; las cifras van en S13
    "s13": {"nombre": "Contadores", "audio": "", "dur_estimada": 6.0, "local": "s13"},   # 17/11: sin locución (solo música); antes s13_v01_contadores.mp3   # maqueta de la diapositiva + 200.367 interacciones
    "s14": {"nombre": "Notoriedad cumplida", "audio": "s14_v01_rafaga_cifras.mp3", "local": "s14"},   # antes: ráfaga de cifras (obsoleta)
    "s15": {"nombre": "Crecimiento", "audio": "s15_v01_barra_impactos.mp3", "local": "s15"},   # impactos, interacciones y ER 2025 → 2026; voz regrabada
    "s16": {"nombre": "Pregunta", "audio": "s16_v01_pregunta.mp3", "local": "s16"},   # año en cuentakilómetros 2025→2027 + pregunta escrita
    "s17": {"nombre": "Notoriedad → comunidad", "audio": "s17_v01_notoriedad_comunidad.mp3", "anim": "s17"},   # letra a letra (la versión con sellos, s17 local, se descartó: «antes era más elegante»)
    "s18": {"nombre": "Comentarios y DM", "audio": "s18_v01_comentarios_dm.mp3", "local": "s18",   # citas reales sin @
            "huecos": []},
    "s18b": {"nombre": "Contexto · atención", "audio": "s18b_v01.mp3", "local": "s18b"},   # 17/11 · IAB Spain + Epsilon
    "s18c": {"nombre": "Contexto · qué funciona", "audio": "s18c_v01.mp3", "local": "s18c"},   # 18/11: sin voz hasta grabar la nueva (la anterior: s18c_v01.mp3)
    "s19": {"nombre": "Cómo lo haremos", "audio": "", "dur_estimada": 4.5, "local": "s19",   # 17/11: voz nueva PENDIENTE (antes s19_v01_montaje_5_palancas.mp3)   # índice 01–05 sincronizado
            "huecos": []},
    "s19a": {"nombre": "Palanca 1", "audio": "s19a_v01.mp3", "local": "s19a"},   # 18/11 · voz de Alba
    "s19b": {"nombre": "Palanca 2", "audio": "s19b_v01.mp3", "local": "s19b"},   # 18/11 · voz de Alba
    "s19c": {"nombre": "Palanca 3", "audio": "s19c_v01.mp3", "local": "s19c"},   # 18/11 · voz de Alba
    "s19d": {"nombre": "Palanca 4", "audio": "s19d_v01.mp3", "local": "s19d"},   # 18/11 · voz de Alba
    "s19e": {"nombre": "Palanca 5", "audio": "s19e_v01.mp3", "local": "s19e"},   # 18/11 · voz de Alba
    "s20": {"omitir": True, "nombre": "Antes / después caras", "audio": "s20_v01_antes_despues_caras.mp3",
            "huecos": [H_("PIEZA SIN CARA · PENDIENTE", "SIN CARA"), H_("PIEZA CON CARA · PENDIENTE", "CON CARA")],
            "palabra": ("emoción", "EMOCIÓN")},
    "s21": {"omitir": True, "nombre": "Host", "audio": "s21_v01_host.mp3",
            "huecos": [H_("STREET · HOST · PENDIENTE", "NUEVO: EL HOST DE AMAZONIA")]},
    "s22": {"omitir": True, "nombre": "Timeline embajadores", "audio": "s22_v01_timeline_embajadores.mp3",
            "huecos": [H_("TIMELINE EMBAJADORES · PENDIENTE")]},
    "s23": {"omitir": True, "nombre": "Votación (mockup)", "audio": "s23_v01_votacion.mp3",
            "huecos": [H_("CREADOR A · SABOR 1 · MOCKUP"), H_("CREADOR B · SABOR 2 · MOCKUP")]},
    "s24": {"omitir": True, "nombre": "Dos bolsas", "audio": "s24_v01_dos_bolsas.mp3", "anim": "s24"},
    "s25": {"omitir": True, "nombre": "Run club", "audio": "s25_v01_run_club.mp3",
            "huecos": [H_("RUN CLUB · PENDIENTE", "REFERENCIA")]},
    "s26": {"omitir": True, "nombre": "Web club", "audio": "s26_v01_web_club.mp3",
            "huecos": [H_("WEB CLUB · SCROLL · PENDIENTE", "ÚNETE AL CLUB")]},
    "s27": {"omitir": True, "nombre": "Referencias", "audio": "s27_v01_montaje_referencias.mp3",
            "huecos": [H_("REFERENCIAS DE MARCA · PENDIENTE")]},
    "s29": {"omitir": True, "nombre": "Gen Z", "audio": "s29_v01_genz.mp3",
            "huecos": [H_("GEN Z · ENTRENO Y TARDEO · PENDIENTE")]},
    "s30": {"omitir": True, "nombre": "Cierre", "audio": "s30_v01_loop_cierre.mp3",
            "huecos": [H_("LOOP CIERRE + LOGO · PENDIENTE", formato="16:9")], "capa_verde": 0.6},
    "s31": {"nombre": "Soñamos alto", "audio": "s31_v01.mp3", "local": "s31", "extra": .5,
            "musica_fuera": lambda: t_palabra("s31", "con", fin=True, defecto=2.2) - .6},   # la música de Artlist se apaga en los «…»   # voz de Alba hasta «…con»
    "s32": {"nombre": "Bad Gyal", "audio": "s32_v01.mp3", "extra": 5.9, "local": "s32",   # vídeo del cliente a 0,51× + «Fiebre»; USO INTERNO
            "huecos": []},
}
# orden del montaje (cambios del cliente): S15 va antes que S14
_ORDEN = ["s15", "s14"]
TRAMOS = {k: TRAMOS[k] for k in sorted(TRAMOS, key=lambda k: (k if k not in _ORDEN else min(_ORDEN), _ORDEN.index(k) if k in _ORDEN else 0))}

# ------------------------------------------------------------------ tiempos de la locución
def duraciones(k):
    """(duración del tramo, segundo en que empieza la voz, segundo en que acaba)."""
    t = TRAMOS[k]
    if t["audio"] and k in A.TIEMPOS:
        voz = A.TIEMPOS[k]["duracion"] - 1.0   # el MP3 lleva 0,5 s de silencio a cada lado
        return PRE + voz + POST + t.get("extra", 0), PRE, PRE + voz   # extra: segundos de lectura tras la voz
    d = t.get("dur_estimada", 4.0)
    return d, PRE, d - POST

def palabras(k):
    if k in TRAMOS and not TRAMOS[k].get("audio"): return []   # sección sin voz: tiempos por defecto
    if k not in A.TIEMPOS: return []
    if "palabras" in A.TIEMPOS[k]:   # sección regrabada aparte (build/sustituir_frase.py)
        return [dict(w=x["w"], s=x["s"] + PRE, e=x["e"] + PRE) for x in A.TIEMPOS[k]["palabras"]]
    a, b = A.TIEMPOS[k]["origen"]
    return [dict(w=x["w"], s=x["s"] - a + PRE, e=x["e"] - a + PRE) for x in A._PAL if a - .05 <= x["s"] < b]

def _letras(s): return len(re.sub(r"[^\wáéíóúñü]", "", s.lower()))

def frases(k):
    """[(inicio, fin, texto)] por frase del guion, alineadas con la voz por proporción de letras."""
    D, v0, v1 = duraciones(k)
    fr = re.split(r"(?<=[.?!])\s+", GUION[k].strip())
    ws = palabras(k)
    tot = sum(_letras(f) for f in fr)
    starts, acc = [], 0
    if ws:
        wl = [_letras(w["w"]) for w in ws]; wt = sum(wl)
        cum = [sum(wl[:i]) / wt for i in range(len(ws))]
        for f in fr:
            r = acc / tot
            i = next((j for j, c in enumerate(cum) if c >= r - 0.02), len(ws) - 1)
            starts.append(ws[i]["s"]); acc += _letras(f)
        end = ws[-1]["e"] + 0.3
    else:
        for f in fr:
            starts.append(v0 + (v1 - v0) * acc / tot); acc += _letras(f)
        end = v1 + 0.2
    return [(starts[i], starts[i + 1] if i + 1 < len(fr) else min(end, D - FUNDIDO), fr[i]) for i in range(len(fr))]

# ------------------------------------------------------------------ piezas reales
class Fuente:
    """Pieza real (imagen o vídeo) encajada entera en un rectángulo w×h sobre verde."""
    def __init__(self, ruta, w, h, dur):
        self.w, self.h, self.img, self.p, self.last = w, h, None, None, None
        ruta = Path(ruta)
        if ruta.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
            self.img = self._encaja(Image.open(ruta).convert("RGB"))
        else:
            vf = (f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0x2F3B26,"
                  f"fps={FPS},format=rgb24")
            self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-stream_loop", "-1", "-i", str(ruta), "-t", f"{dur + 1:.2f}",
                                       "-vf", vf, "-an", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    def _encaja(self, im):
        im.thumbnail((self.w, self.h), Image.LANCZOS) if im.width > self.w or im.height > self.h else None
        r = min(self.w / im.width, self.h / im.height)
        im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
        bg = Image.new("RGB", (self.w, self.h), GREEN); bg.paste(im, ((self.w - im.width) // 2, (self.h - im.height) // 2))
        return bg
    def frame(self):
        if self.img is not None: return self.img
        buf = self.p.stdout.read(self.w * self.h * 3)
        if len(buf) == self.w * self.h * 3: self.last = Image.frombytes("RGB", (self.w, self.h), buf)
        return self.last or Image.new("RGB", (self.w, self.h), GREEN)
    def close(self):
        if self.p: self.p.kill()

def existe(ruta): return bool(ruta) and Path(ruta).exists()

# ------------------------------------------------------------------ dibujo de huecos
def rect_mask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255); return m

def hueco_img(w, h, label, r=26):
    """Rectángulo redondeado verde claro con borde amarillo fino y el nombre de la pieza en Oswald amarilla."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([1, 1, w - 2, h - 2], radius=r, fill=HUECO, outline=A.ACC, width=3)
    partes = [p.strip() for p in label.split("·")]
    maxw = w - 56
    lines, cur = [], ""
    for p in partes:   # se parte por « · » y, si hace falta, por palabras
        t = (cur + " · " + p) if cur else p
        if text_w(t, F("o", 40, "SemiBold")) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = p
    lines.append(cur)
    size = min(44, min(A.fit("o", l, maxw, 44, "SemiBold") for l in lines))
    f = F("o", size, "SemiBold"); lh = size * 1.25
    y0 = h / 2 - (len(lines) - 1) * lh / 2 + cap_h(f) / 2
    for i, l in enumerate(lines):
        draw_text(d, w / 2, y0 + i * lh, l, f, A.ACC, anchor="ms", track=2)
    tag = "16:9" if w > h else "9:16"
    draw_text(d, w - 22, h - 20, tag, F("d", 22, "Medium"), mix(HUECO, A.ACC, .55), anchor="rs")
    return im

def slots(n, formato, gap=None):
    """Rectángulos (x, y, w, h) para n huecos en paralelo."""
    if formato == "16:9":
        return [(40, 40, W - 80, H - 80)]
    h = 690; w = round(h * 9 / 16); gap = gap or (70 if n == 3 else 140)
    tot = n * w + (n - 1) * gap; x0 = (W - tot) / 2
    return [(round(x0 + i * (w + gap)), 46, w, h) for i in range(n)]

def pie_contador(d, x, y, w, valor, rotulo, k, a=1.0):
    """Cifra grande que cuenta de 0 a valor (k de 0 a 1) con su rótulo debajo."""
    draw_text(d, x + w / 2, y + 12, A.es_num(round(valor * k)), F("o", 64, "Bold"), mix(A.BG, A.INK, a), tab=True, anchor="ms")
    draw_text(d, x + w / 2, y + 56, rotulo, F("d", 28, "Regular"), mix(A.BG, A.INK, .7 * a), anchor="ms")

def pie(d, x, y, w, texto, a=1.0):
    f = F("o", 34, "Medium")
    size = A.fit("o", texto, w + 120, 34, "Medium")
    draw_text(d, x + w / 2, y, texto, F("o", size, "Medium"), mix(A.BG, A.INK, a), anchor="ms", track=1)

# ------------------------------------------------------------------ animaciones propias del borrador
def t_palabra(k, w, fin=False, defecto=0.5):
    for p in palabras(k):
        if A._limpia(p["w"]) == A._limpia(w): return p["e"] if fin else p["s"]
    return defecto

# --- S05: grid antes / después dentro de dos teléfonos (mockup genérico, sin marca de fabricante)
PH_W, PH_H, PH_R, PH_B = 400, 800, 64, 16          # cuerpo del teléfono y grosor del marco
SC_W, SC_H = PH_W - 2 * PH_B, PH_H - 2 * PH_B
_TEL = {}

def _telefono():
    if "cuerpo" in _TEL: return _TEL
    pad = 60
    cuerpo = Image.new("RGBA", (PH_W + 2 * pad, PH_H + 2 * pad), (0, 0, 0, 0))
    sombra = Image.new("L", cuerpo.size, 0)
    ImageDraw.Draw(sombra).rounded_rectangle([pad + 10, pad + 30, pad + PH_W - 10, pad + PH_H + 10], PH_R, fill=90)
    cuerpo.putalpha(sombra.filter(ImageFilter.GaussianBlur(28)))
    sh = Image.new("RGBA", cuerpo.size, (40, 46, 32, 0)); sh.putalpha(cuerpo.getchannel("A")); cuerpo = sh
    d = ImageDraw.Draw(cuerpo)
    d.rounded_rectangle([pad, pad, pad + PH_W - 1, pad + PH_H - 1], PH_R, fill=(28, 30, 26, 255))
    d.rounded_rectangle([pad + 2, pad + 2, pad + PH_W - 3, pad + PH_H - 3], PH_R - 2, outline=(70, 74, 64, 255), width=2)
    for y0, y1 in ((150, 210), (240, 330)):        # botones laterales
        d.rounded_rectangle([pad - 4, pad + y0, pad + 1, pad + y1], 2, fill=(28, 30, 26, 255))
    d.rounded_rectangle([pad + PH_W - 1, pad + 200, pad + PH_W + 4, pad + 300], 2, fill=(28, 30, 26, 255))
    _TEL.update(cuerpo=cuerpo, pad=pad, mask=rect_mask(SC_W, SC_H, PH_R - PH_B))
    g = Image.open(GRID_ANTIGUO).convert("RGB")
    _TEL["grid"] = g.resize((SC_W, round(g.height * SC_W / g.width)), Image.LANCZOS)
    return _TEL

def _pantalla_pendiente():
    sc = Image.new("RGB", (SC_W, SC_H), (0x3D, 0x4A, 0x31)); d = ImageDraw.Draw(sc); f = F("o", 40, "Bold")
    for i, l in enumerate(("GRID ACTUAL", "PENDIENTE")):
        draw_text(d, SC_W / 2, SC_H / 2 - 10 + i * 56, l, f, A.ACC, anchor="ms", track=2)
    return sc

class _VideoPantalla:
    """Vídeo (grabación de pantalla) a tamaño de la pantalla del teléfono, ajustado a 'dur' segundos."""
    def __init__(self, ruta, dur, max_vel=None):
        self.ruta, self.dur, self.p, self.i, self.last = ruta, dur, None, -1, None
        src = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
                                   capture_output=True, text=True).stdout)
        self.factor = dur / src if not max_vel else max(dur / src, 1 / max_vel)   # como mucho max_vel× más rápido
    def _abre(self):
        if self.p: self.p.kill()
        vf = (f"setpts=PTS*{self.factor:.5f},fps={FPS},scale={SC_W}:{SC_H}:force_original_aspect_ratio=increase,"
              f"crop={SC_W}:{SC_H},format=rgb24")
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(self.ruta), "-vf", vf, "-an", "-f", "rawvideo", "-"],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL); self.i = -1
    def frame(self, t):
        n = max(0, round(t * FPS))
        if self.p is None or n < self.i: self._abre()
        while self.i < n:
            buf = self.p.stdout.read(SC_W * SC_H * 3)
            if len(buf) < SC_W * SC_H * 3: break
            self.last = Image.frombytes("RGB", (SC_W, SC_H), buf); self.i += 1
        return self.last or Image.new("RGB", (SC_W, SC_H), GREEN)

def _s05_tiempos(D):
    """Momentos clave de S05 (los usa también el audio para colocar los efectos)."""
    ts = t_palabra("s05", "adaptamos", defecto=D * .25) - .2   # «…y adaptamos la nueva imagen»: cambio al grid actual
    return {"titulo": TIT_T0, "mueve": TIT_MUEVE, "entra": TIT_CONTENIDO, "cambio": ts, "nuevo": ts + .15}

def _titulo_bloque(num, lineas, kicker=None):
    """Bloque de título (número en amarillo + líneas + antetítulo opcional) en RGBA, a tamaño grande; luego se escala."""
    fn, fl, fk = F("o", 230, "Bold"), F("o", 140, "Bold"), F("o", 64, "Medium")
    ws = [text_w(num, fn)] + [text_w(l, fl) + 4 * (len(l) - 1) for l in lineas] + ([text_w(kicker, fk) + 8 * len(kicker)] if kicker else [])
    h = cap_h(fn) + 60 + len(lineas) * (cap_h(fl) + 34) + (cap_h(fk) + 50 if kicker else 0)
    im = Image.new("RGBA", (round(max(ws) + 20), round(h + 40)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    draw_text(d, 0, cap_h(fn) + 10, num, fn, A.ACC)
    y = cap_h(fn) + 26
    for l in lineas:
        y += cap_h(fl) + 34; draw_text(d, 0, y, l, fl, A.INK, track=4)
    if kicker: draw_text(d, 2, y + 50 + cap_h(fk), kicker, fk, A.KICK, track=8)
    return im

_TIT = {}
def titulo_palanca(k):
    key = (k, A.BG)
    if key not in _TIT: _TIT[key] = _titulo_bloque(*TRAMOS[k]["palanca"])
    return _TIT[key]

TIT_ESCALA = .5
TIT_T0, TIT_MUEVE, TIT_CONTENIDO = .1, 1.15, 1.3   # entra · se coloca a la izquierda · aparecen las piezas

def dibuja_titulo(im, t, tb, x_der, cy, out=1.0):
    """Título de palanca: entra grande y centrado; luego se reduce y se coloca con su borde derecho en x_der."""
    ka = eo(seg(t, TIT_T0, TIT_T0 + .5)) * out
    if ka <= 0: return
    km = eio(seg(t, TIT_MUEVE, TIT_MUEVE + .55))
    sc = 1 + (TIT_ESCALA - 1) * km
    bw, bh = round(tb.width * sc), round(tb.height * sc); b = tb.resize((bw, bh), Image.LANCZOS)
    x0 = (W - bw) / 2 + ((x_der - bw) - (W - bw) / 2) * km
    y0 = (H - bh) / 2 + 40 * (1 - eo(seg(t, TIT_T0, TIT_T0 + .5))) + ((cy - bh / 2) - (H - bh) / 2) * km
    if ka < 1: b.putalpha(b.getchannel("A").point(lambda v: round(v * ka)))
    im.paste(b, (round(x0), round(y0)), b)

def sfx_palanca(D): return [(TIT_T0, "pop"), (TIT_MUEVE - .05, "whoosh_corto"), (TIT_CONTENIDO + .1, "pop")]

def s05(t, D):
    """Identidad: un solo teléfono. Primero el grid antiguo; sale, y entra el teléfono con el grid actual."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    T = _telefono(); pad = T["pad"]; tt = _s05_tiempos(D)
    out = 1 - seg(t, D - .4, D)
    top = 70; xc = W / 2 - PH_W / 2
    vid = next((x for x in sorted((ROOT / "material/s05_grid_antes_despues").glob("*"))
                if x.suffix.lower() in (".mov", ".mp4", ".m4v")), None)
    def pega(sc, x, y, a):
        tel = T["cuerpo"].copy()
        tel.paste(sc, (pad + PH_B, pad + PH_B), T["mask"])
        ImageDraw.Draw(tel).rounded_rectangle([pad + PH_W / 2 - 52, pad + PH_B + 14, pad + PH_W / 2 + 52, pad + PH_B + 44],
                                              15, fill=(12, 12, 12, 255))
        if a < 1: tel.putalpha(tel.getchannel("A").point(lambda v: round(v * a)))
        im.paste(tel, (round(x - pad), round(y - pad)), tel)
    fl = F("o", 52, "Medium"); ly = top + PH_H + 75
    # 0) título «1. IDENTIDAD PROPIA»: entra grande en el centro y se coloca a la izquierda del teléfono
    dibuja_titulo(im, t, titulo_palanca("s05"), xc - 90, top + PH_H / 2, out)
    # 1) ANTES: entra subiendo, hace scroll y sale por la izquierda
    k_in = eo(seg(t, tt["entra"], tt["entra"] + .6))
    k_out = eio(seg(t, tt["cambio"], tt["cambio"] + .45))
    a = k_in * (1 - k_out)
    if a > 0:
        g = T["grid"]; off = round((g.height - SC_H) * eio(seg(t, .8, tt["cambio"] + .3)))
        pega(g.crop((0, off, SC_W, off + SC_H)), xc, top + 60 * (1 - k_in) + 160 * k_out, a)
        draw_text(d, W / 2, ly + 160 * k_out, "ANTES", fl, mix(BG, INK, a), anchor="ms", track=8)
    # 2) DESPUÉS: entra desde la derecha con la grabación del grid actual
    k2 = eo(seg(t, tt["nuevo"], tt["nuevo"] + .55)) * out
    if k2 > 0:
        if vid:
            if "vid" not in _TEL or _TEL["vid"].ruta != vid:
                _TEL["vid"] = _VideoPantalla(vid, D - tt["nuevo"] - .4, max_vel=1.5)
            sc = _TEL["vid"].frame(max(0, t - tt["nuevo"]))
        else:
            sc = _pantalla_pendiente()
        pega(sc, xc + 700 * (1 - k2), top, k2)
        draw_text(d, W / 2 + 300 * (1 - k2), ly, "DESPUÉS", fl, mix(BG, INK, k2), anchor="ms", track=8)
    # 3) etiquetas INSTAGRAM · TIKTOK a la derecha del teléfono: se encienden cuando Alba las dice (17/11/2026)
    fp = F("o", 54, "Medium"); x0 = xc + PH_W + 110 + 700 * (1 - k2)   # se mueve con el teléfono al salir
    for j, (pal, txt) in enumerate((("instagram", "INSTAGRAM"), ("tiktok", "TIKTOK"))):
        tw = t_palabra("s05", pal, defecto=D - 1.6 + j * .6)
        kk = eo(seg(t, tw - .05, tw + .3)) * out
        if kk <= 0: continue
        w_ = text_w(txt, fp) + 6 * (len(txt) - 1) + 64; h_ = 84; y_ = top + PH_H / 2 - 110 + j * 130 + 20 * (1 - kk)
        d.rounded_rectangle([x0, y_, x0 + w_, y_ + h_], 42, fill=mix(BG, A.ACC, kk), outline=mix(BG, INK, kk), width=3)
        draw_text(d, x0 + 32, y_ + h_ / 2 + cap_h(fp) / 2, txt, fp, BG, track=6)
    return im

# --- S18b / S18c: contexto 2026 (Informe Marcas y Atención Social 2026, IAB Spain + Epsilon Technologies)
FUENTE_IAB = "Fuente: IAB Spain y Epsilon Technologies, Informe Marcas y Atención Social 2026 (1.163 marcas, ene-may 2026 vs. año anterior)"

def _fuente(d, t, D, txt=FUENTE_IAB):
    k = eo(seg(t, .6, 1.1)) * (1 - seg(t, D - .4, D))
    if k > 0: draw_text(d, 160, H - 40, txt, F("d", 24, "Regular"), mix(A.BG, A.INK, .55 * k))

S18B_FEED = ["s06_street1", "s07_receta2", "s09_colab1", "s06_street3", "s07_receta3", "s09_colab3",
             "s06_street2", "s07_receta1", "s09_colab2", "s08_tiktok1"]

def _s18b_feed():
    """Tira vertical de «posts» genéricos: fotogramas muy desenfocados (no se reconoce la marca) + interfaz de feed."""
    if "s18b_feed" in _TEL: return _TEL["s18b_feed"]
    tiles = []
    for j, n in enumerate(S18B_FEED * 2):
        src = OUTDIR / "entradas" / f"{n}.mp4"
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{1.0 + (j % 3) * .9:.2f}", "-i", str(src), "-frames:v", "1",
                            "-vf", f"scale={SC_W}:{SC_H}:force_original_aspect_ratio=increase,crop={SC_W}:{SC_H}",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
        im = Image.frombytes("RGB", (SC_W, SC_H), r.stdout) if len(r.stdout) == SC_W * SC_H * 3 else Image.new("RGB", (SC_W, SC_H), (60, 64, 50))
        im = im.filter(ImageFilter.GaussianBlur(16))
        im = Image.blend(im, Image.new("RGB", im.size, (20, 22, 18)), .25)
        d = ImageDraw.Draw(im); wh = (245, 242, 236)
        cx = SC_W - 40                                                   # columna de iconos
        hy = SC_H - 300
        d.ellipse([cx - 17, hy - 15, cx + 1, hy + 3], outline=wh, width=4); d.ellipse([cx - 1, hy - 15, cx + 17, hy + 3], outline=wh, width=4)
        d.polygon([(cx - 18, hy - 4), (cx + 18, hy - 4), (cx, hy + 18)], outline=wh)
        d.line([(cx - 16, hy), (cx, hy + 17), (cx + 16, hy)], fill=wh, width=4)
        d.rounded_rectangle([cx - 18, hy + 60, cx + 18, hy + 88], 10, outline=wh, width=4)
        d.polygon([(cx - 6, hy + 88), (cx - 12, hy + 98), (cx + 2, hy + 88)], fill=wh)
        d.polygon([(cx - 16, hy + 140), (cx + 18, hy + 128), (cx + 6, hy + 162)], outline=wh, width=4)
        d.ellipse([22, SC_H - 120, 62, SC_H - 80], fill=(200, 196, 188))           # usuario genérico
        d.rounded_rectangle([74, SC_H - 112, 74 + 120 + 30 * (j % 3), SC_H - 96], 8, fill=(220, 216, 208))
        d.rounded_rectangle([22, SC_H - 66, SC_W - 90, SC_H - 54], 6, fill=(170, 166, 158))
        d.rounded_rectangle([22, SC_H - 44, SC_W - 160, SC_H - 32], 6, fill=(170, 166, 158))
        tiles.append(im)
    _TEL["s18b_feed"] = tiles
    return tiles

def _s18b_scroll(t, tq):
    """Nº de posts recorridos: deslizamientos rápidos y seguidos; con «audiencias» el pulgar frena y se para."""
    t0, per = .35, .42
    n_rap = max(1, int((tq - t0) // per))
    if t < t0: return 0.0
    if t < t0 + n_rap * per:
        i, f = divmod(t - t0, per); return i + eio(min(1, f / (per * .7)))
    return n_rap + eo(min(1, (t - t0 - n_rap * per) / 1.1))            # último deslizamiento, lento

S18B_PLANO = "material/s18b_ia/scroll_sofa_1.mp4"   # 18/11: plano generado con IA (Higgsfield, Seedance 2.5)

S18B_PLANOS = [("material/s18b_ia/scroll_sofa_1.mp4", .21), ("material/s18b_ia/scroll_sofa_2.mp4", .10)]   # (plano, recorte)

def _s18b_frames(j=0):
    """Fotogramas de un plano IA (720p, 24 fps) en memoria; se escalan al pintar."""
    key = f"s18b_ia{j}"
    if key not in _TEL:
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ROOT / S18B_PLANOS[j][0]), "-t", "6", "-vf", "scale=1280:720",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
        b = 1280 * 720 * 3
        _TEL[key] = [Image.frombytes("RGB", (1280, 720), r.stdout[i * b:(i + 1) * b]) for i in range(len(r.stdout) // b)]
    return _TEL[key]

def _s18b_src(t, tq):
    """Tiempo del plano: va a 0,8× y, con «audiencias», frena hasta quedarse quieto (el pulgar se para)."""
    v, fr = .8, 1.0
    if t < tq: return v * t
    u = min(t - tq, fr)
    return v * tq + v * (u - u * u / (2 * fr))

S18B_VW, S18B_X0 = 1240, .21   # ancho del plano en pantalla y desde qué fracción del plano se recorta

def s18b(t, D):
    """18/11: a la izquierda, plano IA de alguien haciendo scroll aburrido en el sofá (tinte verde suave); a la derecha,
    panel verde con +17 % views y −16 % interacciones; con «audiencias» el plano frena y entra la frase."""
    BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .4, D)
    tv = t_palabra("s18b", "ve", defecto=.9) - .1
    ti = t_palabra("s18b", "responde", defecto=2.0) - .1
    tq = t_palabra("s18b", "audiencias", defecto=3.6) - .2
    tc = ti if len(S18B_PLANOS) > 1 else 99            # 18/11: prueba con las dos chicas; corte en «se responde menos»
    j, tl = (0, t) if t < tc else (1, t - tc)
    frs = _s18b_frames(j)
    fr = frs[min(len(frs) - 1, int(_s18b_src(tl, tq - (0 if j == 0 else tc)) * 24))].resize((1920, 1080), Image.BICUBIC)
    z = 1.0 + .05 * eo(t / D)
    fr = fr.transform((W, H), Image.AFFINE, (1 / z, 0, W / 2 - W / 2 / z, 0, 1 / z, H / 2 - H / 2 / z), resample=Image.BICUBIC)
    x0 = round(S18B_PLANOS[j][1] * 1920); fr = fr.crop((x0, 0, x0 + S18B_VW, H))
    fr = Image.blend(fr, Image.new("RGB", fr.size, BG), .18)
    im = Image.new("RGB", (W, H), BG)
    m = Image.new("L", (S18B_VW, H), 255); md = ImageDraw.Draw(m)
    for i in range(160): md.line([(S18B_VW - 160 + i, 0), (S18B_VW - 160 + i, H)], fill=round(255 * (1 - i / 160)))   # fundido al panel
    kv = eo(seg(t, 0, .6)) * out
    m = m.point(lambda v: round(v * kv))
    im.paste(fr, (0, 0), m)
    d = ImageDraw.Draw(im)
    ka = eo(seg(t, .15, .6)) * out
    xr = 1530
    draw_text(d, xr, 200, "EL CONTEXTO ACTUAL", F("o", 42, "Medium"), mix(BG, A.KICK, ka), anchor="ms", track=10)
    fn, fl = F("o", 200, "Bold"), F("o", 42, "Medium")
    for y, t0, v, lab in ((450, tv, 17, "VIEWS"), (720, ti, -16, "INTERACCIONES")):
        k = eo(seg(t, t0, t0 + .5)) * out
        if k <= 0: continue
        n = round(v * A.eo5(seg(t, t0, t0 + 1.0)))
        draw_text(d, xr, y + (25 if v < 0 else -25) * (1 - k), f"{'+' if n >= 0 else '−'}{abs(n)} %", fn, mix(BG, A.ACC, k), anchor="ms")
        lw_ = text_w(lab, fl) + 8 * (len(lab) - 1)
        draw_text(d, xr + 16, y + 66, lab, fl, mix(BG, INK, k), anchor="ms", track=8)
        ax = xr + 16 - lw_ / 2 - 36; ay = y + 66 - cap_h(fl) / 2; c = mix(BG, A.ACC, k)
        if v > 0: d.polygon([(ax, ay - 13), (ax - 15, ay + 11), (ax + 15, ay + 11)], fill=c)
        else: d.polygon([(ax, ay + 13), (ax - 15, ay - 11), (ax + 15, ay - 11)], fill=c)
    kq = eo(seg(t, tq, tq + .6)) * out
    if kq > 0:
        fq = F("d", 44, "Medium")
        for i, l in enumerate(("Las audiencias no están", "saturadas: están aburridas.")):
            draw_text(d, xr, 880 + i * 58 + 14 * (1 - kq), l, fq, mix(BG, INK, kq), anchor="ms")
        lw = 300 * eio(seg(t, tq + .6, tq + 1.3))
        d.rectangle([xr - lw / 2, 968, xr + lw / 2, 975], fill=mix(BG, A.ACC, out))
    _fuente(d, t, D)
    return im

def s18b_iphone(t, D):
    """18/11: más alcance, menos respuesta. iPhone con un feed genérico que pasa sin parar; a los lados +17 % views
    y −16 % interacciones; al decir «audiencias» el scroll frena y entra «no están saturadas: están aburridas»."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .4, D)
    tv = t_palabra("s18b", "ve", defecto=.9) - .1
    ti = t_palabra("s18b", "responde", defecto=2.0) - .1
    tq = t_palabra("s18b", "audiencias", defecto=3.6) - .2
    ka = eo(seg(t, .15, .6)) * out
    draw_text(d, W / 2, 105, "EL CONTEXTO ACTUAL", F("o", 46, "Medium"), mix(BG, A.KICK, ka), anchor="ms", track=10)
    # teléfono con el feed
    T = _telefono(); pad = T["pad"]; tiles = _s18b_feed()
    pos = _s18b_scroll(t, tq); i = int(pos); off = round((pos - i) * SC_H)
    sc = Image.new("RGB", (SC_W, SC_H)); sc.paste(tiles[i % len(tiles)], (0, -off)); sc.paste(tiles[(i + 1) % len(tiles)], (0, SC_H - off))
    tel = T["cuerpo"].copy(); tel.paste(sc, (pad + PH_B, pad + PH_B), T["mask"])
    esc = .82; tel = tel.resize((round(tel.width * esc), round(tel.height * esc)), Image.LANCZOS)
    kt = eo(seg(t, .1, .7)) * out
    if kt < 1: tel.putalpha(tel.getchannel("A").point(lambda v: round(v * kt)))
    ty = 150 + 50 * (1 - kt)
    im.paste(tel, (round(W / 2 - tel.width / 2), round(ty - pad * esc)), tel)
    # cifras a los lados
    fn, fl = F("o", 230, "Bold"), F("o", 46, "Medium")
    for x, t0, v, lab in ((W / 2 - 560, tv, 17, "VIEWS"), (W / 2 + 560, ti, -16, "INTERACCIONES")):
        k = eo(seg(t, t0, t0 + .5)) * out
        if k <= 0: continue
        n = round(v * A.eo5(seg(t, t0, t0 + 1.0)))
        draw_text(d, x, 560 + (25 if v < 0 else -25) * (1 - k), f"{'+' if n >= 0 else '−'}{abs(n)} %", fn, mix(BG, A.ACC, k), anchor="ms")
        draw_text(d, x, 640, lab, fl, mix(BG, INK, k), anchor="ms", track=8)
        ay = 700; c = mix(BG, A.ACC, k)                                   # flecha: sube / baja
        if v > 0: d.polygon([(x, ay), (x - 18, ay + 24), (x + 18, ay + 24)], fill=c)
        else: d.polygon([(x, ay + 24), (x - 18, ay), (x + 18, ay)], fill=c)
    kq = eo(seg(t, tq, tq + .6)) * out
    if kq > 0:
        fq = F("d", 50, "Medium")
        draw_text(d, W / 2, 935 + 14 * (1 - kq), "Las audiencias no están saturadas: están aburridas.", fq, mix(BG, INK, kq), anchor="ms")
        lw = 560 * eio(seg(t, tq + .6, tq + 1.3))
        d.rectangle([W / 2 - lw / 2, 962, W / 2 + lw / 2, 969], fill=mix(BG, A.ACC, out))
    _fuente(d, t, D)
    return im

S18C_BLOQUES = [("01", ["CERCANÍA E", "HIPERREALISMO"], "Contenido real que entretiene.", "cercanía"),
                ("02", ["UNA COMUNIDAD", "QUE PARTICIPA"], "Retos y votaciones en serie.", "comunidad"),
                ("03", ["CREADORES"], "Credibilidad y cercanía, con constancia: los mismos creadores durante todo el año.", "creadores"),
                ("04", ["EXPERIENCIAS", "FÍSICAS"], "La marca se vive, no solo se ve.", "experiencias")]   # 18/11: orden de las palancas

S18C_FUENTES = [("borrador/entradas/s06_street1.mp4", 0.0),                       # 18/11: real, street de Amazonia
                ("material/s18c_ia/bloque_2.mp4", 0.0),                          # IA (comunidad)
                ("material/s09_colaboraciones/colab_probandoconcali.mp4", 0.0),  # real, creadora con Platanitos
                ("material/s19_palancas/club_cupra.mp4", 13.0)]                  # real, run club de otra marca
S18C_TW, S18C_TH = 390, 440   # 18/11: plano IA vertical encima de cada bloque

def _s18c_clip(j):
    key = f"s18c_{j}"
    if key not in _TEL:
        src, ss = S18C_FUENTES[j]; f = ROOT / src
        if f.exists():
            r = subprocess.run(["ffmpeg", "-v", "error", "-stream_loop", "-1", "-ss", str(ss), "-i", str(f), "-t", "9", "-vf",
                                f"scale={S18C_TW}:{S18C_TH}:force_original_aspect_ratio=increase,crop={S18C_TW}:{S18C_TH}",
                                "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
            n = S18C_TW * S18C_TH * 3
            _TEL[key] = [Image.frombytes("RGB", (S18C_TW, S18C_TH), r.stdout[i * n:(i + 1) * n]) for i in range(len(r.stdout) // n)]
        else:
            ph = Image.new("RGB", (S18C_TW, S18C_TH), mix(A.BG, A.INK, .15))
            draw_text(ImageDraw.Draw(ph), S18C_TW / 2, S18C_TH / 2, "PLANO IA", F("o", 40, "Bold"), mix(A.BG, A.INK, .5), anchor="ms", track=4)
            _TEL[key] = [ph]
        _TEL.setdefault("s18c_mask", rect_mask(S18C_TW, S18C_TH, 22))
    return _TEL[key]

def s18c(t, D):
    """Lo que funciona (18/11): cuatro columnas; cada una entra con la voz con un plano IA vertical que se reproduce,
    y debajo titular + frase."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .4, D)
    ka = eo(seg(t, .15, .6)) * out
    draw_text(d, 160, 190 + 20 * (1 - ka), "LO QUE FUNCIONA", F("o", 100, "Bold"), mix(BG, INK, ka), track=4)
    defs = (1.0, 2.6, 4.0, 5.4)
    cw, gap, x0, yt = S18C_TW, 40, 160, 250
    fh, fs, fk = F("o", 42, "Bold"), F("d", 27, "Regular"), F("o", 38, "Bold")
    for j, (num, lin, sub, pal) in enumerate(S18C_BLOQUES):
        te = t_palabra("s18c", pal, defecto=defs[j]) - .15
        k = eo(seg(t, te, te + .5)) * out
        if k <= 0: continue
        x = x0 + j * (cw + gap)
        frs = _s18c_clip(j); fr = frs[min(len(frs) - 1, int(max(0, t - te) * 24))].copy()
        draw_text(ImageDraw.Draw(fr), 22, 22 + cap_h(fk), num, fk, (255, 255, 255), track=3)
        if k < 1: fr = Image.blend(Image.new("RGB", fr.size, BG), fr, k)
        im.paste(fr, (x, round(yt + 30 * (1 - k))), _TEL["s18c_mask"])
        y = yt + S18C_TH + 34 + 20 * (1 - k)
        d.rectangle([x, y, x + 60 * eio(seg(t, te, te + .5)), y + 6], fill=mix(BG, A.ACC, out))
        for i, l in enumerate(lin):
            draw_text(d, x, y + 34 + cap_h(fh) + i * (cap_h(fh) + 14), l, fh, mix(BG, INK, k), track=2)
        for i, l in enumerate(_parte(sub, fs, cw - 10)):
            draw_text(d, x, y + 34 + 2 * (cap_h(fh) + 14) + 44 + i * 36, l, fs, mix(BG, INK, .8 * k))
    _fuente(d, t, D)
    return im

def s18c_texto(t, D):
    """Lo que funciona: cuatro bloques que entran con la voz (anticipan las palancas 2027)."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .4, D)
    ka = eo(seg(t, .15, .6)) * out
    draw_text(d, 160, 300 + 20 * (1 - ka), "LO QUE FUNCIONA", F("o", 110, "Bold"), mix(BG, INK, ka), track=4)
    defs = (1.0, 2.6, 4.0, 5.4)
    cw, gap, x0, y0 = 390, 40, 160, 470
    fh, fs, fk = F("o", 44, "Bold"), F("d", 28, "Regular"), F("o", 40, "Medium")
    for j, (num, lin, sub, pal) in enumerate(S18C_BLOQUES):
        te = t_palabra("s18c", pal, defecto=defs[j]) - .15
        k = eo(seg(t, te, te + .5)) * out
        if k <= 0: continue
        x = x0 + j * (cw + gap); y = y0 + 20 * (1 - k)
        d.rectangle([x, y, x + 60 * eio(seg(t, te, te + .5)), y + 6], fill=mix(BG, A.ACC, out))
        draw_text(d, x, y + 70, num, fk, mix(BG, A.KICK, k), track=4)
        for i, l in enumerate(lin):
            draw_text(d, x, y + 150 + i * (cap_h(fh) + 16), l, fh, mix(BG, INK, k), track=2)
        for i, l in enumerate(_parte(sub, fs, cw - 10)):
            draw_text(d, x, y + 150 + 2 * (cap_h(fh) + 16) + 40 + i * 40, l, fs, mix(BG, INK, .8 * k))
    _fuente(d, t, D)
    return im

# --- S19a-S19e: una escena por palanca 2027 (número grande + titular + una frase), 17/11
S19_PALANCAS = {"s19a": ("1", ["CARAS Y HOST", "EN LA CALLE"], "Gente real, con rostro y emoción, y un presentador fijo que conversa en la calle y en redes."), "s19b": ("2", ["COMUNIDAD", "QUE PARTICIPA"], "La gente decide: votaciones de sabores, retos y comentarios que se convierten en contenido."), "s19c": ("3", ["PAID EN DOS"], "Notoriedad e interacción, medidas por separado."), "s19d": ("4", ["EMBAJADORES", "TODO EL AÑO"], "Embajadores, caras reconocibles que asociaremos con Amazonia."), "s19e": ("5", ["AMAZONIA", "CLUB"], "Un club propio donde la comunidad tiene prioridad: drops y ediciones limitadas, y experiencias de running, yoga y deporte en grupo.")}

_JOR = "material/s19_palancas/jordi_verano_familia.mp4"
_NES, _AMV = "material/s19_palancas/ref_nestea_ibangarcia.mp4", "material/s19_palancas/amazonia_verano_reel.mp4"
S19_CLIPS = {"s19a": [(_AMV, 10.0, 12.2), (_AMV, 24.0, 26.3), (_NES, 3.0, 5.3), (_NES, 12.0, 14.4)],
             "s19b": [(_AMV, 2.0, 4.2), (_AMV, 12.0, 15.0), (_AMV, 18.0, 21.0)],
             "s19d": [(_JOR, 84.0, 85.5), (_JOR, 92.0, 93.5), (_JOR, 124.0, 125.5), (_JOR, 140.0, 141.5)],
             "s19e": [("material/s19_palancas/club_oysho.mp4", 0.5, 2.0), ("material/s19_palancas/club_b3tter.mp4", 6.0, 7.5),
                      ("material/s19_palancas/club_cupra.mp4", 10.5, 12.0), ("material/s19_palancas/club_cupra.mp4", 20.0, 21.5)]}   # clubs de otras marcas (Oysho, run club, CUPRA)   # Jordi, «Un verano en familia» (colab real)   # pregunta al público + elegir sabor en la nevera   # 18/11: contenido real (host + caras riendo)

def _s19_clip(k):
    key = f"clip_{k}"
    if key not in _TEL:
        vf = f"scale={SC_W}:{SC_H}:force_original_aspect_ratio=increase,crop={SC_W}:{SC_H},fps=25,format=rgb24"
        frames = []; n = SC_W * SC_H * 3
        for src, a, b in S19_CLIPS[k]:
            r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", str(ROOT / src), "-vf", vf,
                                "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
            frames += [Image.frombytes("RGB", (SC_W, SC_H), r.stdout[i * n:(i + 1) * n]) for i in range(len(r.stdout) // n)]
        _TEL[key] = frames
    return _TEL[key]

def _s19b_extra(im, t, D, out):
    """Palanca 2: encuesta de sabores que se rellena sobre el teléfono + dos comentarios reales que saltan."""
    d = ImageDraw.Draw(im); tx0 = 480 - PH_W / 2 + PH_B; ty0 = (H - PH_H) / 2 + PH_B
    tvo = t_palabra("s19b", "votaciones", defecto=1.6) - .2; tco = t_palabra("s19b", "comentarios", defecto=3.4) - .1
    kp = eo(seg(t, tvo, tvo + .4)) * out
    if kp > 0:   # encuesta tipo sticker
        w_, h_ = SC_W - 50, 230; x = tx0 + 25; y = ty0 + SC_H - h_ - 120 + 20 * (1 - kp)
        card = Image.new("RGBA", (w_, h_), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([0, 0, w_ - 1, h_ - 1], 26, fill=(255, 255, 255, 245))
        draw_text(cd, w_ / 2, 52, "¿QUÉ SABOR SACAMOS?", F("o", 34, "Bold"), GREEN + (255,), anchor="ms", track=2)
        for i, (op, v) in enumerate((("Sandía", .64), ("Mango", .36))):
            yy = 80 + i * 66; bw_ = w_ - 40
            cd.rounded_rectangle([20, yy, 20 + bw_, yy + 50], 25, fill=(236, 230, 220, 255))
            fill = bw_ * v * eio(seg(t, tvo + .5 + i * .15, tvo + 1.9 + i * .15))
            col = GREEN if i == 0 else mix(CREAM, GREEN, .35)          # gana Sandía: verde; Mango: verde claro
            if fill > 50: cd.rounded_rectangle([20, yy, 20 + fill, yy + 50], 25, fill=col + (255,))
            draw_text(cd, 42, yy + 34, op, F("d", 26, "Bold"), (255, 255, 255, 255) if (i == 0 and fill > 120) else GREEN + (255,))
        if kp < 1: card.putalpha(card.getchannel("A").point(lambda a: round(a * kp)))
        im.paste(card, (round(x), round(y)), card)
    for j, (txt, tt) in enumerate((("Mi nuevo vicio !!", tco), ("Diosssss mi agua de coco favoritaaaa del momento!", tco + .7))):
        kc = eo(seg(t, tt, tt + .35)) * out
        if kc <= 0: continue
        fc = F("d", 24, "Medium"); lines = _parte(txt, fc, 300)
        w_ = max(text_w(l, fc) for l in lines) + 90; h_ = 40 + 32 * len(lines)
        b = Image.new("RGBA", (round(w_), h_), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
        bd.rounded_rectangle([0, 0, w_ - 1, h_ - 1], 22, fill=CREAM + (255,), outline=GREEN + (255,), width=3)
        bd.ellipse([16, h_ / 2 - 15, 46, h_ / 2 + 15], fill=mix(CREAM, GREEN, .35) + (255,))
        for i, l in enumerate(lines): draw_text(bd, 60, 30 + 22 + i * 32 - 8, l, fc, GREEN + (255,))
        sc = .85 + .15 * kc; b = b.resize((round(b.width * sc), round(b.height * sc)), Image.LANCZOS)
        if kc < 1: b.putalpha(b.getchannel("A").point(lambda a: round(a * kc)))
        bx = (60, 120)[j]; by = (60, 175)[j]
        im.paste(b, (bx, round(ty0 + by)), b)

def _s19d_extra(im, t, D, out):
    """Palanca 4: los 12 meses del año se van encendiendo bajo el texto (presencia todo el año)."""
    d = ImageDraw.Draw(im); BG, INK = A.BG, A.INK
    fm = F("o", 30, "Bold"); x0, y = 860, 905
    for i, m in enumerate(("ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC")):
        k = eo(seg(t, 1.6 + i * .2, 1.9 + i * .2)) * out
        if k <= 0: continue
        cx = x0 + 34 + i * 78
        d.ellipse([cx - 22, y - 22, cx + 22, y + 22], fill=mix(BG, INK, k))
        draw_text(d, cx, y + 64, m, fm, mix(BG, INK, .8 * k), anchor="ms", track=2)
        if i: d.line([(cx - 56, y), (cx - 22, y)], fill=mix(BG, INK, .4 * k), width=3)

S19_EXTRA = {"s19b": _s19b_extra, "s19d": _s19d_extra}

S19C_BOLSAS = [("NOTORIEDAD", ["Alcance", "Impresiones"]), ("INTERACCIÓN", ["Engagement", "Comentarios"])]   # KPIs orientativos

def _s19c_izq(im, t, D, out):
    """Palanca 3: dos bolsas de paid como dos barras que se llenan, cada una con sus KPIs (estilo gráfico S10)."""
    d = ImageDraw.Draw(im); BG, INK = A.BG, A.INK
    bw, bh, r, base = 250, 520, 26, 760
    fl, fk = F("o", 40, "Bold"), F("d", 26, "Medium")
    for j, (tit, kpis) in enumerate(S19C_BOLSAS):
        x = 170 + j * (bw + 90); t0 = .4 + j * .5
        kb = eio(seg(t, t0, t0 + .8)) * out
        if kb <= 0: continue
        d.rounded_rectangle([x, base - bh, x + bw, base], r, outline=mix(BG, INK, .35 * kb), width=4)   # bolsa vacía
        h_ = (bh - 16) * kb
        if h_ > 2 * r: d.rounded_rectangle([x + 8, base - 8 - h_, x + bw - 8, base - 8], r - 6, fill=mix(BG, INK if j == 0 else mix(INK, BG, .35), kb))
        kt = eo(seg(t, t0 + .5, t0 + .9)) * out
        if kt > 0:
            draw_text(d, x + bw / 2, base + 60, tit, fl, mix(BG, INK, kt), anchor="ms", track=3)
            for i, kp in enumerate(kpis):
                ki = eo(seg(t, t0 + .8 + i * .15, t0 + 1.2 + i * .15)) * out
                if ki <= 0: continue
                w_ = text_w(kp, fk) + 40; yy = base + 90 + i * 54
                d.rounded_rectangle([x + bw / 2 - w_ / 2, yy, x + bw / 2 + w_ / 2, yy + 42], 21, outline=mix(BG, INK, ki), width=2)
                draw_text(d, x + bw / 2, yy + 30, kp, fk, mix(BG, INK, ki), anchor="ms")

S19_IZQ = {"s19c": _s19c_izq}

S19C_REPARTO = (.70, .30)   # 18/11: reparto del documento de propuesta (awareness / interacción)
S19C_TEXTOS = (("AWARENESS", "Mantenemos la notoriedad como motor de crecimiento y llegamos a nuevas audiencias."),
               ("INTERACCIÓN", "Impulsamos los contenidos que invitan a participar, comentar y compartir."))

def s19c_paid(t, D):
    """Palanca 3 (como la slide 37 del documento): PAID EN DOS + barra a todo el ancho que se reparte 70/30."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .4, D)
    kn = eo(seg(t, .1, .6)) * out
    draw_text(d, 150, 150, "PALANCA 3 DE 5", F("o", 40, "Medium"), mix(BG, A.KICK, kn), track=8)
    fT = F("o", 230, "Bold"); yb = 185 + cap_h(fT)
    kt = eo(seg(t, .3, .8)) * out
    if kt > 0: draw_text(d, 140, yb + 20 * (1 - kt), "PAID EN DOS", fT, mix(BG, INK, kt), track=4)
    ks = eo(seg(t, .6, 1.1)) * out
    if ks > 0: draw_text(d, 150, yb + 75, "Notoriedad e interacción, medidas por separado.", F("d", 40, "Medium"), mix(BG, INK, ks))
    # barra a todo el ancho: entra entera como awareness y luego se abre el tramo de interacción
    y0, bh = 600, 120
    kb = eio(seg(t, .9, 1.6)) * out
    if kb > 0:
        AW, IN = INK, mix(INK, BG, .4)
        d.rectangle([0, y0, W * kb, y0 + bh], fill=mix(BG, AW, out))
        ksp = eio(seg(t, 1.8, 2.7))
        xs = W * (1 - S19C_REPARTO[1] * ksp)
        if ksp > 0: d.rectangle([xs, y0, W, y0 + bh], fill=mix(BG, IN, out))
        fp = F("o", 90, "Bold"); cy = y0 + bh / 2 + cap_h(fp) / 2
        p1 = round(100 - 100 * S19C_REPARTO[1] * ksp)
        if ksp > .05: draw_text(d, xs - 40, cy, f"{p1}%", fp, mix(AW, BG, kb), anchor="rs")
        if ksp > .05: draw_text(d, xs + 40, cy, f"{round(100 * S19C_REPARTO[1] * ksp)}%", fp, mix(IN, AW, ksp * out))
        fh, fx = F("o", 44, "Bold"), F("d", 32, "Regular")
        for j, (tit, tx) in enumerate(S19C_TEXTOS):
            kx = eo(seg(t, 2.6 + j * .3, 3.1 + j * .3)) * out
            if kx <= 0: continue
            lines = _parte(tx, fx, 640)
            if j == 0:
                xr = xs - 40
                draw_text(d, xr, y0 + bh + 80, tit, fh, mix(BG, INK, kx), anchor="rs", track=3)
                for i, l in enumerate(lines): draw_text(d, xr, y0 + bh + 130 + i * 44, l, fx, mix(BG, INK, kx), anchor="rs")
            else:
                xl = xs + 40
                draw_text(d, xl, y0 + bh + 80, tit, fh, mix(BG, IN, kx), track=3)
                for i, l in enumerate(_parte(tx, fx, W - xl - 80)): draw_text(d, xl, y0 + bh + 130 + i * 44, l, fx, mix(BG, INK, kx))
    return im

S19E_T = {"cambio": 5.45, "feed": 6.9, "running": 7.72, "yoga": 8.76, "deporte": 9.5}   # medidos en las pausas de la toma _2 (18/11)

def s19e_club(t, D):
    """Palanca 5 en dos tiempos (18/11): 1) la web Amazonia Club · Friends First con scroll hasta «Próximas
    quedadas» y un toque en «Apúntate»; 2) la pantalla pasa a planos reales de clubs y el texto a «Activaciones»."""
    import club_web
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .4, D)
    if "club_web" not in _TEL: _TEL["club_web"] = club_web.web(SC_W)
    webim, (bx, by), yq = _TEL["club_web"]
    T = _telefono(); pad = T["pad"]
    tcam = S19E_T["cambio"]; ttap = tcam - .6   # cambio en la pausa antes de «Y activaciones»
    if t < tcam:
        fin = min(yq - 60, webim.height - SC_H)
        off = fin * eio(seg(t, .9, tcam - 1.0))
        sc = webim.crop((0, round(off), SC_W, round(off) + SC_H)).convert("RGB")
        kt_ = seg(t, ttap, ttap + .45)
        if kt_ > 0:   # toque en «Apúntate»
            sd = ImageDraw.Draw(sc, "RGBA"); r = 18 + 30 * kt_; cy = by - off
            sd.ellipse([bx - r, cy - r, bx + r, cy + r], fill=(255, 255, 255, round(150 * (1 - kt_))))
    else:
        frs = _s19_clip("s19e"); sc = frs[min(len(frs) - 1, int((t - tcam) * 25))]
        if t < tcam + .35:   # barrido de la web a los planos
            k = eio(seg(t, tcam, tcam + .35)); fin = min(yq - 60, webim.height - SC_H); prev = webim.crop((0, round(fin), SC_W, round(fin) + SC_H)).convert("RGB")
            sc = sc.copy(); sc.paste(prev.crop((0, 0, SC_W, round(SC_H * (1 - k)))), (0, 0))
    tel = T["cuerpo"].copy(); tel.paste(sc, (pad + PH_B, pad + PH_B), T["mask"])
    kt = eo(seg(t, 0, .6)) * out
    if kt < 1: tel.putalpha(tel.getchannel("A").point(lambda v: round(v * kt)))
    im.paste(tel, (round(480 - PH_W / 2 - pad), round((H - PH_H) / 2 + 40 * (1 - kt) - pad)), tel)
    x0 = 860
    kn = eo(seg(t, .1, .6)) * out
    fnum = F("o", 300, "Bold"); yn = 150 + cap_h(fnum)
    draw_text(d, x0 - 10, yn + 30 * (1 - kn), "5", fnum, mix(BG, A.ACC, kn))
    draw_text(d, x0 + text_w("5", fnum) + 30, yn, "PALANCA 5 DE 5", F("o", 38, "Medium"), mix(BG, A.KICK, kn), track=8)
    ft = F("o", 104, "Bold"); y1 = yn + 60; fs = F("d", 38, "Regular")
    ka = (1 - eio(seg(t, tcam - .3, tcam))) * out            # tiempo 1: la web
    kb = eio(seg(t, tcam, tcam + .4)) * out                  # tiempo 2: activaciones
    if ka > 0:
        for i, l in enumerate(("AMAZONIA CLUB:", "FRIENDS FIRST")):
            kk = eo(seg(t, .35 + i * .12, .85 + i * .12)) * ka
            if kk > 0: draw_text(d, x0, y1 + cap_h(ft) + i * (cap_h(ft) + 24) + 18 * (1 - kk), l, ft, mix(BG, INK, kk), track=4)
        y2 = y1 + 2 * (cap_h(ft) + 24) + 80
        for i, l in enumerate(_parte("Un espacio propio donde la comunidad tiene prioridad: lanzamientos, ediciones limitadas y acceso a eventos.", fs, 880)):
            kl = eo(seg(t, 1.0 + i * .12, 1.5 + i * .12)) * ka
            if kl > 0: draw_text(d, x0, y2 + i * 54 + 12 * (1 - kl), l, fs, mix(BG, INK, .9 * kl))
    if kb > 0:
        draw_text(d, x0, y1 + cap_h(ft) + 18 * (1 - kb), "ACTIVACIONES", ft, mix(BG, INK, kb), track=4)
        fc = F("o", 44, "Bold"); xc = x0; yc = y1 + cap_h(ft) + 60
        for i, (c, pal) in enumerate((("RUNNING", "running"), ("YOGA", "yoga"), ("DEPORTE EN GRUPO", "deporte"))):   # 18/11: sin Wellhub
            tc_ = S19E_T[pal] - .1
            kc = eo(seg(t, tc_, tc_ + .35)) * out
            w_ = text_w(c, fc) + 8 * (len(c) - 1) + 60
            if kc > 0:
                d.rounded_rectangle([xc, yc, xc + w_, yc + 76], 38, fill=mix(BG, INK, kc))
                draw_text(d, xc + 30, yc + 38 + cap_h(fc) / 2, c, fc, mix(INK, BG, kc), track=8)
            xc += w_ + 20
        tf_ = S19E_T["feed"] - .2
        kl = eo(seg(t, tf_, tf_ + .5)) * out
        if kl > 0: draw_text(d, x0, yc + 76 + 90 + 12 * (1 - kl), "Del feed a la quedada.", F("d", 44, "Medium"), mix(BG, INK, kl))
    return im

def _palanca(k):
    if k == "s19c": return s19c_paid
    if k == "s19e": return s19e_club
    if k in S19_CLIPS or k in S19_IZQ: return _palanca_clip(k)
    return _palanca_texto(k)

def _palanca_clip(k):
    """18/11: teléfono con contenido real a la izquierda; a la derecha número, titular y frase."""
    def fn(t, D):
        im, d = A.canvas(); BG, INK = A.BG, A.INK
        num, lin, frase = S19_PALANCAS[k]
        out = 1 - seg(t, D - .4, D)
        if k in S19_IZQ: S19_IZQ[k](im, t, D, out)
        else:
            T = _telefono(); pad = T["pad"]; frs = _s19_clip(k)
            sc = frs[min(len(frs) - 1, int(t * 25))]
            tel = T["cuerpo"].copy(); tel.paste(sc, (pad + PH_B, pad + PH_B), T["mask"])
            kt = eo(seg(t, 0, .6)) * out
            if kt < 1: tel.putalpha(tel.getchannel("A").point(lambda v: round(v * kt)))
            im.paste(tel, (round(480 - PH_W / 2 - pad), round((H - PH_H) / 2 + 40 * (1 - kt) - pad)), tel)
        if k in S19_EXTRA: S19_EXTRA[k](im, t, D, out)
        x0 = 860
        kn = eo(seg(t, .1, .6)) * out
        fnum = F("o", 300, "Bold"); yn = 150 + cap_h(fnum)
        draw_text(d, x0 - 10, yn + 30 * (1 - kn), num, fnum, mix(BG, A.ACC, kn))
        draw_text(d, x0 + text_w(num, fnum) + 30, yn, f"PALANCA {num} DE 5", F("o", 38, "Medium"), mix(BG, A.KICK, kn), track=8)
        ft = F("o", 110, "Bold"); y1 = yn + 60
        for i, l in enumerate(lin):
            kk = eo(seg(t, .35 + i * .12, .85 + i * .12)) * out
            if kk > 0: draw_text(d, x0, y1 + cap_h(ft) + i * (cap_h(ft) + 24) + 18 * (1 - kk), l, ft, mix(BG, INK, kk), track=4)
        tf = t_palabra(k, frase.split()[0], defecto=1.1) - .1
        fs = F("d", 38, "Regular"); y2 = y1 + 2 * (cap_h(ft) + 24) + 80
        for i, l in enumerate(_parte(frase, fs, 880)):
            kl = eo(seg(t, tf + i * .12, tf + .5 + i * .12)) * out
            if kl > 0: draw_text(d, x0, y2 + i * 54 + 12 * (1 - kl), l, fs, mix(BG, INK, .9 * kl))
        return im
    return fn

def _palanca_texto(k):
    def fn(t, D):
        im, d = A.canvas(); BG, INK = A.BG, A.INK
        num, lin, frase = S19_PALANCAS[k]
        out = 1 - seg(t, D - .4, D)
        kn = eo(seg(t, .1, .6)) * out
        draw_text(d, 380, 760 + 30 * (1 - kn), num, F("o", 560, "Bold"), mix(BG, A.ACC, kn), anchor="ms")
        draw_text(d, 690, 300, f"PALANCA {num} DE 5", F("o", 38, "Medium"), mix(BG, A.KICK, kn), track=8)
        ft = F("o", 120, "Bold")
        for i, l in enumerate(lin):
            kt = eo(seg(t, .35 + i * .12, .85 + i * .12)) * out
            if kt > 0: draw_text(d, 690, 300 + 40 + cap_h(ft) + i * (cap_h(ft) + 26) + 18 * (1 - kt), l, ft, mix(BG, INK, kt), track=4)
        tf = t_palabra(k, frase.split()[0], defecto=1.1) - .1
        fs = F("d", 40, "Regular"); y0 = 300 + 40 + 2 * (cap_h(ft) + 26) + 70
        for i, l in enumerate(_parte(frase, fs, 1080)):
            kl = eo(seg(t, tf + i * .12, tf + .5 + i * .12)) * out
            if kl > 0: draw_text(d, 690, y0 + i * 56 + 12 * (1 - kl), l, fs, mix(BG, INK, .9 * kl))
        return im
    return fn
s19a, s19b, s19c, s19d, s19e = (_palanca(f"s19{x}") for x in "abcde")

SFX = {"s03": lambda D: [(t_palabra("s03", "otra", defecto=2.2) - .1, "pop")], "s05": lambda D: sfx_palanca(D) + [(_s05_tiempos(D)["cambio"] - .1, "whoosh")],
       **{k: sfx_palanca for k in ("s06", "s07")},
       "s11": lambda D: sfx_palanca(D) + [(_s11_tiempos()["foco"], "pop"), (_s11_tiempos()["mas"], "pop"),
                                          (_s11_tiempos()["sw"] - .4, "whoosh_corto"), (_s11_tiempos()["p2"], "pop")],
       "s10": lambda D: [x for x in sfx_palanca(D) if x[1] != "pop" or x[0] < 1] + [(_s10_entra()[0], "pop"), (_s10_entra()[1] - .15, "whoosh_corto")],
       "s13": lambda D: [(t_palabra("s13", w, defecto=dd) - .1, "pop") for w, dd in (("53", .5), ("200", 1.7), ("18", 2.5), ("7", 3.3))],
       "s15": lambda D: [(x[3], "pop") for x in _s15_tiempos()] + [(x[0], "whoosh_corto") for x in _s15_tiempos()[1:]],
       "s14": lambda D: [(t_palabra("s14", "notoriedad", defecto=1.15) - .35, "whoosh_corto"), (t_palabra("s14", "cumplido", defecto=2.15) + .1, "pop")],
       "s16": lambda D: [(t_palabra("s16", "2027", defecto=1.0) - .3, "pop"), (t_palabra("s16", "2027", defecto=1.0) + .02, "pop")],
       "s19": lambda D: [(x - .2, "pop") for x in _s19_tiempos()],
       "s32": lambda D: [(duraciones("s32")[2] + .2, "bad_gyal_fiebre")],
       "s31": lambda D: [(t_palabra("s31", "con", fin=True, defecto=2.2) - .15 + j * .25, "pop") for j in range(3)],
       "s12": lambda D: [(t_palabra("s12", "llegaron", defecto=1.4) - .35, "whoosh_corto")],
       "s09": lambda D: sfx_palanca(D) + [(a - .1, "whoosh_corto") for a in _s09_tiempos(D)[1:]]
                        + [(t_palabra("s09", "suman", defecto=6.2) + 1.8, "pop")],
       "s08": lambda D: sfx_palanca(D) + [(t_palabra("s08", "hoy") - .25, "whoosh_corto"), (t_palabra("s08", "7") + 1.2, "pop")]}

# --- S08: teléfono con una app de vídeo corto estilo TikTok (mockup): feed con la pieza → perfil con seguidores contando
S08_SRC = ROOT / "material/s08_tiktok/GIF LATAS AMAZONIA V2.mp4"
S08_DESDE = 1.0                      # segundo de inicio del corte (nota del cliente: 1 → 5)
S08_USUARIO = "@amazonia_fruit"      # confirmado con la captura del perfil
TK_ROJO = (0xFE, 0x2C, 0x55)

def _s08_frames():
    if "s08" in _TEL: return _TEL["s08"]
    vf = f"scale={SC_W}:{SC_H}:force_original_aspect_ratio=increase,crop={SC_W}:{SC_H},format=rgb24"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(S08_DESDE), "-i", str(S08_SRC), "-vf", vf, "-an",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    n = len(raw) // (SC_W * SC_H * 3)
    fr = [Image.frombytes("RGB", (SC_W, SC_H), raw[i * SC_W * SC_H * 3:(i + 1) * SC_W * SC_H * 3]) for i in range(n)]
    fps = float(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                                "-of", "csv=p=0", str(S08_SRC)], capture_output=True, text=True).stdout.split("/")[0])
    # avatar: círculo recortado del centro de la lata
    f0 = fr[0]; c = f0.crop((SC_W // 2 - 90, SC_H // 2 - 120, SC_W // 2 + 90, SC_H // 2 + 60)).resize((84, 84), Image.LANCZOS)
    m = Image.new("L", (84, 84), 0); ImageDraw.Draw(m).ellipse([0, 0, 83, 83], fill=255)
    av = Image.new("RGBA", (84, 84), (0, 0, 0, 0)); av.paste(c, (0, 0), m)
    thumbs = [fr[min(len(fr) - 1, round(i * (len(fr) - 1) / 8))] for i in range(9)]
    _TEL["s08"] = {"fr": fr, "fps": fps, "av": av, "thumbs": thumbs}
    return _TEL["s08"]

def _icono_corazon(d, cx, cy, r, fill):
    d.ellipse([cx - r, cy - r * .9, cx, cy + r * .1], fill=fill); d.ellipse([cx, cy - r * .9, cx + r, cy + r * .1], fill=fill)
    d.polygon([(cx - r * .97, cy - r * .2), (cx + r * .97, cy - r * .2), (cx, cy + r)], fill=fill)

def _pantalla_feed(t_vid=None, img=None, usuario=None, av=None, cifras=None, texto=None):
    """Pantalla «Para ti». Por defecto, la pieza de S08; img/usuario/av/cifras para otras piezas.
    cifras: textos bajo corazón, comentarios, guardados y compartir (None = sin cifra)."""
    if img is None:
        S = _s08_frames(); fr = S["fr"]; img = fr[min(len(fr) - 1, int(t_vid * S["fps"]))]; av = S["av"]; usuario = S08_USUARIO
    sc = img.copy().convert("RGBA")
    ov = Image.new("RGBA", (SC_W, SC_H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for i in range(160):   # degradado inferior para que se lea el texto
        d.line([(0, SC_H - 70 - i), (SC_W, SC_H - 70 - i)], fill=(0, 0, 0, round(110 * (1 - i / 160))))
    fb, fr_ = F("d", 17, "Bold"), F("d", 17, "Medium")
    draw_text(d, SC_W / 2 - 50, 78, "Siguiendo", fr_, (255, 255, 255, 170), anchor="ms")
    draw_text(d, SC_W / 2 + 50, 78, "Para ti", fb, (255, 255, 255, 255), anchor="ms")
    d.rounded_rectangle([SC_W / 2 + 34, 86, SC_W / 2 + 66, 89], 2, fill=(255, 255, 255, 255))
    x = SC_W - 34   # columna de acciones
    a50 = av.resize((50, 50), Image.LANCZOS); ov.paste(a50, (round(x - 25), 330), a50)
    d.ellipse([x - 10, 370, x + 10, 390], fill=TK_ROJO + (255,))
    d.line([(x - 5, 380), (x + 5, 380)], fill=(255, 255, 255, 255), width=2); d.line([(x, 375), (x, 385)], fill=(255, 255, 255, 255), width=2)
    _icono_corazon(d, x, 432, 16, (255, 255, 255, 235))
    d.rounded_rectangle([x - 16, 474, x + 16, 500], 12, fill=(255, 255, 255, 235)); d.polygon([(x - 6, 498), (x + 4, 498), (x - 8, 508)], fill=(255, 255, 255, 235))
    d.polygon([(x - 13, 540), (x + 13, 540), (x + 13, 566), (x, 556), (x - 13, 566)], fill=(255, 255, 255, 235))
    d.polygon([(x - 14, 610), (x + 2, 596), (x + 2, 604), (x + 16, 604), (x + 16, 616), (x + 2, 616), (x + 2, 624)], fill=(255, 255, 255, 235))
    if cifras:
        fc = F("d", 12, "Bold")
        for c, y in zip(cifras, (462, 522, 584, 642)):
            if c: draw_text(d, x, y, c, fc, (255, 255, 255, 255), anchor="ms")
    draw_text(d, 16, SC_H - 112 - (22 if texto else 0), usuario, F("d", 18, "Bold"), (255, 255, 255, 255))
    if texto: draw_text(d, 16, SC_H - 88, texto, F("d", 14, "Regular"), (255, 255, 255, 235))
    d.rectangle([0, SC_H - 64, SC_W, SC_H], fill=(0, 0, 0, 255))   # barra inferior
    fn_ = F("d", 11, "Medium")
    for i, l in enumerate(("Inicio", "Amigos", "", "Bandeja", "Perfil")):
        cx = SC_W * (i + .5) / 5
        if l: d.rounded_rectangle([cx - 9, SC_H - 52, cx + 9, SC_H - 36], 4, outline=(255, 255, 255, 220), width=2); draw_text(d, cx, SC_H - 16, l, fn_, (255, 255, 255, 220), anchor="ms")
        else: d.rounded_rectangle([cx - 22, SC_H - 50, cx + 22, SC_H - 22], 8, fill=(255, 255, 255, 255)); draw_text(d, cx, SC_H - 28, "+", F("d", 26, "Bold"), (0, 0, 0, 255), anchor="ms")
    sc.alpha_composite(ov); return sc.convert("RGB")

S08_PERFIL = ROOT / "material/s08_tiktok/perfil_tiktok.png"   # captura real del perfil (la pasó el cliente)

def _pantalla_perfil(n, brillo):
    if S08_PERFIL.exists():   # captura real: se tapa la cifra de seguidores y se dibuja la que cuenta
        if "perfil" not in _TEL: _TEL["perfil"] = Image.open(S08_PERFIL).convert("RGB")
        im = _TEL["perfil"].copy(); d = ImageDraw.Draw(im)
        d.rectangle([372, 528, 596, 574], fill=(255, 255, 255))
        draw_text(d, 483, 568, f"{round(n):,}", F("d", 42, "Bold"), (22, 24, 35), tab=True, anchor="ms")
        if brillo > 0:
            d.rounded_rectangle([382, 522, 584, 618], 22, outline=mix((255, 255, 255), A.ACC, brillo), width=6)
        r = im.width / SC_W
        im = im.resize((SC_W, round(im.height / r)), Image.LANCZOS)
        sc = Image.new("RGB", (SC_W, SC_H), (255, 255, 255)); sc.paste(im, (0, 22))   # 22 px más abajo: libre de la isla
        return sc
    S = _s08_frames()
    sc = Image.new("RGB", (SC_W, SC_H), (255, 255, 255)); d = ImageDraw.Draw(sc)
    draw_text(d, SC_W / 2, 80, S08_USUARIO.lstrip("@").replace("_", " ").title(), F("d", 19, "Bold"), (22, 24, 35), anchor="ms")
    sc.paste(S["av"].resize((96, 96), Image.LANCZOS), (SC_W // 2 - 48, 108), S["av"].resize((96, 96), Image.LANCZOS))
    draw_text(d, SC_W / 2, 236, S08_USUARIO, F("d", 17, "Medium"), (22, 24, 35), anchor="ms")
    # bloque de seguidores (la única cifra que conocemos)
    if brillo > 0:
        d.rounded_rectangle([SC_W / 2 - 100, 254, SC_W / 2 + 100, 336], 16, fill=mix((255, 255, 255), A.ACC, .35 * brillo))
    draw_text(d, SC_W / 2, 298, A.es_num(round(n)), F("d", 40, "Bold"), (22, 24, 35), tab=True, anchor="ms")
    draw_text(d, SC_W / 2, 324, "Seguidores", F("d", 16, "Regular"), (120, 122, 130), anchor="ms")
    d.rounded_rectangle([SC_W / 2 - 80, 352, SC_W / 2 + 80, 394], 6, fill=TK_ROJO)
    draw_text(d, SC_W / 2, 379, "Seguir", F("d", 17, "Bold"), (255, 255, 255), anchor="ms")
    d.line([(0, 420), (SC_W, 420)], fill=(230, 230, 232), width=1)
    d.rectangle([SC_W / 2 - 40, 418, SC_W / 2 + 40, 421], fill=(22, 24, 35))
    tw_, th_ = (SC_W - 4) // 3, round((SC_W - 4) / 3 * 4 / 3)
    for i, th in enumerate(S["thumbs"]):
        x, y = (i % 3) * (tw_ + 2), 424 + (i // 3) * (th_ + 2)
        if y > SC_H: break
        c = th.resize((tw_, round(tw_ * SC_H / SC_W)), Image.LANCZOS); off = (c.height - th_) // 2
        sc.paste(c.crop((0, off, tw_, off + th_)), (x, y))
    return sc

def _s08_tiempos(D):
    return {"hoy": t_palabra("s08", "hoy") - .15, "cuenta": t_palabra("s08", "7") - .1}

def s08(t, D):
    """3. TikTok: teléfono con el feed (la pieza) y, en «Hoy», el perfil con los seguidores subiendo de 0 a 7.823."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    T = _telefono(); pad = T["pad"]; tt = _s08_tiempos(D)
    out = 1 - seg(t, D - .4, D)
    top = 70; xc = W / 2 - PH_W / 2
    dibuja_titulo(im, t, titulo_palanca("s08"), xc - 90, top + PH_H / 2, out)
    k_in = eo(seg(t, TIT_CONTENIDO, TIT_CONTENIDO + .6)) * out
    if k_in <= 0: return im
    feed = _pantalla_feed(max(0, t - TIT_CONTENIDO))
    kp = eio(seg(t, tt["hoy"], tt["hoy"] + .45))          # el perfil entra deslizando desde la derecha
    if kp > 0:
        n = 7823 * A.eo5(seg(t, tt["cuenta"], tt["cuenta"] + 1.4))
        brillo = eo(seg(t, tt["cuenta"] + 1.3, tt["cuenta"] + 1.7))
        perfil = _pantalla_perfil(n, brillo)
        sx = round(SC_W * (1 - kp)); sc = feed.copy()
        sc.paste(feed.crop((0, 0, SC_W, SC_H)).transform((SC_W, SC_H), Image.AFFINE, (1, 0, -round(-SC_W * .3 * kp), 0, 1, 0)), (0, 0))
        sc.paste(perfil.crop((0, 0, SC_W - sx, SC_H)), (sx, 0))
    else:
        sc = feed
    tel = T["cuerpo"].copy()
    tel.paste(sc, (pad + PH_B, pad + PH_B), T["mask"])
    ImageDraw.Draw(tel).rounded_rectangle([pad + PH_W / 2 - 52, pad + PH_B + 14, pad + PH_W / 2 + 52, pad + PH_B + 44], 15, fill=(12, 12, 12, 255))
    if k_in < 1: tel.putalpha(tel.getchannel("A").point(lambda v: round(v * k_in)))
    im.paste(tel, (round(xc - pad), round(top + 60 * (1 - k_in) - pad)), tel)
    # a la derecha del teléfono, la cifra en grande cuando termina de contar
    kb = eo(seg(t, tt["cuenta"] + .2, tt["cuenta"] + .7)) * out
    if kb > 0:
        n = 7823 * A.eo5(seg(t, tt["cuenta"], tt["cuenta"] + 1.4)); xr = xc + PH_W + 90
        draw_text(d, xr, top + PH_H / 2 + 40 + 20 * (1 - kb), A.es_num(round(n)), F("o", 150, "Bold"), mix(BG, A.ACC, kb), tab=True)
        draw_text(d, xr + 4, top + PH_H / 2 + 110 + 20 * (1 - kb), "SEGUIDORES EN TIKTOK", F("o", 44, "Medium"), mix(BG, INK, kb), track=4)
    return im

# --- S09: tres colaboraciones (descargadas de TikTok) que pasan en el feed deslizando + reproducciones sumando
# Cifras de TikTok a 11/11/2026. Locución regrabada: «…Tres colaboraciones que suman 4.300.000 reproducciones solo en TikTok.»
COLABS = [
    {"src": "colab_jordirodriguezmoreno.mp4", "corte": (0.0, 2.4), "usuario": "@jordirodriguezmoreno", "repro": 1_200_000,
     "cifras": ("62,3K", "980", None, "877"), "texto": "Publi con nuestras bebidas de @amazonia_fruit…", "av": (24.5, None)},
    {"src": "colab_probandoconcali.mp4", "corte": (0.0, 2.4), "usuario": "@probandoconcali", "repro": 2_000_000,
     "cifras": ("79K", "676", None, "1286"), "texto": "Probando todos los sabores de los virales snacks…", "av": (3.0, None)},
    # 17/11: sustituye a la 2.ª de @probandoconcali (se repetía). Post de Instagram DbP6rqUKZEg, sin interfaz de app encima
    {"src": "colab_instagram_ruta_fluvial.mp4", "corte": (0.0, 4.0), "crudo": True},
]
S09_DIR = ROOT / "material/s09_colaboraciones"

def _avatar_de(src, ts, cara=(.5, .22, .36)):
    """Avatar redondo recortado de un fotograma (centro x, centro y, lado) en fracciones del vídeo."""
    cx, cy, lado = cara
    vf = f"crop=iw*{lado}:iw*{lado}:iw*{cx}-iw*{lado}/2:ih*{cy}-iw*{lado}/2,scale=84:84"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ts), "-i", str(src), "-frames:v", "1", "-vf", vf,
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    c = Image.frombytes("RGB", (84, 84), raw); m = Image.new("L", (84, 84), 0); ImageDraw.Draw(m).ellipse([0, 0, 83, 83], fill=255)
    av = Image.new("RGBA", (84, 84), (0, 0, 0, 0)); av.paste(c, (0, 0), m); return av

def _s09_colabs():
    if "s09" in _TEL: return _TEL["s09"]
    out = []
    for i, c in enumerate(COLABS, 1):
        src = S09_DIR / c["src"]; corte = OUTDIR / f"entradas/s09_colab{i}.mp4"
        if not corte.exists():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(c["corte"][0]), "-to", str(c["corte"][1]), "-i", str(src),
                            "-an", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", str(corte)], check=True)
        av = None if c.get("crudo") else _avatar_de(src, c["av"][0], (.5, .32, .5) if i == 1 else (.5, .2, .36))
        out.append({**c, "vid": _VideoPantalla(corte, c["corte"][1] - c["corte"][0]), "avatar": av})
    _TEL["s09"] = out; return out

def _s09_tiempos(D):
    """Entrada de cada colaboración: al aparecer el teléfono, en «nuevas audiencias» y en «Tres colaboraciones»."""
    return [TIT_CONTENIDO, t_palabra("s09", "nuevas", defecto=3.4) - .3, t_palabra("s09", "tres", defecto=5.0) - .2]

def _m(v):   # 1200000 → «1,2 M»
    return (f"{v / 1e6:.1f}".rstrip("0").rstrip(".").replace(".", ",")) + " M"

def s09(t, D):
    """4. Influencers: tres colaboraciones que pasan en el feed y, al lado, las reproducciones sumándose."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    T = _telefono(); pad = T["pad"]; C = _s09_colabs(); ini = _s09_tiempos(D)
    out = 1 - seg(t, D - .4, D)
    top = 70; xc = W / 2 - PH_W / 2 + 120   # 17/11: sin la columna de cifras, teléfono más centrado
    dibuja_titulo(im, t, titulo_palanca("s09"), xc - 90, top + PH_H / 2, out)
    k_in = eo(seg(t, TIT_CONTENIDO, TIT_CONTENIDO + .6)) * out
    if k_in <= 0: return im
    def pantalla(i):
        c = C[i]; img = c["vid"].frame(max(0, t - ini[i]))
        if c.get("crudo"): return img
        return _pantalla_feed(img=img, usuario=c["usuario"], av=c["avatar"], cifras=c["cifras"], texto=c["texto"])
    i = max(j for j, a in enumerate(ini) if t >= a) if t >= ini[0] else 0
    ks = eio(seg(t, ini[i], ini[i] + .35)) if i > 0 else 1        # deslizar hacia arriba
    if ks < 1:
        sc = Image.new("RGB", (SC_W, SC_H)); off = round(SC_H * ks)
        sc.paste(pantalla(i - 1), (0, -off)); sc.paste(pantalla(i), (0, SC_H - off))
    else:
        sc = pantalla(i)
    tel = T["cuerpo"].copy(); tel.paste(sc, (pad + PH_B, pad + PH_B), T["mask"])
    ImageDraw.Draw(tel).rounded_rectangle([pad + PH_W / 2 - 52, pad + PH_B + 14, pad + PH_W / 2 + 52, pad + PH_B + 44], 15, fill=(12, 12, 12, 255))
    if k_in < 1: tel.putalpha(tel.getchannel("A").point(lambda v: round(v * k_in)))
    im.paste(tel, (round(xc - pad), round(top + 60 * (1 - k_in) - pad)), tel)
    return im   # 17/11: fuera la columna derecha (total de reproducciones y lista de creadores), a petición de Juan
    # columna derecha: total que va sumando y lista de creadores
    xr = xc + PH_W + 100; cy = top + PH_H / 2
    ka = eo(seg(t, ini[0] + .2, ini[0] + .6)) * out
    if ka <= 0: return im
    draw_text(d, xr, cy - 170, f"{len(C)} COLABORACIONES", F("o", 40, "Medium"), mix(BG, A.KICK, ka), track=6)
    # el total cuenta mientras Alba dice «suman 4.300.000 reproducciones»
    tsu = t_palabra("s09", "suman", defecto=6.2) - .05
    kt = eo(seg(t, tsu - .15, tsu + .25)) * out
    if kt > 0:
        total = sum(c["repro"] for c in C) * A.eo5(seg(t, tsu, tsu + 1.9))
        draw_text(d, xr - 6, cy + 10 + 20 * (1 - kt), A.es_num(round(total)), F("o", 170, "Bold"), mix(BG, A.ACC, kt), tab=True)
        draw_text(d, xr, cy + 78 + 20 * (1 - kt), "REPRODUCCIONES SOLO EN TIKTOK", F("o", 44, "Medium"), mix(BG, INK, kt), track=4)
    for j, a in enumerate(ini):
        kr = eo(seg(t, a + .1, a + .5)) * out
        if kr <= 0: continue
        y = cy + 150 + j * 50 + 15 * (1 - kr)
        draw_text(d, xr, y, C[j]["usuario"], F("d", 30, "Medium" if j == i else "Regular"), mix(BG, INK, kr * (1 if j == i else .6)))
        draw_text(d, xr + 560, y, _m(C[j]["repro"]), F("o", 34, "Bold"), mix(BG, INK, kr * (1 if j == i else .6)), anchor="rs")
    return im

# --- S10: paid media sin piezas: dos columnas de texto 2025 → 2026 (texto literal del cliente)
S10_TEXTO = [   # 17/11: resumido a titular + una línea (antes, texto literal del cliente)
    ("2025", "AWARENESS", "Darnos a conocer y llegar a nuevas audiencias."),
    ("2026", "INTERACCIÓN", "Introducimos campañas de interacción para empezar a construir comunidad."),
]
def _s10_entra():   # cada columna entra cuando Alba dice su año
    return (t_palabra("s10", "2025", defecto=3.4) - .2, t_palabra("s10", "2026", defecto=9.1) - .2)

def _parte(texto, f, ancho):
    lineas, cur = [], ""
    for w in texto.split():
        prueba = (cur + " " + w).strip()
        if text_w(prueba, f) > ancho and cur: lineas.append(cur); cur = w
        else: cur = prueba
    return lineas + ([cur] if cur else [])

def s10(t, D):
    """5. Paid media: gráfico de barras 2025 (todo awareness) → 2026 (awareness + ~15 % interacción), sin cifras.
    Cada barra crece cuando Alba dice su año; debajo, año + titular + una línea. 18/11: añadido el gráfico."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .4, D)
    x0, ancho, gap = 760, 470, 120
    bw, bh, r = 300, 400, 22
    fy, fb, fh = F("o", 100, "Bold"), F("d", 32, "Regular"), F("o", 58, "Bold")
    fl = F("o", 40, "Bold")
    cols = [(y, (tit, _parte(tx, fb, ancho))) for y, tit, tx in S10_TEXTO]
    alto = bh + 50 + cap_h(fy) + 36 + cap_h(fh) + 30 + max(len(l) for _, (_, l) in cols) * 46
    top = (H - alto) / 2; base = top + bh
    dibuja_titulo(im, t, titulo_palanca("s10"), x0 - 110, H / 2, out)
    AW = mix(BG, INK, .38)
    for j, ((ano, (tit, lineas)), te) in enumerate(zip(cols, _s10_entra())):
        x = x0 + j * (ancho + gap); bx = x
        kb = eio(seg(t, te, te + .7)) * out
        if kb <= 0: continue
        h_ = bh * kb
        d.rounded_rectangle([bx, base - h_, bx + bw, base], radius=min(r, h_ / 2), fill=mix(BG, AW, out))
        kl = eo(seg(t, te + .45, te + .8)) * out
        if kl > 0:
            cy = base - (bh * (.85 if j else 1)) / 2
            lw = text_w("AWARENESS", fl)
            draw_text(d, bx + (bw - lw) / 2, cy + cap_h(fl) / 2, "AWARENESS", fl, mix(AW, INK, kl), track=2)
        if j == 1:   # tramo de interacción (~15 %), entra con pop encima de la barra
            ki = eo(seg(t, te + .75, te + 1.1)) * out
            if ki > 0:
                hi = bh * .15; yt = base - bh
                d.rounded_rectangle([bx, yt - 8 * (1 - ki), bx + bw, yt + hi], radius=r, fill=mix(BG, INK, ki))
                d.rectangle([bx, yt + hi - r, bx + bw, yt + hi], fill=mix(AW, INK, ki))
                lw = text_w("INTERACCIÓN", fl)
                draw_text(d, bx + (bw - lw) / 2, yt + hi / 2 + cap_h(fl) / 2, "INTERACCIÓN", fl, mix(INK, BG, ki), track=2)
            kf = eo(seg(t, te - .2, te + .3)) * out   # flecha de evolución entre barras
            ax = x0 + bw + (ancho + gap - bw) / 2; ay = base - bh / 2
            d.line([(ax - 60, ay), (ax + 40 * kf, ay)], fill=mix(BG, INK, kf), width=5)
            d.polygon([(ax + 52, ay), (ax + 34, ay - 13), (ax + 34, ay + 13)], fill=mix(BG, INK, kf))
        ka = eo(seg(t, te + .1, te + .6)) * out
        yy = base + 50 + cap_h(fy)
        if ka > 0: draw_text(d, x, yy + 24 * (1 - ka), ano, fy, mix(BG, INK, ka))
        kt = eo(seg(t, te + .25, te + .65)) * out
        if kt > 0: draw_text(d, x, yy + 36 + cap_h(fh) + 14 * (1 - kt), tit, fh, mix(BG, INK, kt), track=3)
        for i, l in enumerate(lineas):
            kk = eo(seg(t, te + .35 + i * .07, te + .75 + i * .07)) * out
            if kk > 0: draw_text(d, x, yy + 36 + cap_h(fh) + 30 + (i + 1) * 46 + 14 * (1 - kk), l, fb, mix(BG, INK, kk))
    return im

# --- S11: comunidad sin piezas: texto literal del cliente con las frases clave subrayadas en amarillo
S11_INTRO = "Dinámicas para generar conversación y hacer crecer la base de seguidores."
S11_PARRAFOS = [
    ("Conseguimos resultados excepcionales de participación con sorteos en los que el único premio es nuestro propio "
     "producto, sin recurrir a incentivos externos como hacen otras marcas.", "el único premio es nuestro propio producto,"),
    ("Y lo más importante: los seguidores que ganamos se quedan, demostrando un interés por la marca que va más allá "
     "del sorteo.", "los seguidores que ganamos se quedan,"),
]

S11_TITULARES = [   # 17/11: resumen del texto del cliente (sustituye a S11_INTRO + S11_PARRAFOS en pantalla)
    (["EL ÚNICO PREMIO,", "NUESTRO PRODUCTO"], "Sin incentivos externos."),
    (["LOS SEGUIDORES", "SE QUEDAN"], "Un interés que va más allá del sorteo."),
]

S11_SORTEOS = [   # datos del cliente (11/11/2026), orden cronológico
    {"img": "sorteo_1.png", "fecha": "JUL–AGO 2025", "inter": 8468, "seg": 1068},   # «regalamos la nevera»
    {"img": "sorteo_2.png", "fecha": "OCT 2025", "inter": 4607, "seg": 317},        # imagen PENDIENTE (llega mañana)
    {"img": "sorteo_3.png", "fecha": "MAR 2026", "inter": 4485, "seg": 647},        # todo el portfolio de productos
]

def _s11_tiempos():
    """Fase 1: los tres sorteos con sus cifras. Fase 2 (en «El único premio…»): el texto del cliente."""
    sw = t_palabra("s11", "único", defecto=4.6) - .1   # 17/11: con la voz corta, las tarjetas se ven más rato
    return {"cards": TIT_CONTENIDO, "sw": sw, "intro": sw + .1, "p1": sw + .35,
            "m1": t_palabra("s11", "premio", defecto=sw + 1.3),
            "p2": t_palabra("s11", "importante", defecto=sw + 2.4) - .5,
            "m2": t_palabra("s11", "ganamos", defecto=sw + 3.1) - .8,
            "foco": t_palabra("s11", "mejor", defecto=99) - .3, "mas": t_palabra("s11", "trajo", defecto=99)}

def _s11_imgs(w, h):
    key = ("s11", w, h)
    if key not in _TEL:
        out = []
        for c in S11_SORTEOS:
            f = ROOT / "material/s11_sorteos" / c["img"]
            if f.exists():
                im = Image.open(f).convert("RGB"); r = max(w / im.width, h / im.height)
                im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
                im = im.crop(((im.width - w) // 2, (im.height - h) // 2, (im.width - w) // 2 + w, (im.height - h) // 2 + h))
            else:   # hueco provisional
                im = Image.new("RGB", (w, h), (0x3D, 0x4A, 0x31)); dd = ImageDraw.Draw(im)
                for i, l in enumerate(("SORTEO " + c["fecha"].split()[0], "PENDIENTE")):
                    draw_text(dd, w / 2, h / 2 + i * 44, l, F("o", 36, "Bold"), A.ACC, anchor="ms", track=2)
            out.append(im)
        _TEL[key] = (out, rect_mask(w, h, 22))
    return _TEL[key]

def _s11_cards(im, d, t, x0, alpha):
    BG, INK = A.BG, A.INK; tt = _s11_tiempos()
    w, h, gap = 300, 375, 50
    imgs, mask = _s11_imgs(w, h)
    top = (H - (h + 200)) / 2
    for j, (c, img) in enumerate(zip(S11_SORTEOS, imgs)):
        t0 = tt["cards"] + j * .18
        kf = eio(seg(t, tt["foco"], tt["foco"] + .45))            # «Nuestro mejor sorteo…»: foco en el de la nevera
        k = eo(seg(t, t0, t0 + .55)) * alpha * (1 - .65 * kf if j > 0 else 1)
        if k <= 0: continue
        x = x0 + j * (w + gap); y = top + 40 * (1 - k)
        card = Image.new("RGBA", (w, h), (0, 0, 0, 0)); card.paste(img, (0, 0), mask)
        if k < 1: card.putalpha(card.getchannel("A").point(lambda v: round(v * k)))
        im.paste(card, (round(x), round(y)), card)
        if j == 0 and kf > 0:
            d.rounded_rectangle([x - 10, y - 10, x + w + 9, y + h + 9], 30, outline=mix(BG, A.ACC, kf * alpha), width=7)
        cx = x + w / 2
        draw_text(d, cx, y + h + 46, c["fecha"], F("o", 30, "Medium"), mix(BG, A.KICK, k), anchor="ms", track=6)
        kc = A.eo5(seg(t, t0 + .3, t0 + 1.1))   # 17/11: más rápido, la voz nueva es corta
        draw_text(d, cx, y + h + 112, A.es_num(round(c["inter"] * kc)), F("o", 64, "Bold"), mix(BG, INK, k), tab=True, anchor="ms")
        draw_text(d, cx, y + h + 146, "interacciones", F("d", 26, "Regular"), mix(BG, INK, .7 * k), anchor="ms")
        ks = eo(seg(t, t0 + .6, t0 + 1.0)) * alpha * (1 - .65 * kf if j > 0 else 1)
        if ks > 0:
            kp = eo(seg(t, tt["mas"], tt["mas"] + .35)) * alpha if j == 0 else 0   # «…más de mil seguidores»
            if kp > 0:
                d.rounded_rectangle([cx - 150, y + h + 160, cx + 150, y + h + 210], 25, fill=mix(BG, A.ACC, .55 * kp))
            draw_text(d, cx, y + h + 196, f"+{A.es_num(round(c['seg'] * A.eo5(seg(t, t0 + .6, t0 + 1.3))))} seguidores",
                      F("o", 36, "Bold"), mix(BG, mix(A.ACC, INK, kp), ks), tab=True, anchor="ms", track=2)

def _lineas_marcadas(texto, marca, f, ancho):
    """Parte en líneas y señala qué palabras forman la frase destacada."""
    pal = texto.split(); i0 = texto[:texto.index(marca)].count(" ") if marca in texto else -1
    n = len(marca.split()); lineas, cur = [], []
    for k, w in enumerate(pal):
        prueba = " ".join(x for x, _ in cur + [(w, 0)])
        if text_w(prueba, f) > ancho and cur: lineas.append(cur); cur = []
        cur.append((w, i0 <= k < i0 + n))
    return lineas + ([cur] if cur else [])

def s11(t, D):
    """6. Comunidad: intro + dos párrafos; la frase clave de cada uno se subraya cuando Alba la dice."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .4, D); tt = _s11_tiempos()
    x0, ancho, gap = 760, 500, 80
    fi, fb = F("d", 42, "Medium"), F("d", 32, "Regular")
    intro = _parte(S11_INTRO, fi, 2 * ancho + gap)
    cols = [_lineas_marcadas(tx, m, fb, ancho) for tx, m in S11_PARRAFOS]
    alto = len(intro) * 56 + 70 + max(len(c) for c in cols) * 48
    top = (H - alto) / 2 + 30
    dibuja_titulo(im, t, titulo_palanca("s11"), x0 - 110, H / 2, out)
    kx = eio(seg(t, tt["sw"] - .35, tt["sw"] + .05))          # salen los sorteos, entra el texto
    if kx < 1: _s11_cards(im, d, t, x0, (1 - kx) * out)
    if t < tt["sw"] - .05: return im
    if S11_TITULARES:   # 17/11: dos titulares en filas que entran con la voz y se subrayan en amarillo
        fh, fs = F("o", 60, "Bold"), F("d", 34, "Regular"); fila = cap_h(fh) + 110
        y0 = (H - 2 * fila) / 2 + 30
        for j, ((lin, sub), te, tm) in enumerate(zip(S11_TITULARES, (tt["p1"], tt["p2"]), (tt["m1"], tt["m2"]))):
            l = " ".join(lin); x = x0; yb = y0 + j * fila + cap_h(fh)
            kb = eo(seg(t, te, te + .5)) * out
            if kb <= 0: continue
            d.rectangle([x - 26, yb - cap_h(fh) - 6, x - 20, yb - cap_h(fh) - 6 + (cap_h(fh) + 70) * eio(seg(t, te, te + .6))], fill=mix(BG, A.KICK, kb))
            ku = eio(seg(t, tm, tm + .7)) * out
            if ku > 0: d.rectangle([x, yb + 14, x + (text_w(l, fh) + 3 * (len(l) - 1)) * ku, yb + 22], fill=mix(BG, A.ACC, out))   # 18/11: subrayado fino (antes marcador amarillo)
            draw_text(d, x, yb + 16 * (1 - kb), l, fh, mix(BG, INK, kb), track=3)
            ks = eo(seg(t, te + .3, te + .7)) * out
            if ks > 0: draw_text(d, x, yb + 58 + 10 * (1 - ks), sub, fs, mix(BG, INK, ks))
        return im
    ka = eo(seg(t, tt["intro"], tt["intro"] + .5)) * out
    for i, l in enumerate(intro):
        if ka > 0: draw_text(d, x0, top + i * 56 + 14 * (1 - ka), l, fi, mix(BG, INK, ka))
    y0 = top + len(intro) * 56 + 70
    for j, (lineas, te, tm) in enumerate(zip(cols, (tt["p1"], tt["p2"]), (tt["m1"], tt["m2"]))):
        x = x0 + j * (ancho + gap)
        kb = eo(seg(t, te, te + .5)) * out
        if kb <= 0: continue
        d.rectangle([x - 26, y0 - 34, x - 20, y0 - 34 + len(lineas) * 48 * eio(seg(t, te, te + .6))], fill=mix(BG, A.KICK, kb))
        # subrayado de la frase clave, palabra a palabra, mientras Alba la dice
        marcadas = [(i, w) for i, ln in enumerate(lineas) for w in ln if w[1]]
        km = seg(t, tm, tm + 1.2); hechas = round(km * len(marcadas))
        cuenta = 0
        for i, ln in enumerate(lineas):
            xx = x; yy = y0 + i * 48
            for w, m in ln:
                ww = text_w(w, fb)
                if m:
                    if cuenta < hechas:
                        d.rectangle([xx - 3, yy - 26, xx + ww + 3 + (text_w(" ", fb) if w != ln[-1][0] else 0), yy + 8],
                                    fill=mix(BG, A.ACC, .55 * out))
                    cuenta += 1
                xx += ww + text_w(" ", fb)
        for i, ln in enumerate(lineas):
            kl = eo(seg(t, te + .1 + i * .06, te + .5 + i * .06)) * out
            if kl > 0:
                draw_text(d, x, y0 + i * 48 + 12 * (1 - kl), " ".join(w for w, _ in ln), fb, mix(BG, INK, kl))
    return im

def s12(t, D):
    """Y LOS RESULTADOS · LLEGARON — solo texto (las cifras van en S13)."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .35, D)
    word = "LLEGARON"
    f = F("o", A.fit("o", word, 1300, 300)); ch = cap_h(f)
    by = 700; win = (by - ch - 30, by + 30); hgt = win[1] - win[0]
    tr = t_palabra("s12", "resultados", defecto=.6) - .35
    tl = t_palabra("s12", "llegaron", defecto=1.4) - .3
    ka = eo(seg(t, tr, tr + .45)) * out
    draw_text(d, W / 2, win[0] - 50 + 20 * (1 - ka), "Y LOS RESULTADOS", F("o", 90, "Medium"), mix(BG, INK, ka), anchor="ms", track=10)
    band = Image.new("RGB", (W, hgt), BG); bd = ImageDraw.Draw(band)
    x = W / 2 - text_w(word, f) / 2
    for i, c in enumerate(word):
        k = eio(seg(t, tl + i * .035, tl + i * .035 + .4))
        if k > 0: bd.text((x, by - win[0] + hgt * (1 - k)), c, font=f, fill=mix(BG, A.ACC, out), anchor="ls")
        x += f.getlength(c)
    im.paste(band, (0, win[0]))
    lw = 520 * eio(seg(t, tl + .25, tl + 1.0))
    if lw > 1: d.rectangle([W / 2 - lw / 2, by + 60, W / 2 + lw / 2, by + 68], fill=mix(BG, INK, out))
    return im

# --- S13: resultados 2025-2026 con la maqueta de la diapositiva del cliente
OCRE = CREAM   # 18/11 (Paula): antes ocre; solo colores de marca (S13 ahora sobre verde)

def s13(t, D):
    """53,5 M grande + fila: 200.367 interacciones · 18.011 Instagram · 7.823 TikTok (todo contando)."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .45, D)
    x0 = 200
    tA = t_palabra("s13", "53", defecto=.5) - .1
    tI = t_palabra("s13", "200", defecto=1.7) - .1
    tG = t_palabra("s13", "18", defecto=2.5) - .1
    tT = t_palabra("s13", "7", defecto=3.3) - .1
    ka = eo(seg(t, .1, .45)) * out
    draw_text(d, x0, 175, "RESULTADOS 2025-2026", F("o", 40, "Bold"), mix(BG, OCRE, ka), track=8)
    # 53,5 M
    a = eo(seg(t, tA, tA + .3)) * out
    if a > 0:
        k = A.eo5(seg(t, tA, tA + 1.6))
        draw_text(d, x0 - 8, 470 + 20 * (1 - a), A.es_num(53.5 * k, 1) + " M", F("o", 300, "Bold"), mix(BG, A.ACC, a), tab=True)
        draw_text(d, x0, 540 + 10 * (1 - a), "impactos acumulados en Instagram y TikTok, abril 2025 – octubre 2026",
                  F("d", 36, "Bold"), mix(BG, OCRE, a))
    # fila de tres cifras
    fila = [(200367, "interacciones acumuladas", None, tI),
            (18011, "seguidores en Instagram", "Desde abril de 2025", tG),
            (7823, "seguidores en TikTok", "Partiendo de cero", tT)]
    for j, (v, lab, sub, ts) in enumerate(fila):
        x = x0 + j * 600
        b = eo(seg(t, ts, ts + .3)) * out
        if b <= 0: continue
        k = A.eo5(seg(t, ts, ts + 1.4)); y = 800 + 16 * (1 - b)
        draw_text(d, x - 4, y, A.es_num(round(v * k)), F("o", 140, "Bold"), mix(BG, A.ACC, b), tab=True)
        draw_text(d, x, y + 58, lab, F("d", 34, "Bold"), mix(BG, OCRE, b))
        if sub:
            tsub = t_palabra("s13", "partiendo", defecto=ts) - .1 if j == 2 else ts   # «…partiendo de cero»
            bs = eo(seg(t, tsub, tsub + .35)) * out
            if bs > 0: draw_text(d, x, y + 100 + 8 * (1 - bs), sub, F("d", 27, "Regular"), mix(BG, INK, .65 * bs))
    return im

# --- S15: crecimiento 2025 → 2026 en tres métricas (datos del cliente, 11/11/2026)
S15_METRICAS = [
    # rótulo, valor 2025, valor 2026, formato, distintivo, palabra de la voz donde entra
    ("IMPACTOS AL MES", 1.3e6, 4.2e6, "M", "×3", "impactos"),
    ("INTERACCIONES AL MES", 1389, 9741, "n", "×7", "interacciones"),
    ("ENGAGEMENT RATE", .30, .73, "%", "×2,4", "engagement"),   # 0,30 % → 0,73 % = +143 % (el cliente dijo «+ del 50 %»)
]

def _fmt15(v, f):
    if f == "M": return A.es_num(v / 1e6, 1) + " M"
    if f == "%": return A.es_num(v, 2) + " %"
    return A.es_num(round(v))

def _tpal(k, w, n=1, defecto=0.0):
    hits = [x for x in palabras(k) if A._limpia(x["w"]) == A._limpia(w)]
    return hits[n - 1]["s"] if len(hits) >= n else defecto

def _s15_tiempos():
    """(entrada, barra 2025, barra 2026, distintivo) de cada métrica, según la voz (17/11: solo multiplicadores)."""
    im_ = t_palabra("s15", "impactos", defecto=.8); tr = t_palabra("s15", "tres", defecto=2.6)
    i0 = t_palabra("s15", "interacciones", defecto=3.4); si = t_palabra("s15", "siete", defecto=4.6)
    e0 = t_palabra("s15", "engagement", defecto=5.6); do = t_palabra("s15", "dos", defecto=6.8)
    return [(.3, im_ - .1, im_ + .4, tr - .1),
            (i0 - .4, i0 - .1, i0 + .4, si - .1),
            (e0 - .4, e0 - .1, e0 + .4, do - .1)]

def s15(t, D):
    """Tres columnas: barras 2025 y 2026 que crecen, cifras contando y distintivo del multiplicador."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .45, D)
    ka = eo(seg(t, .1, .45)) * out
    fk = F("o", 44, "Bold"); c = mix(BG, OCRE, ka)
    draw_text(d, W / 2 - 50, 140, "2025", fk, c, anchor="rs", track=8)
    draw_text(d, W / 2 + 50, 140, "2026", fk, c, track=8)
    d.line([(W / 2 - 26, 124), (W / 2 + 22, 124)], fill=c, width=4)
    d.polygon([(W / 2 + 30, 124), (W / 2 + 16, 114), (W / 2 + 16, 134)], fill=c)
    base, hmax, bw, gap = 800, 400, 150, 40
    for j, ((lab, v0, v1, f, badge, palabra), (ts, tb0, tb1, tbad)) in enumerate(zip(S15_METRICAS, _s15_tiempos())):
        cx = W / 2 + (j - 1) * 600
        a = eo(seg(t, ts, ts + .4)) * out
        if a <= 0: continue
        draw_text(d, cx, 250 + 14 * (1 - a), lab, F("o", 42, "Medium"), mix(BG, INK, a), anchor="ms", track=4)
        for i, (v, col, yr) in enumerate(((v0, mix(BG, INK, .35), "2025"), (v1, A.ACC, "2026"))):
            tb = (tb0, tb1)[i]; k = A.eo5(seg(t, tb, tb + 1.1))
            x = cx + (i - .5) * (bw + gap) - bw / 2
            h = hmax * (v / v1) * k
            if h > 3: d.rounded_rectangle([x, base - h, x + bw, base], 14, fill=mix(BG, col, a))
            if k > 0:
                draw_text(d, x + bw / 2, base - h - 22, _fmt15(v * k, f), F("o", 54 if i else 44, "Bold"),
                          mix(BG, INK, a * (1 if i else .7)), tab=True, anchor="ms")
            draw_text(d, x + bw / 2, base + 52, yr, F("o", 34, "Medium"), mix(BG, INK, a * .8), anchor="ms", track=2)
        kb = eo(seg(t, tbad, tbad + .4)) * out
        if kb > 0:
            fb = F("o", 50, "Bold"); bwid = text_w(badge, fb) + 50
            d.rounded_rectangle([cx - bwid / 2, base + 90, cx + bwid / 2, base + 160], 35, fill=mix(BG, INK, kb))
            draw_text(d, cx, base + 143, badge, fb, mix(INK, BG, kb), anchor="ms")
    return im

_SELLO = {}
def _sello_marca(texto, alto_letra):
    """Sello al estilo del «OTRA HISTORIA» de marca: texto redondeado (Fredoka Bold, OFL) en un marco abierto por la
    izquierda con esquinas redondas a la derecha. Devuelve RGBA en crema."""
    key = (texto, alto_letra)
    if key in _SELLO: return _SELLO[key]
    from PIL import ImageFont
    S = 4; C = alto_letra * S
    f = ImageFont.truetype(str(ROOT / "fonts/Fredoka-Bold.ttf"), round(C / .70))
    bb = f.getbbox(texto, anchor="ls"); cap = -f.getbbox("H", anchor="ls")[1]
    sc = C / cap; f = ImageFont.truetype(str(ROOT / "fonts/Fredoka-Bold.ttf"), round(f.size * sc)); bb = f.getbbox(texto, anchor="ls")
    th = round(.085 * C); r = round(.42 * C); m = th
    tl = round(1.0 * C); tr = round(.5 * C); gt = round(.42 * C); gb = round(.48 * C)
    w = m + tl + (bb[2] - bb[0]) + tr + m; h = m + gt + C + gb + m
    im = Image.new("L", (w, h), 0); d = ImageDraw.Draw(im)
    xl, yt, xr, yb = m, m, w - m, h - m
    d.rounded_rectangle([xl - 4 * r, yt, xr, yb], r, outline=255, width=th)
    d.rectangle([0, 0, xl - 1, h], fill=0)
    for y in (yt + th / 2, yb - th / 2): d.ellipse([xl - th / 2, y - th / 2, xl + th / 2, y + th / 2], fill=255)
    d.text((m + tl - bb[0], m + gt + C), texto, font=f, fill=255, anchor="ls")
    im = im.resize((w // S, h // S), Image.LANCZOS)
    out = Image.new("RGBA", im.size, CREAM + (0,)); out.putalpha(im)
    _SELLO[key] = out
    return out

def s14(t, D):
    """18/11 (referencia de Juan): «EL ENCARGO / DE NOTORIEDAD» grande en crema; al decir «cumplido» se apaga y cae
    encima el sello «CUMPLIDO» con el mismo estilo que el «OTRA HISTORIA» de la S03."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .35, D)
    t1 = t_palabra("s14", "el", defecto=.5) - .1
    tn = t_palabra("s14", "notoriedad", defecto=1.15) - .3
    tc = t_palabra("s14", "cumplido", defecto=2.15) - .12
    f = F("o", 235); ch = cap_h(f); paso = ch + 30; x0 = 80; y0 = 230
    apaga = 1 - .55 * eio(seg(t, tc - .1, tc + .35))
    for i, (l, te) in enumerate((("EL ENCARGO", t1), ("DE NOTORIEDAD", tn))):
        k = eo(seg(t, te, te + .45)) * out
        if k > 0: draw_text(d, x0, y0 + ch + i * paso + 20 * (1 - k), l, f, mix(BG, INK, apaga * k), track=2)
    k = eio(seg(t, tc, tc + .45)) * out
    if k > 0:
        st = _sello_marca("CUMPLIDO", 118)
        sc = 1.18 - .18 * k
        st = st.resize((round(st.width * sc), round(st.height * sc)), Image.LANCZOS).rotate(3 + 2 * (1 - k), expand=True, resample=Image.BICUBIC)
        if k < 1: st.putalpha(st.getchannel("A").point(lambda v: round(v * k)))
        cx, cy = x0 + 560, y0 + 2 * paso + 65
        im.paste(st, (round(cx - st.width / 2), round(cy - st.height / 2)), st)
    return im

def s16(t, D):
    """Y EN 202[5→6→7], ¿QUÉ PASA? — el año rueda como un cuentakilómetros y la pregunta se escribe (sobre verde)."""
    BGc = A.BG   # verde de marca (antes negro), como S12 y S14
    im = Image.new("RGB", (W, H), BGc); d = ImageDraw.Draw(im)
    out = 1 - seg(t, D - .3, D)
    f = F("o", 190, "Bold"); ch = cap_h(f)
    t0 = t_palabra("s16", "en", defecto=.65) - .15
    ty = t_palabra("s16", "2027", defecto=1.0)
    tq = t_palabra("s16", "qué", defecto=2.2) - .1
    y1, y2 = 470, 470 + ch + 70
    pre = "Y EN "; x0 = W / 2 - text_w("Y EN 2027,", f) / 2
    ka = eo(seg(t, t0, t0 + .3)) * out
    draw_text(d, x0, y1, pre, f, mix(BGc, CREAM, ka))
    xa = x0 + text_w(pre, f)
    if t >= t0:
        draw_text(d, xa, y1, "202", f, mix(BGc, A.ACC, out))
        xd = xa + text_w("202", f); dw = text_w("8", f)
        # último dígito: 5 → 6 → 7 (cada paso sube como un rodillo)
        pasos = [(5, 6, ty - .3), (6, 7, ty + .02)]
        pos = 5.0
        for a, b, ts in pasos:
            pos += eio(seg(t, ts, ts + .28))
        lo = int(pos) if pos < 7 else 7; fr = pos - lo
        win = Image.new("RGB", (round(dw + 20), round(ch + 40)), BGc); wd = ImageDraw.Draw(win)
        for dig, off in ((lo, -fr), (min(lo + 1, 7), 1 - fr)):
            if abs(off) < 1: wd.text((10, 20 + ch + off * (ch + 40) * -1 * -1), str(dig), font=f, fill=mix(BGc, A.ACC, out), anchor="ls")
        im.paste(win, (round(xd - 10), round(y1 - ch - 20)))
        if pos >= 6.99: draw_text(d, xd + dw + 4, y1, ",", f, mix(BGc, CREAM, out))
    # ¿QUÉ PASA? escrito con cursor
    q = "¿QUÉ PASA?"; n = int(len(q) * seg(t, tq, tq + .5)) if t >= tq else 0
    xq = x0
    if n > 0: draw_text(d, xq, y2, q[:n], f, mix(BGc, CREAM, out))
    blink = (int(t * 2.4) % 2 == 0) or (tq <= t < tq + .6)
    if t >= tq - .4 and blink and out > 0:
        cx = xq + (text_w(q[:n], f) if n else 0) + 12
        d.rectangle([cx, y2 - ch, cx + 10, y2 + 12], fill=mix(BGc, A.ACC, out))
    return im

def _sello(txt, color, tick=True, fs=120):
    """Sello de goma: marco redondeado + (tic) + texto, en RGBA sin girar."""
    f = F("o", fs, "Bold"); tw_ = text_w(txt, f) + 8 * (len(txt) - 1)
    pad_t = round(fs * 1.4) if tick else round(fs * .35)
    sw, sh = round(tw_ + pad_t + fs * .55), round(fs * 1.75)
    st = Image.new("RGBA", (sw, sh), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rounded_rectangle([6, 6, sw - 7, sh - 7], round(fs * .22), outline=color + (255,), width=max(6, round(fs / 12)))
    if tick:
        cx0 = round(fs * .55)
        sd.line([(cx0, sh / 2 + 4), (cx0 + fs * .22, sh / 2 + fs * .27), (cx0 + fs * .63, sh / 2 - fs * .25)],
                fill=color + (255,), width=max(8, round(fs / 7.5)), joint="curve")
    draw_text(sd, pad_t, sh / 2 + cap_h(f) / 2, txt, f, color + (255,), track=8)
    return st

def _pega_sello(im, st, cx, cy, k, alpha=1.0, giro=-6, escala=1.0):
    """k: 0→1 caída (de 1,35× a 1×). alpha y escala finales."""
    if k <= 0 or alpha <= 0: return
    esc = (1.35 - .35 * eo(min(k, 1))) * escala
    s2 = st.resize((max(1, round(st.width * esc)), max(1, round(st.height * esc))), Image.LANCZOS).rotate(giro, resample=Image.BICUBIC, expand=True)
    a = min(1, k * 1.6) * alpha
    if a < 1: s2.putalpha(s2.getchannel("A").point(lambda v: round(v * a)))
    im.paste(s2, (round(cx - s2.width / 2), round(cy - s2.height / 2)), s2)

def s17(t, D):
    """NOTORIEDAD (✓ CUMPLIDO) sube y se apaga · COMUNIDAD entra debajo con el sello «RETO 2027»."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .35, D)
    tn0 = .3
    tmv = t_palabra("s17", "a", defecto=2.86) - .45          # NOTORIEDAD se aparta
    tc = t_palabra("s17", "comunidad", defecto=3.1) - .3      # entra COMUNIDAD
    ts2 = tc + .55                                             # sello nuevo
    km = eio(seg(t, tmv, tmv + .5))
    # NOTORIEDAD: centrada y grande → arriba, más pequeña y apagada
    big = A.fit("o", "NOTORIEDAD", 1300, 240); size = round(big + (110 - big) * km)
    fN = F("o", size, "Bold"); yN = 600 + (330 - 600) * km
    ka = eo(seg(t, tn0, tn0 + .4)) * out
    colN = mix(BG, INK, ka * (1 - .55 * km))
    draw_text(d, W / 2, yN + 20 * (1 - ka), "NOTORIEDAD", fN, colN, anchor="ms", track=4)
    # sello CUMPLIDO sobre NOTORIEDAD (recuerda S14) y se va con ella
    if "sello_c" not in _TEL: _TEL["sello_c"] = _sello("CUMPLIDO", A.ACC)
    _pega_sello(im, _TEL["sello_c"], W / 2 + 330 - 180 * km, yN + 70 - 30 * km, seg(t, .75, 1.0),
                alpha=out * (1 - .55 * km), escala=.62 - .3 * km)
    # flecha hacia abajo
    kf = eo(seg(t, tmv + .2, tmv + .5)) * out
    if kf > 0:
        ax, ay = W / 2, 455
        d.line([(ax, ay - 30), (ax, ay + 20 * kf)], fill=mix(BG, A.ACC, kf), width=6)
        d.polygon([(ax - 16, ay + 14), (ax + 16, ay + 14), (ax, ay + 36)], fill=mix(BG, A.ACC, kf))
    # COMUNIDAD sube letra a letra
    word = "COMUNIDAD"; f = F("o", A.fit("o", word, 1300, 260)); ch = cap_h(f)
    by = 770; win = (by - ch - 30, by + 30); hgt = win[1] - win[0]
    if t >= tc:
        band = Image.new("RGB", (W, hgt), BG); bd = ImageDraw.Draw(band)
        x = W / 2 - text_w(word, f) / 2
        for i, c in enumerate(word):
            k = eio(seg(t, tc + i * .03, tc + i * .03 + .38))
            if k > 0: bd.text((x, by - win[0] + hgt * (1 - k)), c, font=f, fill=mix(BG, A.ACC, out), anchor="ls")
            x += f.getlength(c)
        im.paste(band, (0, win[0]))
    if "sello_r" not in _TEL: _TEL["sello_r"] = _sello("RETO 2027", CREAM, tick=False)
    _pega_sello(im, _TEL["sello_r"], W / 2 + 470, by + 70, seg(t, ts2, ts2 + .25), alpha=out, giro=5, escala=.62)
    return im

# --- S18: la comunidad ya existe — citas reales (capturas del cliente, 11/11/2026), sin @ por discreción
S18_CITAS = [   # (texto literal, canal). «[…]» = recorte de la cita original
    ("Ha sido un descubrimiento este verano, en casa no pueden faltar", "COMENTARIO · INSTAGRAM"),
    ("Amo vuestra agua de coco […] la volví a encontrar y soy muy fan!!!", "MENSAJE DIRECTO"),
    ("Hace poco empece a tomarla, está buenísima, al finnnnn una que sabe bien", "COMENTARIO · TIKTOK"),
    ("Diosssss mi agua de coco favoritaaaa del momento!", "COMENTARIO · INSTAGRAM"),
    ("Me encanta el agua de coco, la mejor q hay", "MENSAJE DIRECTO"),
    ("awesome product! We need it in Germany!", "COMENTARIO · TIKTOK"),
    ("Mi nuevo vicio !!", "COMENTARIO · INSTAGRAM"),
    ("[…] era la única agua de coco que me gustaba", "COMENTARIO · TIKTOK"),
    ("[…] it's the best one I've ever tried. […] Big FAN!", "MENSAJE DIRECTO"),
    ("El de piña está brutal", "COMENTARIO · INSTAGRAM"),
    ("meilleur jus tellement bons surtout Coco", "COMENTARIO · TIKTOK"),
    ("Me encantan los platanitos picantes", "COMENTARIO · INSTAGRAM"),
]
S18_COLS, S18_CW = 4, 410

def _s18_tarjetas():
    if "s18" in _TEL: return _TEL["s18"]
    cw, fq, fl = S18_CW, F("d", 30, "Medium"), F("d", 18, "Bold")
    out = []
    for txt, canal in S18_CITAS:
        lineas = _parte(txt, fq, cw - 80)
        ch = 128 + len(lineas) * 41 + 46
        sombra = Image.new("RGBA", (cw + 60, ch + 60), (0, 0, 0, 0))
        ImageDraw.Draw(sombra).rounded_rectangle([30, 38, cw + 30, ch + 34], 26, fill=(40, 46, 32, 40))
        card = sombra.filter(ImageFilter.GaussianBlur(14)); cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([30, 30, cw + 30, ch + 30], 26, fill=(255, 255, 255, 255))
        draw_text(cd, 62, 30 + 112, "“", F("o", 96, "Bold"), A.ACC + (255,))
        for i, l in enumerate(lineas):
            draw_text(cd, 64, 30 + 146 + i * 41, l, fq, GREEN + (255,))
        draw_text(cd, 64, 30 + ch - 30, canal, fl, A.ACC + (255,), track=3)
        out.append(card)
    _TEL["s18"] = out; return out

def s18(t, D):
    """Las citas aparecen una a una (mosaico de 3 columnas) y, en «Ahora toca potenciarla», se apagan y entra la frase."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .4, D)
    cards = _s18_tarjetas(); cw = S18_CW; gap = 32; nc = S18_COLS; sep = 40
    tp = t_palabra("s18", "ahora", defecto=6.0) - .15
    kd = eio(seg(t, tp, tp + .5))                     # las citas se apagan
    cols, alt = [[] for _ in range(nc)], [0] * nc      # mampostería: cada tarjeta a la columna más baja
    for i, cdd in enumerate(cards):
        c = alt.index(min(alt)); cols[c].append(i); alt[c] += cdd.height - 60 + gap
    alturas = [sum(cards[i].height - 60 for i in c) + gap * (len(c) - 1) for c in cols]
    top0 = (H - max(alturas)) / 2
    x0 = (W - (nc * cw + (nc - 1) * sep)) / 2
    paso = (t_palabra("s18", "medio", defecto=5.4) - .75) / len(cards)
    t_in = [.75 + i * paso for i in range(len(cards))]   # entran todas mientras Alba habla, hasta «…de por medio»
    for c, idx in enumerate(cols):
        y = top0 + (max(alturas) - alturas[c]) / 2
        for i in idx:
            k = eo(seg(t, t_in[i], t_in[i] + .6)) * out * (1 - .93 * kd)
            if k > 0:
                cd = cards[i] if k >= 1 else cards[i].copy()
                if k < 1: cd.putalpha(cd.getchannel("A").point(lambda v: round(v * k)))
                im.paste(cd, (round(x0 + c * (cw + sep) - 30), round(y - 30 + 30 * (1 - min(1, k / max(1e-3, (1 - .93 * kd)))))), cd)
            y += cards[i].height - 60 + gap
    # frase final
    kh = eo(seg(t, tp + .15, tp + .6)) * out
    if kh > 0:
        f = F("o", 130, "Bold")
        draw_text(d, W / 2, H / 2 + 20 + 20 * (1 - kh), "AHORA TOCA POTENCIARLA", f, mix(BG, INK, kh), anchor="ms", track=4)
        lw = 560 * eio(seg(t, tp + .45, tp + 1.1))
        if lw > 1: d.rectangle([W / 2 - lw / 2, H / 2 + 62, W / 2 + lw / 2, H / 2 + 70], fill=mix(BG, A.ACC, kh))
    return im

# --- S19: «CÓMO LO HAREMOS» + las cinco palancas de 2027 (17/11: palancas cerradas, sobre verde como la slide del deck)
S19_ITEMS = []   # 17/11: la S19 queda como separador; cada palanca tiene su escena (S19a-S19e)

def _s19_tiempos():
    return [t_palabra("s19", w, defecto=dd) for (_, w), dd in zip(S19_ITEMS, (3.2, 4.4, 5.6, 6.9, 8.1))]

def s19(t, D):
    """Izquierda: CÓMO / LO HAREMOS + «Cinco palancas para construir comunidad». Derecha: 01–05 con la voz."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .4, D)
    ka = eo(seg(t, .2, .7)) * out
    ft = F("o", 140, "Bold"); xl = 130
    for i, l in enumerate(("CÓMO", "LO HAREMOS")):
        draw_text(d, xl, 380 + i * (cap_h(ft) + 30) + 20 * (1 - ka), l, ft, mix(BG, INK, ka), track=4)
    kb = eo(seg(t, t_palabra("s19", "cinco", defecto=1.4) - .1, t_palabra("s19", "cinco", defecto=1.4) + .4)) * out
    if kb > 0:
        fs = F("d", 40, "Bold"); y = 380 + 2 * (cap_h(ft) + 30) + 10
        draw_text(d, xl, y + 10 * (1 - kb), "Cinco palancas para construir comunidad", fs, mix(BG, INK, kb))
        lw = (text_w("Cinco palancas", fs) + 4) * eio(seg(t, t_palabra("s19", "cinco", defecto=1.4), t_palabra("s19", "cinco", defecto=1.4) + .6))
        d.rectangle([xl, y + 12, xl + lw, y + 17], fill=mix(BG, A.ACC, kb))
    ts = _s19_tiempos(); x0 = 1110; y0 = 330; paso = 118
    fn_, fi = F("o", 48, "Bold"), F("o", 50, "Medium")
    for i, ((txt, _), ti) in enumerate(zip(S19_ITEMS, ts)):
        k = eo(seg(t, ti - .2, ti + .3)) * out
        if k <= 0: continue
        sig = ts[i + 1] if i + 1 < len(ts) else 99
        act = 1 - .45 * eio(seg(t, sig - .2, sig + .2))     # el anterior se apaga un poco al llegar el siguiente
        y = y0 + i * paso
        draw_text(d, x0, y + 16 * (1 - k), f"{i + 1:02d}", fn_, mix(BG, A.ACC, k * act))
        draw_text(d, x0 + 86 - 30 * (1 - k), y + 16 * (1 - k), txt.upper(), fi, mix(BG, INK, k * act), track=3)
    return im

# --- S31-S32: cierre soñado (pedido del cliente, 11/11/2026)
S31_LINEAS = ["Y SI SOÑAMOS ALTO DE VERDAD", "Y CREAMOS LA PRÓXIMA", "CANCIÓN DEL VERANO CON"]

def s31(t, D):
    """Texto en tres líneas que entran una a una + puntos suspensivos que aparecen de uno en uno (sobre verde)."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .3, D)
    f = F("o", 104, "Bold"); ch = cap_h(f); paso = ch + 46
    y0 = H / 2 - paso + ch / 2
    tl = [_tpal("s31", "y", 1, defecto=.3) - .15, _tpal("s31", "creamos", defecto=1.0) - .4, _tpal("s31", "canción", defecto=1.7) - .2]
    fin = t_palabra("s31", "con", fin=True, defecto=2.2)
    for i, l in enumerate(S31_LINEAS):
        k = eo(seg(t, tl[i], tl[i] + .6)) * out
        if k > 0:
            col = A.ACC if i == 2 else INK
            dx = -50 if i == 2 else 0   # la última línea + «…» quedan centradas como bloque
            draw_text(d, W / 2 + dx, y0 + i * paso + 18 * (1 - k), l, f, mix(BG, col, k), anchor="ms", track=6)
    # «…» de uno en uno, con calma
    xs = W / 2 - 50 + (text_w(S31_LINEAS[2], f) + 6 * (len(S31_LINEAS[2]) - 1)) / 2 + 24
    for j in range(3):
        kd = eo(seg(t, fin - .15 + j * .25, fin + .05 + j * .25)) * out   # en el silencio tras «con…»
        if kd > 0:
            r = 11; cx = xs + j * 34; cy = y0 + 2 * paso - 8
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=mix(BG, A.ACC, kd))
    return im

def s32(t, D):
    """18/11: cierre en tríptico: tres planos verticales del videoclip de Bad Gyal (grabación de Juan, segundos 22-30),
    rotando entre paneles, sobre verde (montado con /tmp/trip.py → entradas/s32_triptico.mp4)."""
    if "s32" not in _TEL: _TEL["s32"] = Fuente(OUTDIR / "entradas/s32_triptico.mp4", W, H, D)
    return _TEL["s32"].frame().convert("RGB")

S01_ALA = [(643, 170), (790, 170), (793, 303), (787, 312), (720, 327), (643, 331)]   # ala del pájaro, px de la imagen
S01_PIVOTE = (742, 326)   # unión ala-cuerpo

def _s01_capas():
    """Separa el ala del logo de la imagen de portada: fondo con el ala borrada (inpaint) + ala RGBA suelta."""
    if "s01" not in _TEL:
        import numpy as np, cv2
        ref = Image.open(ROOT / "material/s01_portada/portada_referencia.png").convert("RGB")
        arr = np.asarray(ref).astype(np.float32)
        lum = arr.mean(axis=2)
        alfa = np.clip((lum - 130) / (215 - 130), 0, 1)               # crema del logo vs fondo oscurecido
        zona = Image.new("L", ref.size, 0); ImageDraw.Draw(zona).polygon(S01_ALA, fill=255)
        zona_np = np.asarray(zona) > 0
        a_ala = (alfa * zona_np * 255).astype(np.uint8)
        base = S01_ALA[2:][::-1]                                       # borde inferior del ala (junta con el cuerpo)
        bm = Image.new("L", ref.size, 0); ImageDraw.Draw(bm).polygon(base + [(x, y - 12) for x, y in base[::-1]], fill=255)
        banda = zona_np & (np.asarray(bm) > 0)                         # franja de ~12 px sobre la junta
        hueco = cv2.dilate(((lum > 105) & zona_np).astype(np.uint8) * 255, np.ones((9, 9), np.uint8))
        hueco[~zona_np] = 0                                            # solo se borra dentro del ala
        fondo = cv2.inpaint(np.asarray(ref), hueco, 9, cv2.INPAINT_TELEA)
        fondo = np.where((zona_np & ~banda)[..., None], fondo, np.asarray(ref))   # cuerpo y junta originales: tapan la costura
        crema = tuple(int(v) for v in np.median(arr[a_ala > 250], axis=0))
        ala = Image.new("RGB", ref.size, crema).convert("RGBA"); ala.putalpha(Image.fromarray(a_ala))   # sin halo oscuro al girar
        _TEL["s01"] = (Image.fromarray(fondo).convert("RGBA"), ala)
    return _TEL["s01"]

def s01(t, D):
    """Portada (18/11): imagen de Juan (platanitos con velo verde + logo Amazonia); el pájaro bate el ala suave,
    entra desde verde con zoom lento."""
    fondo, ala = _s01_capas()
    ang = 5 * math.sin(2 * math.pi * t / 1.1)                         # aleteo suave: ±5°
    px, py = S01_PIVOTE
    fr = fondo.copy(); fr.alpha_composite(ala.rotate(ang, resample=Image.BILINEAR, center=(px, py)))
    fr = fr.convert("RGB")
    r = max(W / fr.width, H / fr.height)
    fr = fr.resize((round(fr.width * r), round(fr.height * r)), Image.LANCZOS)
    fr = fr.crop(((fr.width - W) // 2, (fr.height - H) // 2, (fr.width - W) // 2 + W, (fr.height - H) // 2 + H))
    z = 1.06 - .06 * eo(t / D)
    fr = fr.transform((W, H), Image.AFFINE, (1 / z, 0, W / 2 - W / 2 / z, 0, 1 / z, H / 2 - H / 2 / z), resample=Image.BICUBIC)
    k = eo(seg(t, 0, .8)) * (1 - seg(t, D - .4, D))
    return Image.blend(Image.new("RGB", (W, H), GREEN), fr, k)

def s01_texto(t, D):
    """Portada: AMAZONIA · 2027 · ES OTRA HISTORIA — texto animado centrado."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .4, D)
    fA, f27, fH = F("o", 110, "Medium"), F("o", 360, "Bold"), F("o", 64, "Medium")
    yA, y27, yH = 330, 330 + 40 + cap_h(f27), 330 + 40 + cap_h(f27) + 70 + cap_h(fH)
    # AMAZONIA
    a = eo(seg(t, .2, .7)) * out
    if a > 0: draw_text(d, W / 2, yA + 30 * (1 - a), "AMAZONIA", fA, mix(BG, INK, a), anchor="ms", track=22)
    # 2027 sube cifra a cifra dentro de una ventana
    hgt = cap_h(f27) + 40; top = y27 - cap_h(f27) - 20
    band = Image.new("RGB", (W, hgt), BG); bd = ImageDraw.Draw(band)
    x = W / 2 - (text_w("2027", f27) + 3 * 10) / 2
    for i, c in enumerate("2027"):
        k = eio(seg(t, .55 + i * .08, .55 + i * .08 + .5))
        if k > 0: bd.text((x, y27 - top + hgt * (1 - k)), c, font=f27, fill=mix(BG, A.ACC, out), anchor="ls")
        x += f27.getlength(c) + 10
    im.paste(band, (0, top))
    # ES OTRA HISTORIA + subrayado
    b = eo(seg(t, 1.35, 1.8)) * out
    if b > 0: draw_text(d, W / 2, yH + 20 * (1 - b), "ES OTRA HISTORIA", fH, mix(BG, INK, b), anchor="ms", track=10)
    lw = 420 * eio(seg(t, 1.6, 2.3))
    if lw > 1: d.rectangle([W / 2 - lw / 2, yH + 40, W / 2 + lw / 2, yH + 47], fill=mix(BG, A.ACC, out))
    return im

def s02(t, D):
    """185 SEGUIDORES · 0 EN TIKTOK — dos cifras grandes, la primera cuenta, la segunda cae."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    t185, t0 = t_palabra("s02", "185") - .15, t_palabra("s02", "ninguna") - .1
    out = 1 - seg(t, D - .4, D)
    fn = F("o", 330); fl = F("o", 64, "Medium"); fs = F("d", 34, "Regular")
    by = 640; xs = (W / 2 - 400, W / 2 + 400)
    # rótulo superior
    ka = seg(t, .15, .5) * out
    draw_text(d, W / 2, by - cap_h(fn) - 90, "INICIOS DE 2025", F("o", 46, "Medium"), mix(BG, A.KICK, ka), anchor="ms", track=8)
    # divisor
    la = seg(t, .3, .7) * out
    d.line([(W / 2, by - cap_h(fn) - 10), (W / 2, by + 150)], fill=mix(BG, INK, .25 * la), width=3)
    # 185 contando
    a = seg(t, t185, t185 + .25) * out
    if a > 0:
        k = A.eo5(seg(t, t185, t185 + 1.1)); y = by + 25 * (1 - eo(seg(t, t185, t185 + .35)))
        draw_text(d, xs[0], y, A.es_num(185 * k), fn, mix(BG, A.ACC, a), tab=True, anchor="ms")
        draw_text(d, xs[0], y + 95, "SEGUIDORES", fl, mix(BG, INK, a), anchor="ms", track=4)
        draw_text(d, xs[0], y + 145, "en Instagram", fs, mix(BG, INK, a * .7), anchor="ms")
    # 0 en TikTok
    b = seg(t, t0, t0 + .2) * out
    if b > 0:
        y = by - 60 * (1 - eo(seg(t, t0, t0 + .35)))
        draw_text(d, xs[1], y, "0", fn, mix(BG, A.ACC, b), anchor="ms")
        draw_text(d, xs[1], by + 95, "EN TIKTOK", fl, mix(BG, INK, b), anchor="ms", track=4)
        draw_text(d, xs[1], by + 145, "ni una cuenta", fs, mix(BG, INK, b * .7), anchor="ms")
    return im

_LOCKUP = {}
def _lockup_otra_historia(w):
    """Logo «Otra historia» de marca (beige), recortado a su contenido y escalado a ancho w."""
    if w not in _LOCKUP:
        lg = Image.open(ROOT / "material/marca/logo-otrahistoria-sin-es-beige.png").convert("RGBA")
        lg = lg.crop(lg.getchannel("A").getbbox())
        _LOCKUP[w] = lg.resize((w, round(lg.height * w / lg.width)), Image.LANCZOS)
    return _LOCKUP[w]

def s03(t, D):
    """18/11 (referencia de Juan): «DESDE ABRIL DE / 2025 EMPEZAMOS / A CONTAR» grande y apagado, y encima el
    sello de marca «OTRA HISTORIA» ligeramente girado, que cae cuando Alba lo dice."""
    im, d = A.canvas(); BG, INK = A.BG, A.INK
    out = 1 - seg(t, D - .35, D)
    f = F("o", 235); ch = cap_h(f); paso = ch + 30; x0 = 80; y0 = 170
    to = t_palabra("s03", "otra", defecto=2.2) - .15
    apaga = 1 - .8 * eio(seg(t, to - .1, to + .35))                     # 18/11: crema al entrar, se apaga con el sello
    for i, l in enumerate(("DESDE ABRIL DE", "2025 EMPEZAMOS", "A CONTAR")):
        k = eo(seg(t, .1 + i * .15, .6 + i * .15)) * out
        if k > 0: draw_text(d, x0, y0 + ch + i * paso + 20 * (1 - k), l, f, mix(BG, INK, apaga * k), track=2)
    k = eio(seg(t, to, to + .45)) * out
    if k > 0:
        lg = _lockup_otra_historia(1180)
        sc = 1.18 - .18 * k
        lg = lg.resize((round(lg.width * sc), round(lg.height * sc)), Image.LANCZOS).rotate(3 + 2 * (1 - k), expand=True, resample=Image.BICUBIC)
        if k < 1: lg.putalpha(lg.getchannel("A").point(lambda v: round(v * k)))
        cx, cy = x0 + 660, y0 + 2 * paso + ch + 60
        im.paste(lg, (round(cx - lg.width / 2), round(cy - lg.height / 2)), lg)
    return im

LOCALES = {"s19a": s19a, "s19b": s19b, "s19c": s19c, "s19d": s19d, "s19e": s19e, "s18b": s18b, "s18c": s18c, "s01": s01, "s32": s32, "s31": s31, "s19": s19, "s18": s18, "s17": s17, "s16": s16, "s14": s14, "s15": s15, "s13": s13, "s12": s12, "s11": s11, "s10": s10, "s05": s05, "s08": s08, "s09": s09, "s02": s02, "s03": s03}

# ------------------------------------------------------------------ escena de un tramo
class Escena:
    def __init__(self, k):
        self.k, self.t = k, TRAMOS[k]
        self.D, self.v0, self.v1 = duraciones(k)
        A.tema(tema(k))
        self.bg = self.t.get("fondo", A.BG)
        self.subs = [(a, b, A.subtitle_layer(txt, CAJA_SUB)) for a, b, txt in frases(k)] if SUBTITULOS else []
        self.dy = 0
        self.fuentes = {}
        hs = self.t.get("huecos", [])
        if "anim" in self.t or "local" in self.t:
            A.CUE.clear(); A.CUE.update(A.cues(k))
            self.fn = getattr(A, self.t["anim"]) if "anim" in self.t else LOCALES[self.t["local"]]
            if "anim" in self.t and not SUBTITULOS: self.dy = A.centrar(self.fn, self.D - 1 / FPS)
            return
        n = 1 if self.t.get("ciclo") or self.t.get("especial") in ("grid_scroll", "grid_fundido") else len(hs)
        fmt = hs[0]["formato"] if hs else "9:16"
        self.rects = slots(n, fmt, 400 if self.t.get("palabra") else None)
        if self.t.get("palanca") and fmt == "9:16":   # deja sitio al título a la izquierda y centra el conjunto
            tw = titulo_palanca(k).width * TIT_ESCALA
            x0 = min(r[0] for r in self.rects); x1 = max(r[0] + r[2] for r in self.rects)
            dx = round((W - (tw + 90 + x1 - x0)) / 2 + tw + 90 - x0)
            self.rects = [(x + dx, y, w, h) for x, y, w, h in self.rects]
        self.huecos = []
        for i, hh in enumerate(hs):
            x, y, w, h = self.rects[min(i, len(self.rects) - 1)]
            self.huecos.append(hueco_img(w, h, hh["label"], r=26 if fmt == "9:16" else 34))
            if existe(hh["ruta"]):
                self.fuentes[i] = Fuente(hh["ruta"], w, h, self.D)
        if self.t.get("ciclo"):
            fr = frases(k)[self.t.get("ciclo_desde", 0):]
            self.cambios = [a for a, _, _ in fr][:len(hs)]
            self.cambios[0] = 0
        if self.t.get("especial") in ("grid_scroll", "grid_fundido"):
            x, y, w, h = self.rects[0]
            g = Image.open(GRID_ANTIGUO).convert("RGB")
            self.grid = g.resize((w, round(g.height * w / g.width)), Image.LANCZOS)
            self.mask = rect_mask(w, h, 26)
        self.mask_cache = {}
        if not SUBTITULOS:   # sin subtítulos: centrar huecos y pies en el cuadro
            self.dy = A.centrar(lambda t, D: self.contenido(t).convert("RGB"), self.D, (0.6,))

    def _mask(self, w, h):
        if (w, h) not in self.mask_cache: self.mask_cache[(w, h)] = rect_mask(w, h, 26)
        return self.mask_cache[(w, h)]

    def _pega_pieza(self, lay, i, x, y, w, h):
        """Pieza real si existe; si no, el hueco."""
        if i in self.fuentes:
            fr = self.fuentes[i].frame()
            lay.paste(fr, (x, y), self._mask(w, h))
            if self.t.get("capa_verde"):
                ov = Image.new("RGBA", (w, h), GREEN + (round(255 * self.t["capa_verde"]),))
                lay.alpha_composite(ov, (x, y))
        else:
            lay.alpha_composite(self.huecos[i], (x, y))

    def contenido(self, t):
        """Capa de contenido (huecos, piezas, pies) antes del zoom lento."""
        lay = Image.new("RGBA", (W, H), self.bg + (255,))
        d = ImageDraw.Draw(lay)
        esp = self.t.get("especial")
        if esp == "grid_scroll":
            x, y, w, h = self.rects[0]
            k = eio(seg(t, self.v0, self.v1))
            off = round((self.grid.height - h) * k)
            lay.paste(self.grid.crop((0, off, w, off + h)), (x, y), self.mask)
            d.rounded_rectangle([x, y, x + w - 1, y + h - 1], radius=26, outline=A.ACC, width=3)
            a = seg(t, self.v1 - 1.6, self.v1 - 1.2)
            if a > 0:
                pie(d, x, y + h + 60, w, "185 SEGUIDORES · 0 EN TIKTOK", a)
        elif esp == "grid_fundido":
            x, y, w, h = self.rects[0]
            mid = (self.v0 + self.v1) / 2
            k = eio(seg(t, mid - .4, mid + .4))
            old = Image.new("RGBA", (w, h), (0, 0, 0, 0)); old.paste(self.grid.crop((0, 0, w, h)), (0, 0), self.mask)
            new = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            if 0 in self.fuentes: new.paste(self.fuentes[0].frame(), (0, 0), self.mask)
            else: new = self.huecos[0]
            lay.alpha_composite(Image.blend(old, new, k), (x, y))
            if k < 1: d.rounded_rectangle([x, y, x + w - 1, y + h - 1], radius=26, outline=mix(A.ACC, A.ACC, 1), width=3)
            pie(d, x, y + h + 60, w, "GRID ANTIGUO" if k < .5 else "GRID ACTUAL", 1 - abs(k - .5) * 2 if .3 < k < .7 else 1)
        elif self.t.get("ciclo"):
            x, y, w, h = self.rects[0]
            i = max(j for j, c in enumerate(self.cambios) if t >= c) if t >= 0 else 0
            self._pega_pieza(lay, i, x, y, w, h)
            n = len(self.cambios)   # puntos de progreso
            for j in range(n):
                cx = W / 2 + (j - (n - 1) / 2) * 34
                d.ellipse([cx - 6, y + h + 34, cx + 6, y + h + 46], fill=A.ACC if j == i else mix(A.BG, A.INK, .25))
        else:
            for i, (x, y, w, h) in enumerate(self.rects):
                self._pega_pieza(lay, i, x, y, w, h)
                hh = self.t["huecos"][i]
                if hh.get("cuenta"):
                    t0 = TIT_CONTENIDO + .3 if self.t.get("palanca") else .4
                    pie_contador(d, x, y + h + 60, w, *hh["cuenta"], A.eo5(seg(t, t0 + i * .12, t0 + i * .12 + 1.8)))
                elif hh.get("pie") and self.t["huecos"][0]["formato"] == "9:16":
                    pie(d, x, y + h + 60, w, hh["pie"])
            if self.t.get("titulo"):   # S01: título a los lados de la pieza vertical
                x, y, w, h = self.rects[0]
                ancho = h * 9 / 16; izq, der = x + (w - ancho) / 2 - 70, x + (w + ancho) / 2 + 70
                cy = y + h / 2
                a1, a2, a3 = (eo(seg(t, t0, t0 + .45)) for t0 in (.25, .55, .85))
                f27, fH = F("o", 230, "Bold"), F("o", 54, "Medium")
                tam = 150
                while text_w("AMAZONIA", F("o", tam, "Bold")) + 28 > izq - 90: tam -= 2   # que quepa en el lateral
                fA = F("o", tam, "Bold"); base = cy + cap_h(f27) / 2 - 40   # misma línea base que 2027
                if a1 > 0: draw_text(d, izq, base + 40 * (1 - a1), "AMAZONIA", fA, mix(self.bg, CREAM, a1), anchor="rs", track=4)
                if a2 > 0: draw_text(d, der, cy + cap_h(f27) / 2 - 40 + 40 * (1 - a2), "2027", f27, mix(self.bg, A.ACC, a2), track=4)
                if a3 > 0: draw_text(d, der + 6, cy + cap_h(f27) / 2 + 50 + cap_h(fH) + 20 * (1 - a3), "ES OTRA HISTORIA", fH, mix(self.bg, CREAM, a3), track=6)
            if self.t.get("palabra"):
                w0, txt = self.t["palabra"]
                ts = next((p["s"] for p in palabras(self.k) if A._limpia(p["w"]) == A._limpia(w0)), self.v1 - .8)
                a = eo(seg(t, ts - .1, ts + .35))
                if a > 0:
                    f = F("o", 64, "Bold")
                    draw_text(d, W / 2, 46 + 345 + cap_h(f) / 2 + 30 * (1 - a), txt, f, mix(A.BG, A.ACC, a), anchor="ms", track=4)
        return lay

    def frame(self, t):
        if "anim" in self.t or "local" in self.t:
            im = A.desplaza(self.fn(t, self.D - 1 / FPS), self.dy).convert("RGBA")
        else:
            lay = A.desplaza(self.contenido(t), self.dy)
            if self.t.get("palanca"):   # las piezas entran cuando el título ya se ha colocado
                kc = eo(seg(t, TIT_CONTENIDO, TIT_CONTENIDO + .5))
                capa = Image.new("RGBA", (W, H), self.bg + (255,))
                lay = Image.blend(capa, ImageChops.offset(lay, 0, round(50 * (1 - kc))), kc) if kc < 1 else lay
            s = 1 + 0.03 * (t / self.D)          # zoom lento del 3 %
            cx, cy = W / 2, (400 + self.dy)
            im = lay.transform((W, H), Image.AFFINE, (1 / s, 0, cx - cx / s, 0, 1 / s, cy - cy / s),
                               resample=Image.BICUBIC, fillcolor=self.bg + (255,))
        if self.t.get("palanca") and "local" not in self.t:
            x, y, w, h = self.rects[0]
            dibuja_titulo(im, t, titulo_palanca(self.k), x - 90, y + h / 2 + self.dy, 1 - seg(t, self.D - .4, self.D))
        if self.t.get("remate"):   # cifra final a pantalla completa: se van las piezas y cuenta la cifra
            r = self.t["remate"]; tr = t_palabra(self.k, r["palabra"]) - .15; tc = t_palabra(self.k, r["cuenta"]) - .1
            kr = eio(seg(t, tr, tr + .4))
            if kr > 0:
                im = Image.blend(im, Image.new("RGBA", (W, H), self.bg + (255,)), kr)
                dd = ImageDraw.Draw(im); BG, INK = A.BG, A.INK; out = 1 - seg(t, self.D - .4, self.D)
                fn = F("o", 330); by = 640
                ka = eo(seg(t, tr + .2, tr + .55)) * out
                draw_text(dd, W / 2, by - cap_h(fn) - 70, r["kicker"], F("o", 46, "Medium"), mix(BG, A.KICK, ka), anchor="ms", track=8)
                a = seg(t, tc, tc + .25) * out
                if a > 0:
                    k = A.eo5(seg(t, tc, tc + 1.3)); y = by + 25 * (1 - eo(seg(t, tc, tc + .35)))
                    draw_text(dd, W / 2, y, A.es_num(r["valor"] * k), fn, mix(BG, A.ACC, a), tab=True, anchor="ms")
                    draw_text(dd, W / 2, y + 95, r["rotulo"], F("o", 64, "Medium"), mix(BG, INK, a), anchor="ms", track=4)
                    draw_text(dd, W / 2, y + 145, r["sub"], F("d", 34, "Regular"), mix(BG, INK, a * .7), anchor="ms")
        ts = [(a0, b0) for a0, b0, _ in self.subs]
        for j, (a0, b0, sub) in enumerate(self.subs):
            a = A.alfa_sub(t, j, ts)
            if a > 0:
                im.alpha_composite(sub if a >= 1 else A.fade_layer(sub, a))
        # fundido de entrada y salida (0,15 s + 0,15 s = 0,3 s entre tramos)
        f = min(seg(t, 0, FUNDIDO), 1 - seg(t, self.D - FUNDIDO, self.D - 1 / FPS))
        if f < 1:
            im = Image.blend(Image.new("RGBA", (W, H), self.bg + (255,)), im, f)
        if ETIQUETA:
            dd = ImageDraw.Draw(im)
            txt, fe = f"{self.k.upper()} · {self.t['nombre']}", F("d", 24, "Medium")
            dd.rounded_rectangle([56, 56, 56 + text_w(txt, fe) + 28, 96], radius=10, fill=mix(self.bg, A.INK, .12))
            draw_text(dd, 70, 84, txt, fe, mix(self.bg, A.INK, .75))
        return im.convert("RGB")

    def close(self):
        for f in self.fuentes.values(): f.close()

# ------------------------------------------------------------------ render
ETIQUETA = True
SUBTITULOS = False   # el cliente pidió quitarlos; --subtitulos los vuelve a poner

def render_tramo(k):
    TRAMOS_DIR.mkdir(parents=True, exist_ok=True)
    e = Escena(k)
    n = round(e.D * FPS); out = TRAMOS_DIR / f"{k}{EXT}"
    audio = A.AUDIO / TRAMOS[k]["audio"] if TRAMOS[k]["audio"] else None
    ain = ["-i", str(audio)] if audio else ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono"]
    efectos = SFX[k](e.D) if k in SFX else []   # efectos de transición: (segundo, nombre en audio/sfx)
    fx_in, fx_f = [], ""
    for j, (ts, nom) in enumerate(efectos):
        fx_in += ["-i", str(ROOT / "audio/sfx" / f"{nom}.wav")]
        fx_f += f"[{j + 2}:a]adelay={max(0, round(ts * 1000))}:all=1[x{j}];"
    if efectos:
        mezcla = ["-filter_complex", fx_f + "[1:a]apad[v];[v]" + "".join(f"[x{j}]" for j in range(len(efectos)))
                  + f"amix=inputs={len(efectos) + 1}:normalize=0:duration=first[a]", "-map", "0:v", "-map", "[a]"]
    else:
        mezcla = ["-map", "0:v", "-map", "1:a", "-af", "apad"]
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           *ain, *fx_in, *mezcla, "-t", f"{n / FPS:.3f}",
           *VCODEC, "-pix_fmt", "yuv420p", "-r", str(FPS),
           *(["-c:a", "pcm_s16le"] if HQ else ["-c:a", "aac", "-b:a", "192k"]), "-ar", "44100", "-ac", "1",
           "-movflags", "+faststart", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(e.frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); e.close()
    print(f"{k}: {n / FPS:5.2f} s · {out.stat().st_size / 1e6:.2f} MB")

def unir(hasta=None, final=None, solo=None):
    """Une los tramos (todos, solo hasta «hasta», o solo la lista «solo») y mezcla la música."""
    global FINAL
    if final: FINAL = final
    lst = OUTDIR / "tramos.txt"
    orden = [k for k in TRAMOS if not TRAMOS[k].get("omitir")]
    if hasta: orden = orden[:orden.index(hasta) + 1]
    if solo: orden = [k for k in orden if k in solo]
    ks = [k for k in orden if (TRAMOS_DIR / f"{k}{EXT}").exists()]
    lst.write_text("".join(f"file '{TRAMOS_DIR.name}/{k}{EXT}'\n" for k in ks))
    if MUSICA and Path(MUSICA).exists():
        tmp = OUTDIR / f"_voz{EXT}"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(tmp)], check=True)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(tmp)],
                                   capture_output=True, text=True).stdout)
        md = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(MUSICA)],
                                  capture_output=True, text=True).stdout)
        tempo = f"atempo={md / dur:.5f}," if 0.97 < md / dur < 1 else ""   # estira hasta un 3 % sin cambiar el tono
        if tempo: print(f"música {md:.2f}s → {dur:.2f}s ({tempo[:-1]})")
        # si alguna sección pide apagar la música (p. ej. S31 antes de Bad Gyal), se funde ahí y no vuelve
        fade_st, fade_d, acum = dur - 2.5, 2.5, 0.0
        for k in ks:
            if TRAMOS[k].get("musica_fuera"):
                fade_st, fade_d = acum + TRAMOS[k]["musica_fuera"](), 1.2; break
            acum += _dur(TRAMOS_DIR / f"{k}{EXT}")
        flt = (f"[1:a]{tempo}atrim=0:{dur:.3f},afade=t=in:d=1,afade=t=out:st={fade_st:.3f}:d={fade_d},volume={MUSICA_DB}dB[m];"
               f"[0:a]aformat=channel_layouts=stereo[v];[v][m]amix=inputs=2:normalize=0:duration=first[a]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-stream_loop", "-1", "-i", str(MUSICA), "-filter_complex", flt,
                        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                        "-movflags", "+faststart", str(FINAL)], check=True)
        tmp.unlink()
    else:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(FINAL)], check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(FINAL)],
                               capture_output=True, text=True).stdout)
    print(f"\n{FINAL.relative_to(ROOT)}: {len(ks)} tramos · {int(dur // 60)}:{dur % 60:05.2f} · {FINAL.stat().st_size / 1e6:.1f} MB")

def _dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                capture_output=True, text=True).stdout)

def seccion(sel):
    """Vista previa solo de los tramos pedidos, sin música (--con-musica la añade en su punto del montaje)."""
    orden = [k for k in TRAMOS if not TRAMOS[k].get("omitir")]
    sel = [k for k in orden if k in sel]
    dest = OUTDIR / "secciones"; dest.mkdir(exist_ok=True)
    out = dest / f"{'_'.join(sel)}{VOCES[VOZ][1]}{'_HQ' if HQ else ''}.mp4"
    lst = dest / "_lista.txt"
    lst.write_text("".join(f"file '{(TRAMOS_DIR / f'{k}{EXT}').resolve()}'\n" for k in sel))
    # punto de partida en el montaje completo (los tramos que faltan se cuentan por su duración prevista)
    durs = {k: _dur(TRAMOS_DIR / f"{k}{EXT}") if (TRAMOS_DIR / f"{k}{EXT}").exists() else Escena(k).D for k in orden}
    total = sum(durs.values()); ini = sum(durs[k] for k in orden[:orden.index(sel[0])])
    dur = sum(durs[k] for k in sel)
    tmp = dest / f"_voz{EXT}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(tmp)], check=True)
    if "--con-musica" in sys.argv and MUSICA and Path(MUSICA).exists():
        md = _dur(MUSICA); r = md / total
        tempo = f"atempo={r:.5f}," if 0.97 < r < 1 else ""
        flt = (f"[1:a]{tempo}atrim={ini:.3f}:{ini + dur:.3f},asetpts=PTS-STARTPTS,volume={MUSICA_DB}dB[m];"
               f"[0:a]aformat=channel_layouts=stereo[v];[v][m]amix=inputs=2:normalize=0:duration=first[a]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-i", str(MUSICA), "-filter_complex", flt,
                        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                        "-movflags", "+faststart", str(out)], check=True)
    else:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-movflags", "+faststart", str(out)], check=True)
    tmp.unlink(); lst.unlink()
    print(f"\n{out.relative_to(ROOT)}: {', '.join(sel)} · {_dur(out):.2f} s · empieza en el {int(ini // 60)}:{ini % 60:05.2f} del montaje")
    return out

def frames(spec):
    (OUTDIR / "frames").mkdir(parents=True, exist_ok=True)
    for kv in spec.split(","):
        k, t = kv.split(":"); e = Escena(k)
        p = OUTDIR / "frames" / f"{k}_{t}s.png"; e.frame(float(t)).save(p); e.close(); print(p.relative_to(ROOT))

if __name__ == "__main__":
    args = sys.argv[1:]
    ETIQUETA = "--sin-etiqueta" not in args
    SUBTITULOS = "--subtitulos" in args
    if "--voz" in args: i = args.index("--voz"); del args[i:i + 2]
    if "--hq" in args: args.remove("--hq")
    if "--frames" in args:
        frames(args[args.index("--frames") + 1]); sys.exit()
    if "--hasta" in args:   # montaje parcial: renderiza y une desde S01 hasta la sección indicada
        h = args[args.index("--hasta") + 1].lower()
        orden = [k for k in TRAMOS if not TRAMOS[k].get("omitir")]
        for k in orden[:orden.index(h) + 1]: render_tramo(k)
        unir(h, OUTDIR / f"amazonia_2027_borrador_v5{VOCES[VOZ][1]}_hasta_{h}{'_HQ' if HQ else ''}.mp4"); sys.exit()
    pedidos = [a.lower() for a in args if a.lower() in TRAMOS]
    if pedidos and "--unir" not in args:
        # por secciones: solo renderiza lo pedido y saca su vista previa (no rehace el vídeo completo)
        for k in pedidos: render_tramo(k)
        seccion(pedidos); sys.exit()
    if "--solo-unir" not in args:
        for k in pedidos or [k for k in TRAMOS if not TRAMOS[k].get("omitir")]:
            render_tramo(k)
    unir()
