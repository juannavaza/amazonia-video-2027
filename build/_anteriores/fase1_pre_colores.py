"""Fase 1 · vídeos tipo B (animación por código) para Amazonia Propuesta Digital 2027.

Uso:  .venv/bin/python build/fase1.py [s12 s13 ...]   (sin args = todos)
      --dur s12=5.2   fuerza la duración
      --mudo          sin locución ni subtítulos

Formato 16:9 · 1920×1080 · 30 fps. Con locución (audio/tiempos.json) la duración se ajusta a la voz y la
animación se sincroniza con las palabras. Subtítulos de la locución en el tercio inferior (y > 820).
Cada vídeo arranca y termina en el mismo frame para que el loop sea limpio.
"""
import json, math, os, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "videos"
W, H, FPS = 1920, 1080, 30
GREEN = (0x3E, 0x44, 0x23)   # 18/11: Pantone 5747 C del manual (antes 2F3B26)
CREAM = (0xE8, 0xD6, 0xC4)   # 18/11: Pantone 9183 C del manual (antes F3EADF)
YELLOW = (0xF0, 0xB4, 0x3A)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
TEAL = (0x69, 0xB4, 0x92)    # acentos de la presentación de referencia (brief de Amazonia)
CORAL = (0xE3, 0x5B, 0x66)

# Temas: «verde» (fondo verde, texto crema) y «crema» (fondo beige de marca, texto verde)
TEMAS = {"verde": dict(BG=GREEN, INK=CREAM, KICK=YELLOW, NUM=CREAM, NUM2=CREAM),
         "crema": dict(BG=CREAM, INK=GREEN, KICK=TEAL, NUM=YELLOW, NUM2=TEAL)}
BG, INK, KICK, NUM, NUM2 = GREEN, CREAM, YELLOW, CREAM, CREAM
def tema(nombre):
    globals().update(TEMAS[nombre])

# Guion (locución) tal cual lo pasó Juan — se usa para los subtítulos.
GUION = {
    "s12": "Y los resultados llegaron.",
    "s13": "53,5 millones de impactos. 18.011 seguidores en Instagram. 7.823 en TikTok.",
    "s14": "El encargo de notoriedad está cumplido.",
    "s15": "De 1,3 millones de impactos al mes en 2025 a 4,2 millones en 2026.",
    "s16": "Y en 2027, ¿qué pasa?",
    "s17": "En 2027 pasamos de notoriedad a comunidad.",
    "s24": "Notoriedad e interacción, medidas por separado.",
}

# Locución (audio/tiempos.json, generado por build/locucion.py) y palabras con tiempo (faster-whisper)
AUDIO = ROOT / os.environ.get("AMAZONIA_AUDIO", "audio")   # carpeta de la voz: audio (Juaniyo) o audio/alba
_TJ = AUDIO / "tiempos.json"
TIEMPOS = json.load(open(_TJ)) if _TJ.exists() else {}
_PJ = ROOT / TIEMPOS.get("_meta", {}).get("palabras", "audio/originales/palabras_alba.json")
_PAL = json.load(open(_PJ)) if _PJ.exists() else []
CUE = {}   # tiempos de sincronía del vídeo que se está renderizando

def _limpia(w): return re.sub(r"[^\wáéíóúñü¿?]", "", w.lower())
def palabra(k, w, n=1, fin=False):
    """Segundo (en el vídeo final) en que se dice la n-ésima palabra w de la locución de la slide k."""
    if "palabras" in TIEMPOS[k]:   # sección regrabada aparte (build/sustituir_frase.py)
        x = [x for x in TIEMPOS[k]["palabras"] if _limpia(x["w"]) == _limpia(w)][n - 1]
        return (x["e"] if fin else x["s"]) + 0.5
    a, b = TIEMPOS[k]["origen"]
    hits = [x for x in _PAL if a - .05 <= x["s"] < b and _limpia(x["w"]) == _limpia(w)]
    x = hits[n - 1]
    return (x["e"] if fin else x["s"]) - a + 0.5

