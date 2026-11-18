"""S05 · Solo el iPhone con el scroll del grid, como vídeos independientes (antes / después / seguidos).
Salida en borrador/recursos/: MP4 sobre crema #F3EADF y MOV ProRes 4444 con canal alfa. Sin audio. 30 fps. Loop limpio.
Uso: .venv/bin/python -I build/s05_iphone.py [antes] [despues] [seguidos] [--frames]
"""
import subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "borrador/recursos"; OUT.mkdir(parents=True, exist_ok=True)
GRID_ANT = ROOT / "borrador/entradas/grid_antiguo_v2.png"
VID = ROOT / "material/s05_grid_antes_despues/grid_actual.mov"
FPS, CREAM, MARGEN = 30, (0xF3, 0xEA, 0xDF), 40
S = 1.35                                              # escala respecto al teléfono del borrador (400×800)
PH_W, PH_H, PH_R, PH_B = round(400 * S), round(800 * S), round(64 * S), round(16 * S)
SC_W, SC_H = PH_W - 2 * PH_B, PH_H - 2 * PH_B
PAD = round(60 * S)

def eio(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)

def telefono():
    """Mismo diseño que el borrador (cuerpo, marco, botones, sombra), dibujado a escala S."""
    c = Image.new("RGBA", (PH_W + 2 * PAD, PH_H + 2 * PAD), (0, 0, 0, 0))
    sh = Image.new("L", c.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle([PAD + 10 * S, PAD + 30 * S, PAD + PH_W - 10 * S, PAD + PH_H + 10 * S], PH_R, fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(28 * S))
    c = Image.new("RGBA", c.size, (40, 46, 32, 0)); c.putalpha(sh)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([PAD, PAD, PAD + PH_W - 1, PAD + PH_H - 1], PH_R, fill=(28, 30, 26, 255))
    d.rounded_rectangle([PAD + 2, PAD + 2, PAD + PH_W - 3, PAD + PH_H - 3], PH_R - 2, outline=(70, 74, 64, 255), width=round(2 * S))
    for y0, y1 in ((150, 210), (240, 330)):
        d.rounded_rectangle([PAD - 4 * S, PAD + y0 * S, PAD + 1, PAD + y1 * S], 2, fill=(28, 30, 26, 255))
    d.rounded_rectangle([PAD + PH_W - 1, PAD + 200 * S, PAD + PH_W + 4 * S, PAD + 300 * S], 2, fill=(28, 30, 26, 255))
    mask = Image.new("L", (SC_W, SC_H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, SC_W - 1, SC_H - 1], PH_R - PH_B, fill=255)
    return c, mask

CUERPO, MASK = telefono()
# recorte del lienzo: caja de todo lo visible (sombra incluida) + 40 px; dimensiones pares
bx0, by0, bx1, by1 = CUERPO.getchannel("A").point(lambda v: 255 if v > 1 else 0).getbbox()
CX0, CY0 = max(0, bx0 - MARGEN), max(0, by0 - MARGEN)
CX1, CY1 = bx1 + MARGEN, by1 + MARGEN
CW, CH = (CX1 - CX0) // 2 * 2, (CY1 - CY0) // 2 * 2
LIENZO_W, LIENZO_H = max(CX1, CUERPO.width + MARGEN), max(CY1, CUERPO.height + MARGEN)

def compone(pantalla):
    tel = CUERPO.copy()
    tel.paste(pantalla, (PAD + PH_B, PAD + PH_B), MASK)
    ImageDraw.Draw(tel).rounded_rectangle([PAD + PH_W / 2 - 52 * S, PAD + PH_B + 14 * S, PAD + PH_W / 2 + 52 * S, PAD + PH_B + 44 * S],
                                          round(15 * S), fill=(12, 12, 12, 255))
    lz = Image.new("RGBA", (LIENZO_W, LIENZO_H), (0, 0, 0, 0)); lz.paste(tel, (0, 0))
    return lz.crop((CX0, CY0, CX0 + CW, CY0 + CH))

# ---- pantalla ANTES: grid antiguo, scroll abajo y vuelta arriba (ping-pong con pausas)
g = Image.open(GRID_ANT).convert("RGB"); G = g.resize((SC_W, round(g.height * SC_W / g.width)), Image.LANCZOS)
RANGO = G.height - SC_H
def antes(k):            # k: 0 = arriba, 1 = abajo
    off = round(RANGO * eio(k)); return G.crop((0, off, SC_W, off + SC_H))
T_PAUSA, T_BAJA, T_SUBE = .7, 3.2, 2.6
def seq_antes():
    fr = [antes(0)] * round(T_PAUSA * FPS)
    fr += [antes(i / (T_BAJA * FPS)) for i in range(round(T_BAJA * FPS))]
    fr += [antes(1)] * round(T_PAUSA * FPS)
    fr += [antes(1 - i / (T_SUBE * FPS)) for i in range(round(T_SUBE * FPS))]
    return fr

# ---- pantalla DESPUÉS: grabación del grid actual, decodificada una vez a tamaño de pantalla
TMP = Path(tempfile.mkdtemp(prefix="s05ip_"))
def decodifica():
    vf = f"scale={SC_W}:{SC_H}:force_original_aspect_ratio=increase:flags=lanczos,crop={SC_W}:{SC_H}"
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(VID), "-vf", vf, "-an", "-q:v", "2", str(TMP / "%05d.jpg")], check=True)
    return sorted(TMP.glob("*.jpg"))
