"""Mockup largo de la web Amazonia Club · Friends First (18/11), a partir del mock de Juan. Devuelve una imagen
de ancho SC_W (pantalla del teléfono) y alto variable, para hacer scroll en la palanca 5."""
from pathlib import Path
from PIL import Image, ImageDraw
import fase1 as A
from fase1 import F, GREEN, CREAM, draw_text, cap_h, text_w, mix

ROOT = Path(__file__).resolve().parent.parent
WHITE = (255, 255, 255)
QUEDADAS = [("RUN CLUB", "Barceloneta · sábado 8:00", "running"),
            ("YOGA AL AMANECER", "Bogatell · domingo 9:00", "yoga"),
            ("ENTRENO FUNCIONAL", "Ciutadella · miércoles 19:30", "funcional")]

def _parte(texto, f, ancho):
    out, cur = [], ""
    for w in texto.split():
        p = (cur + " " + w).strip()
        if text_w(p, f) > ancho and cur: out.append(cur); cur = w
        else: cur = p
    return out + ([cur] if cur else [])

def web(sw):
    S = 2; w = sw * S
    ref = Image.open(ROOT / "material/s19_palancas/club_mock_ref.png").convert("RGB")
    foto = ref.crop((48, 56, 350, 384)); foto = foto.resize((w, round(foto.height * w / foto.width)), Image.LANCZOS)
    th1 = ref.crop((90, 616, 216, 682)); th2 = ref.crop((234, 616, 344, 682))
    secs = []
    # 0) barra superior
    top = Image.new("RGB", (w, 110), CREAM); d = ImageDraw.Draw(top)
    draw_text(d, 36, 72, "AMAZONIA CLUB", F("o", 44, "Bold"), GREEN, track=3)
    for i in range(3): d.rectangle([w - 80, 38 + i * 16, w - 36, 44 + i * 16], fill=GREEN)
    secs.append(top)
    # 1) foto + sello club
    f1 = foto.copy(); d = ImageDraw.Draw(f1)
    bx, by = 36, f1.height - 120
    d.ellipse([bx, by, bx + 190, by + 96], fill=CREAM, outline=GREEN, width=4)
    draw_text(d, bx + 95, by + 64, "club", F("d", 46, "Bold"), GREEN, anchor="ms")
    secs.append(f1)
    # 2) bloque verde: titular + texto + botón
    g = Image.new("RGB", (w, 900), GREEN); d = ImageDraw.Draw(g)
    ft = F("o", 92, "Bold")
    draw_text(d, w / 2, 70 + cap_h(ft), "AMAZONIA CLUB", ft, CREAM, anchor="ms", track=2)
    draw_text(d, w / 2, 70 + 2 * cap_h(ft) + 18, "FRIENDS FIRST", ft, CREAM, anchor="ms", track=2)
    fx = F("d", 30, "Medium"); y = 70 + 2 * cap_h(ft) + 80
    for l in _parte("Un espacio propio donde la comunidad tiene prioridad: lanzamientos, ediciones limitadas y acceso a eventos.", fx, w - 120):
        draw_text(d, w / 2, y, l, fx, CREAM, anchor="ms"); y += 42
    fb = F("d", 32, "Bold"); bw = text_w("ÚNETE AL CLUB", fb)
    draw_text(d, w / 2, y + 50, "ÚNETE AL CLUB", fb, CREAM, anchor="ms")
    d.rectangle([w / 2 - bw / 2, y + 60, w / 2 + bw / 2, y + 63], fill=CREAM)
    secs.append(g.crop((0, 0, w, y + 110)))
    # 3) fotos pequeñas
    ph = Image.new("RGB", (w, 260), GREEN)
    for i, t in enumerate((th1, th2)):
        tw_ = (w - 3 * 30) // 2; t = t.resize((tw_, 220), Image.LANCZOS)
        m = Image.new("L", t.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, t.width - 1, t.height - 1], 28, fill=255)
        ph.paste(t, (30 + i * (tw_ + 30), 10), m)
    secs.append(ph)
    # 4) próximas quedadas
    q = Image.new("RGB", (w, 160 + len(QUEDADAS) * 190), CREAM); d = ImageDraw.Draw(q)
    draw_text(d, 36, 60 + cap_h(F("o", 56, "Bold")), "PRÓXIMAS QUEDADAS", F("o", 56, "Bold"), GREEN, track=2)
    for i, (tit, sub, _) in enumerate(QUEDADAS):
        y = 150 + i * 190
        d.rounded_rectangle([30, y, w - 30, y + 160], 26, fill=WHITE)
        draw_text(d, 64, y + 64, tit, F("o", 42, "Bold"), GREEN, track=2)
        draw_text(d, 64, y + 110, sub, F("d", 26, "Medium"), mix(WHITE, GREEN, .7))
        bw = 170; d.rounded_rectangle([w - 64 - bw, y + 52, w - 64, y + 108], 28, fill=GREEN)
        draw_text(d, w - 64 - bw / 2, y + 90, "APÚNTATE", F("d", 24, "Bold"), CREAM, anchor="ms")
    secs.append(q)
    # 5) drops
    dr = Image.new("RGB", (w, 330), GREEN); d = ImageDraw.Draw(dr)
    draw_text(d, 36, 60 + cap_h(F("o", 56, "Bold")), "DROPS PARA MIEMBROS", F("o", 56, "Bold"), CREAM, track=2)
    y = 150
    for l in _parte("Lanzamientos y ediciones limitadas antes que nadie. Solo para quien está dentro.", F("d", 30, "Medium"), w - 80):
        draw_text(d, 36, y, l, F("d", 30, "Medium"), CREAM); y += 42
    secs.append(dr)
    alto = sum(s.height for s in secs)
    out = Image.new("RGB", (w, alto), CREAM); y = 0
    pos = {}
    for i, s in enumerate(secs): out.paste(s, (0, y)); pos[i] = y; y += s.height
    out = out.resize((sw, alto // S), Image.LANCZOS)
    # posición del primer botón «APÚNTATE» (para el toque), en px de pantalla
    boton = ((w - 64 - 85) / S, (pos[4] + 150 + 80) / S)
    return out, boton, pos[4] / S

if __name__ == "__main__":
    im, b, yq = web(368)
    print(im.size, b, yq); im.save(ROOT / "borrador/corto/_rev/club_web.png")