def cues(k):
    if k not in TIEMPOS: return {}
    fr = TIEMPOS[k]["frases"]
    return {
        "s13": lambda: {"s13": [f - .1 for f in fr]},
        "s15": lambda: {},   # 17/11: la S15 local usa _s15_tiempos() en borrador.py
        "s16": lambda: {"s16_start": fr[0], "s16_end": palabra(k, "pasa?", fin=True)},
        "s17": lambda: {"s17": palabra(k, "comunidad") - .45},
        "s24": lambda: {"s24": palabra(k, "interacción") - .25},
    }.get(k, dict)()

def subtitulos(k):
    """[(inicio, fin, texto)] por frase del guion, con los tiempos de la locución."""
    frases = re.split(r"(?<=[.?!])\s+", GUION[k].strip())
    t = TIEMPOS[k]; fin_voz = t["duracion"] - 0.5 + 0.25
    ini = t["frases"] if len(t["frases"]) == len(frases) else [t["frases"][0]] if len(frases) == 1 else None
    if ini is None:   # nº de frases no coincide: una sola rótulo con todo el texto
        return [(t["frases"][0], fin_voz, GUION[k])]
    return [(ini[i], ini[i + 1] if i + 1 < len(ini) else fin_voz, frases[i]) for i in range(len(frases))]

# ---------------------------------------------------------------- utilidades
_fc = {}
# 18/11: tipografías del manual de marca (Komu para titulares, Proxima Nova para texto). AMAZONIA_MARCA=0 vuelve a Oswald/DM Sans.
MARCA = os.environ.get("AMAZONIA_MARCA", "1") != "0"
KOMU_ESCALA = 81 / 70        # Komu tiene la altura de mayúsculas más baja que Oswald: se escala para igualarla
PROXIMA = {"Regular": "ProximaNova-Regular.otf", "Medium": "ProximaNova-Semibold.otf", "SemiBold": "ProximaNova-Semibold.otf",
           "Bold": "ProximaNova-Bold.otf"}
def F(kind, size, weight="Bold"):
    key = (kind, int(size), weight)
    if key not in _fc and MARCA:
        if kind == "o": _fc[key] = ImageFont.truetype(str(ROOT / "fonts/Komu.otf"), int(size * KOMU_ESCALA))
        else: _fc[key] = ImageFont.truetype(str(ROOT / "fonts" / PROXIMA.get(weight, "ProximaNova-Regular.otf")), int(size))
    if key not in _fc:
        f = ImageFont.truetype(str(ROOT / "fonts" / ("Oswald.ttf" if kind == "o" else "DMSans.ttf")), int(size))
        if kind == "o":
            f.set_variation_by_name(weight)
        else:
            wg = {"Regular": 400, "Medium": 500, "SemiBold": 600, "Bold": 700}[weight]
            f.set_variation_by_axes([min(40, max(9, size * 0.5)), wg])
        _fc[key] = f
    return _fc[key]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= b)