SRC = None
def despues_t(ts):       # ts: segundo de la grabación original (60 fps)
    i = min(len(SRC) - 1, max(0, round(ts * 60))); return Image.open(SRC[i]).convert("RGB")
DUR_SRC = 12.0
V_IDA, V_VUELTA = 1.5, 2.4   # velocidad de la ida (scroll hacia abajo) y de la vuelta (rebobinado hacia arriba)
def seq_despues(con_vuelta=True):
    n_ida = round(DUR_SRC / V_IDA * FPS)
    fr = [despues_t(0)] * round(.5 * FPS)
    fr += [despues_t(DUR_SRC * eio(i / n_ida) if False else DUR_SRC * i / n_ida) for i in range(n_ida)]
    fr += [despues_t(DUR_SRC)] * round(.5 * FPS)
    if con_vuelta:
        n_v = round(DUR_SRC / V_VUELTA * FPS)
        fr += [despues_t(DUR_SRC * (1 - eio(i / n_v))) for i in range(n_v)]
    return fr

def fundido(a, b, n):
    return [Image.blend(a, b, eio((i + 1) / (n + 1))) for i in range(n)]

def seq_seguidos():
    # antes: pausa y baja · fundido al grid actual · grid actual baja · fundido de vuelta al antes arriba (= primer frame)
    fr = [antes(0)] * round(T_PAUSA * FPS)
    fr += [antes(i / (T_BAJA * FPS)) for i in range(round(T_BAJA * FPS))] + [antes(1)] * round(.4 * FPS)
    d = seq_despues(con_vuelta=False)
    fr += fundido(antes(1), d[0], round(.5 * FPS)) + d
    fr += fundido(d[-1], antes(0), round(.6 * FPS))
    return fr

def exporta(nombre, frames, solo_frame=False):
    first = compone(frames[0])
    bg = Image.new("RGBA", first.size, CREAM + (255,))
    Image.alpha_composite(bg, first).convert("RGB").save(OUT / f"{nombre}_frame0_crema.png")
    first.save(OUT / f"{nombre}_frame0_alfa.png")
    if solo_frame: return
    mp4_tmp, mov_tmp = OUT / f".{nombre}.tmp.mp4", OUT / f".{nombre}.tmp.mov"
    base = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-s", f"{CW}x{CH}", "-r", str(FPS)]
    p_mp4 = subprocess.Popen(base + ["-pix_fmt", "rgb24", "-i", "-", "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                                     "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mp4_tmp)], stdin=subprocess.PIPE)
    p_mov = subprocess.Popen(base + ["-pix_fmt", "rgba", "-i", "-", "-an", "-c:v", "prores_ks", "-profile:v", "4444",
                                     "-pix_fmt", "yuva444p10le", "-alpha_bits", "16", "-vendor", "apl0", str(mov_tmp)], stdin=subprocess.PIPE)
    for sc in frames:
        rgba = compone(sc)
        p_mov.stdin.write(rgba.tobytes())
        p_mp4.stdin.write(Image.alpha_composite(bg, rgba).convert("RGB").tobytes())
    for p in (p_mp4, p_mov):
        p.stdin.close()
        if p.wait() != 0: raise SystemExit(f"ffmpeg falló en {nombre}")
    mp4_tmp.rename(OUT / f"{nombre}.mp4"); mov_tmp.rename(OUT / f"{nombre}.mov")
    print(nombre, f"{len(frames) / FPS:.2f} s", f"{CW}x{CH}")

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")] or ["antes", "despues", "seguidos"]
    solo = "--frames" in sys.argv
    if any(a in args for a in ("despues", "seguidos")): SRC = decodifica()
    if "antes" in args: exporta("s05_iphone_antes", seq_antes(), solo)
    if "despues" in args: exporta("s05_iphone_despues", seq_despues(), solo)
    if "seguidos" in args: exporta("s05_iphone_antes_despues", seq_seguidos(), solo)