def eo(x): return 1 - (1 - x) ** 3             # ease out cubic
def eo5(x): return 1 - (1 - x) ** 5
def ei(x): return x ** 3
def eio(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def mix(a, b, k): return tuple(round(a[i] + (b[i] - a[i]) * k) for i in range(3))

DIGITS = "0123456789"
def text_w(s, f, tab=False):
    if not tab: return f.getlength(s)
    dw = max(f.getlength(c) for c in DIGITS)
    return sum(dw if c in DIGITS else f.getlength(c) for c in s)

def draw_text(d, x, y, s, f, fill, tab=False, anchor="ls", track=0):
    """Texto con baseline en y. anchor 'ls' (izq), 'ms' (centro), 'rs' (dcha). tab=cifras tabulares."""
    w = text_w(s, f, tab) + track * max(0, len(s) - 1)
    x0 = x - (w / 2 if anchor == "ms" else w if anchor == "rs" else 0)
    if not tab and not track:
        d.text((x0, y), s, font=f, fill=fill, anchor="ls"); return w
    dw = max(f.getlength(c) for c in DIGITS)
    cx = x0
    for c in s:
        cw = dw if (tab and c in DIGITS) else f.getlength(c)
        off = (cw - f.getlength(c)) / 2 if (tab and c in DIGITS) else 0
        d.text((cx + off, y), c, font=f, fill=fill, anchor="ls")
        cx += cw + track
    return w

def cap_h(f): return -f.getbbox("H", anchor="ls")[1]

def fit(kind, s, maxw, start=400, weight="Bold", tab=False):
    size = start
    while size > 10 and text_w(s, F(kind, size, weight), tab) > maxw: size -= 4
    return size

def es_num(v, dec=0):
    """Formato español: 18.011 · 53,5"""
    s = f"{v:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

# ---------------------------------------------------------------- subtítulos
def wrap(s, f, maxw):
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if f.getlength(t) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def subtitle_layer(text, caja=None):
    f = F("d", 46, "Medium")
    lines = wrap(text, f, 1500)
    lh = 60
    y0 = 975 - (len(lines) - 1) * lh
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    for i, l in enumerate(lines):
        ds.text((W / 2, y0 + i * lh + 3), l, font=f, fill=(0, 0, 0, 150), anchor="ms")
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    dt = ImageDraw.Draw(sh)
    if caja:   # caja verde semitransparente detrás (para fondos claros)
        wmax = max(f.getlength(l) for l in lines)
        dt.rounded_rectangle([W / 2 - wmax / 2 - 30, y0 - lh + 8, W / 2 + wmax / 2 + 30, y0 + (len(lines) - 1) * lh + 24],
                             radius=16, fill=caja)
    for i, l in enumerate(lines):
        dt.text((W / 2, y0 + i * lh), l, font=f, fill=WHITE + (255,), anchor="ms")
    return sh

def alfa_sub(t, i, ts):
    """Opacidad del subtítulo i: fundido solo al entrar/salir de un bloque; entre frases seguidas, corte."""
    a0, b0 = ts[i]
    pg = a0 - ts[i - 1][1] if i else 9
    ng = ts[i + 1][0] - b0 if i + 1 < len(ts) else 9
    fi = seg(t, a0 - .05, a0 + .1) if pg > .3 else float(t >= a0)
    fo = (1 - seg(t, b0 - .1, b0 + .05)) if ng > .3 else float(t < b0)
    return fi * fo

def centrar(fn, D, muestras=(0.55, 0.8)):
    """Desplazamiento vertical para centrar en el cuadro lo que dibuja fn (sin subtítulos)."""
    top, bot = H, 0
    for f in muestras:
        im = fn(D * f, D).convert("RGB"); bg = im.getpixel((4, 4))
        bb = ImageChops.difference(im, Image.new("RGB", im.size, bg)).getbbox()
        if bb: top, bot = min(top, bb[1]), max(bot, bb[3])
    if bot <= top: return 0
    return int(max(-200, min(300, H / 2 - (top + bot) / 2)))

def desplaza(im, dy):
    if not dy: return im
    out = Image.new(im.mode, im.size, im.getpixel((4, 4))); out.paste(im, (0, dy)); return out

def fade_layer(layer, a):
    """Misma capa con la opacidad multiplicada por a (sin oscurecer los colores)."""
    l = layer.copy(); l.putalpha(layer.getchannel("A").point(lambda v: round(v * a))); return l

# ---------------------------------------------------------------- render
def render(name, dur, frame_fn, subs=None, audio=None):
    OUT.mkdir(exist_ok=True)
    path = OUT / name
    n = round(dur * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart", str(path)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    if isinstance(subs, str): subs = [(0.5, dur - 0.5, subs)]
    layers = [(a, b, subtitle_layer(txt, (0x2F, 0x3B, 0x26, 225))) for a, b, txt in (subs or [])]
    empty = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for i in range(n):
        t = i / FPS
        im = frame_fn(t, dur - 1 / FPS)   # el último frame completa la salida → igual al primero
        ts = [(a0, b0) for a0, b0, _ in layers]
        for j, (a0, b0, layer) in enumerate(layers):
            a = alfa_sub(t, j, ts)
            if a > 0:
                lay = layer if a >= 1 else fade_layer(layer, a)
                im = Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB")
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    if audio:
        tmp = path.with_suffix(".tmp.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-i", str(audio), "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-af", "apad", "-t", f"{n / FPS:.3f}", "-c:a", "aac", "-b:a", "128k",
                        "-movflags", "+faststart", str(tmp)], check=True)
        tmp.replace(path)
    print(f"{name}: {n} frames, {dur:.2f}s, {path.stat().st_size/1e6:.2f} MB")

def canvas(bg=None):
    im = Image.new("RGB", (W, H), bg or BG); return im, ImageDraw.Draw(im)

# ---------------------------------------------------------------- vídeos (16:9 · zona útil y < 820; debajo, subtítulos)
def s12(t, D):
    """Contador 0 → 53,5 M."""
    im, d = canvas()
    cy = 500
    fl = F("d", 52, "Medium"); fs = F("d", 32, "Regular")
    draw_text(d, W/2, cy + 130, "impactos acumulados", fl, INK, anchor="ms")
    draw_text(d, W/2, cy + 185, "Instagram y TikTok · abr 2025 – oct 2026", fs, mix(BG, INK, .6), anchor="ms")
    a = seg(t, 0, .25) * (1 - seg(t, D - .35, D))
    k = eo5(seg(t, .25, min(2.4, D - .9)))
    f = F("o", fit("o", "53,5 M", 1000, 380, tab=True))
    draw_text(d, W/2, cy, es_num(53.5 * k, 1) + " M", f, mix(BG, NUM, a), tab=True, anchor="ms")
    lw = 700 * k
    d.rectangle([W/2 - lw/2, cy + 40, W/2 + lw/2, cy + 48], fill=mix(BG, YELLOW, a))
    return im

def s13(t, D):
    """53,5 M · 18.011 · 7.823 subiendo uno tras otro, en tres columnas."""
    im, d = canvas()
    items = [("IMPACTOS", 53.5, 1, " M", "impactos acumulados"),
             ("INSTAGRAM", 18011, 0, "", "seguidores en Instagram"),
             ("TIKTOK", 7823, 0, "", "seguidores en TikTok")]
    xs = [W/2 - 600, W/2, W/2 + 600]
    for x in (W/2 - 300, W/2 + 300):
        d.line([(x, 300), (x, 640)], fill=mix(BG, INK, .18), width=2)
    out = 1 - seg(t, D - .5, D)
    fk = F("o", 40, "Medium"); fl = F("d", 36, "Regular")
    fn = F("o", fit("o", "18.011", 500, 200, tab=True))
    y0 = 520
    for i, (kick, val, dec, suf, lab) in enumerate(items):
        st = CUE.get("s13", [.2, 1.7, 3.2])[i]
        a = seg(t, st, st + .3) * out
        if a <= 0: continue
        k = eo5(seg(t, st, st + 1.4))
        y = y0 + 30 * (1 - eo(seg(t, st, st + .4)))
        draw_text(d, xs[i], y - cap_h(fn) - 34, kick, fk, mix(BG, KICK, a), anchor="ms", track=8)
        draw_text(d, xs[i], y, es_num(val * k, dec) + suf, fn, mix(BG, NUM if i == 0 else NUM2, a), tab=True, anchor="ms")
        draw_text(d, xs[i], y + 62, lab, fl, mix(BG, INK, a * .85), anchor="ms")
    return im

CIFRAS_14 = [("STREET", "[CIFRA]", "reproducciones"),
             ("RECETAS", "[CIFRA]", "reproducciones"),
             ("TIKTOK", "[CIFRA]", "reproducciones"),
             ("COLABORACIONES", "847K", "reproducciones"),
             ("PAID", "[CIFRA]", "impactos")]
def s14(t, D):
    """Ráfaga de rótulos de reproducciones de las mejores piezas (slides 6-10)."""
    im, d = canvas()
    n = len(CIFRAS_14)
    slot = (D - .3) / n
    fk = F("o", 60, "Medium"); fl = F("d", 44, "Regular")
    fn = F("o", fit("o", "[CIFRA]", 1100, 300))
    dots_y = 790
    for i in range(n):
        x = W/2 + (i - (n - 1)/2) * 46
        d.ellipse([x - 8, dots_y - 8, x + 8, dots_y + 8], fill=mix(BG, INK, .25))
    for i, (kick, num, lab) in enumerate(CIFRAS_14):
        st = .15 + i * slot
        tin, tout = seg(t, st, st + .2), seg(t, st + slot - .2, st + slot)
        if tin <= 0 or tout >= 1: continue
        a = eo(tin) * (1 - tout)
        dy = 160 * (1 - eo(tin)) - 150 * ei(tout)
        x = W/2 + (i - (n - 1)/2) * 46
        d.ellipse([x - 8, dots_y - 8, x + 8, dots_y + 8], fill=mix(mix(BG, INK, .25), YELLOW, a))
        y = 540 + dy
        draw_text(d, W/2, y - cap_h(fn) - 50, kick, fk, mix(BG, INK, a), anchor="ms", track=10)
        draw_text(d, W/2, y, num, fn, mix(BG, YELLOW, a), anchor="ms")
        draw_text(d, W/2, y + 80, lab, fl, mix(BG, INK, a * .9), anchor="ms")
    return im

def s15(t, D):
    """Barras horizontales 1,3 M/mes (2025) → 4,2 M/mes (2026)."""
    im, d = canvas()
    x0, maxw, bh = 360, 1120, 150
    rows = [300, 540]
    draw_text(d, W/2, 170, "IMPACTOS AL MES", F("o", 76, "Bold"), INK, anchor="ms", track=2)
    d.line([(x0, rows[0] - 40), (x0, rows[1] + bh + 40)], fill=mix(BG, INK, .5), width=3)
    fy = F("o", 60, "Medium")
    out = 1 - seg(t, D - .5, D)
    sa, sb = CUE.get("s15_a", .3), CUE.get("s15_b", 1.3)
    data = [("2025", 1.3, mix(BG, INK, .55), sa), ("2026", 4.2, YELLOW, sb)]
    fv = F("o", 84, "Bold"); fu = F("d", 32, "Regular")
    for (yr, v, col, st), y in zip(data, rows):
        draw_text(d, x0 - 40, y + bh/2 + cap_h(fy)/2, yr, fy, INK, anchor="rs")
        k = eio(seg(t, st, st + (0.8 if v < 2 else 1.3)))
        w = maxw * v / 4.2 * k * out
        if w > 3:
            d.rectangle([x0 + 2, y, x0 + w, y + bh], fill=col)
        a = seg(t, st + .15, st + .45) * out
        if a > 0:
            xv = x0 + w + 30
            draw_text(d, xv, y + bh/2 + 18, es_num(v * k, 1) + " M", fv, mix(BG, INK, a), tab=True)
            draw_text(d, xv, y + bh/2 + 62, "al mes", fu, mix(BG, INK, a * .8))
    # ×3 (cifra de la propia slide: 4,2 M frente a 1,3 M)
    pa = eo(seg(t, sb + 1.45, sb + 1.8)) * out
    if pa > 0:
        cx, cy, r = x0 + maxw + 320, rows[1] + bh/2, 62 * (0.6 + .4 * pa)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=mix(BG, YELLOW, pa))
        draw_text(d, cx, cy + 22, "×3", F("o", 62 * (0.6 + .4 * pa)), mix(YELLOW, GREEN, pa), anchor="ms")
    return im

def s16(t, D):
    """«Y EN 2027, ¿QUÉ PASA?» escribiéndose sobre negro."""
    im, d = canvas(BLACK)
    lines = ["Y EN 2027,", "¿QUÉ PASA?"]
    f = F("o", fit("o", "¿QUÉ PASA?", 1000, 210))
    lh = 230
    ys = [400, 400 + lh]
    total = sum(len(l) for l in lines)
    t0, t1 = CUE.get("s16_start", .2), CUE.get("s16_end", min(1.7, D - 1.0))
    shown = int(total * seg(t, t0, t1) + 1e-6)
    out = 1 - seg(t, D - .35, D)
    x0 = W/2 - text_w("¿QUÉ PASA?", f)/2
    cur = (x0, ys[0]); left = shown
    for l, y in zip(lines, ys):
        part = l[:max(0, min(len(l), left))]
        x = x0
        for c in part:
            col = YELLOW if l.startswith("Y EN") and c.isdigit() else INK
            d.text((x, y), c, font=f, fill=mix(BLACK, col, out), anchor="ls"); x += f.getlength(c)
        if left > 0 or l is lines[0]: cur = (x, y)
        left -= len(l)
        if left <= 0: break
    blink = 1 if (t < t1 + .05) else (1 if int((t - t1) * 3) % 2 == 0 else 0)
    ca = seg(t, 0, .12) * out * blink
    if ca > 0:
        ch = cap_h(f)
        d.rectangle([cur[0] + 12, cur[1] - ch, cur[0] + 26, cur[1] + 8], fill=mix(BLACK, YELLOW, ca))
    return im

def s17(t, D):
    """Transición tipográfica NOTORIEDAD → COMUNIDAD (rodillo letra a letra)."""
    im, d = canvas()
    A, B = "NOTORIEDAD", "COMUNIDAD"
    f = F("o", fit("o", A, 1300, 300))
    ch = cap_h(f)
    by = 560
    win = (by - ch - 30, by + 30)
    fin = seg(t, 0, .25); fout = 1 - seg(t, D - .3, D)
    tA = CUE.get("s17", .85)
    band = Image.new("RGB", (W, win[1] - win[0]), BG)
    bd = ImageDraw.Draw(band)
    hgt = win[1] - win[0]
    for word, col, entering in ((A, INK, False), (B, YELLOW, True)):
        x = W/2 - text_w(word, f)/2
        for i, c in enumerate(word):
            k = eio(seg(t, tA + i * .04, tA + i * .04 + .42))
            if entering:
                dy = hgt * (1 - k); alpha = 1 if k > 0 else 0
            else:
                dy = -hgt * k; alpha = fin if k < 1 else 0
            alpha *= fout
            if alpha > 0:
                bd.text((x, by - win[0] + dy), c, font=f, fill=mix(BG, col, alpha), anchor="ls")
            x += f.getlength(c)
    im.paste(band, (0, win[0]))
    fk = F("o", 50, "Medium")
    a1 = fin * (1 - seg(t, tA + .05, tA + .25)); a2 = seg(t, tA + .3, tA + .55) * fout
    if a1 > 0: draw_text(d, W/2, win[0] - 40, "2025 – 2026", fk, mix(BG, INK, a1 * .8), anchor="ms", track=6)
    if a2 > 0: draw_text(d, W/2, win[0] - 40, "2027", fk, mix(BG, KICK, a2), anchor="ms", track=6)
    k = eio(seg(t, tA + .05, tA + .85))
    lw = 420
    d.rectangle([W/2 - lw/2, by + 60, W/2 + lw/2, by + 66], fill=mix(BG, mix(INK, YELLOW, k), fin * fout))
    return im

SPLIT_24 = 0.5   # reparto visual provisional: sin porcentajes hasta que Juan los pase
def s24(t, D):
    """Barra que se divide en dos colores: awareness / interacción."""
    im, d = canvas()
    x0, x1, y, h = 260, 1660, 330, 170
    draw_text(d, W/2, 220, "PAID 2027", F("o", 60, "Medium"), mix(BG, INK, .8), anchor="ms", track=10)
    out = 1 - seg(t, D - .5, D)
    g = eio(seg(t, .2, 1.0))
    S = CUE.get("s24", 1.3)
    sp = eio(seg(t, S, S + .65))
    if g * out <= 0: return im
    gap = 50 * sp
    full = x0 + (x1 - x0) * g
    mid = x0 + (x1 - x0) * SPLIT_24
    base = mix(BG, INK, .55)
    cl = mix(BG, mix(base, YELLOW, sp), out)
    cr = mix(BG, mix(base, INK, sp), out)
    if sp <= 0:
        d.rounded_rectangle([x0, y, max(x0 + 2, full), y + h], radius=14, fill=cl)
    else:
        d.rounded_rectangle([x0, y, mid - gap/2, y + h], radius=14, fill=cl)
        d.rounded_rectangle([mid + gap/2, y, x1, y + h], radius=14, fill=cr)
    la = seg(t, S + .5, S + .9) * out
    if la > 0:
        fl = F("o", 64, "Bold"); fs = F("d", 36, "Regular")
        dy = 20 * (1 - eo(seg(t, S + .5, S + .9)))
        draw_text(d, x0, y + h + 95 + dy, "AWARENESS", fl, mix(BG, INK, la), track=3)
        draw_text(d, x1, y + h + 95 + dy, "INTERACCIÓN", fl, mix(BG, INK, la), anchor="rs", track=3)
        draw_text(d, x0, y + h + 150 + dy, "notoriedad", fs, mix(BG, INK, la * .75))
        draw_text(d, x1, y + h + 150 + dy, "comunidad", fs, mix(BG, INK, la * .75), anchor="rs")
    return im

VIDEOS = {
    "s12": ("s12_v01_contador_53M.mp4", 3.5, s12),
    "s13": ("s13_v01_contadores.mp4", 7.0, s13),
    "s14": ("s14_v01_rafaga_cifras.mp4", 5.0, s14),
    "s15": ("s15_v01_barra_impactos.mp4", 5.5, s15),
    "s16": ("s16_v01_pregunta.mp4", 3.0, s16),
    "s17": ("s17_v01_notoriedad_comunidad.mp4", 3.0, s17),
    "s24": ("s24_v01_dos_bolsas.mp4", 4.5, s24),
}

if __name__ == "__main__":
    args = sys.argv[1:]
    mudo = "--mudo" in args   # sin locución ni subtítulos
    durs = {}
    if "--dur" in args:
        for kv in args[args.index("--dur") + 1].split(","):
            k, v = kv.split("="); durs[k] = float(v)
    keys = [a for a in args if a in VIDEOS] or list(VIDEOS)
    for k in keys:
        name, dur, fn = VIDEOS[k]
        CUE.clear()
        tema("verde" if k in ("s12", "s14", "s16", "s17") else "crema")
        D0 = max(dur, TIEMPOS[k]["duracion"]) if (not mudo and k in TIEMPOS) else dur
        if CUE is not None and not mudo and k in TIEMPOS: CUE.update(cues(k))
        dy = centrar(fn, D0 - 1 / FPS)
        fn = (lambda f, dy: (lambda t, D: desplaza(f(t, D), dy)))(fn, dy)
        if not mudo and k in TIEMPOS:
            CUE.update(cues(k))
            D = durs.get(k, max(dur, TIEMPOS[k]["duracion"]))
            render(name, D, fn, subtitulos(k) if "--subtitulos" in args else None, AUDIO / TIEMPOS[k]["archivo"])
        else:
            render(name, durs.get(k, dur), fn)
