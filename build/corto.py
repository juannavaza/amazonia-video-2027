"""Versión corta (presentación) · Amazonia 2027 · escenas 1 a 5.
1 Gancho (iPhone grid 2025 → actual, sin voz) · 2 S02 · 3 Ráfaga de las 6 palancas con la voz de S04 · 4 S13 · 5 S14 + S17 + S18.
Usa los tramos ya renderizados (borrador/tramos_alba) y tapa la etiqueta «SNN · …» de arriba a la izquierda.
Salida: borrador/corto/amazonia_2027_corto_v1_hasta_e5.mp4
Uso: python3 -I build/corto.py [--frames]
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
B = ROOT / "borrador"; TR = B / "tramos_alba_sin_etiqueta"; TR_ORIG = B / "tramos_alba"; OUT = B / "corto"; TMP = OUT / "_tmp"
OUT.mkdir(exist_ok=True); TMP.mkdir(exist_ok=True)
W, H, FPS = 1920, 1080, 25
VENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS)]
AENC = ["-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "1"]
MUSICA = ROOT / "audio/musica/same_kind_of_paradise_borrador.wav"; MUSICA_DB = 8.0
CREAM, GREEN, INK, YELLOW = (0xF3, 0xEA, 0xDF), (0x2F, 0x3B, 0x26), (0x2F, 0x3B, 0x26), (0xF0, 0xB4, 0x3A)
FINAL = OUT / "amazonia_2027_corto_v1_hasta_e5.mp4"

def run(c): subprocess.run(c, check=True)
def dur(f): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                        capture_output=True, text=True).stdout)
def fondo(f, t=1.0):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(f), "-frames:v", "1", "-vf", "crop=4:4:520:20",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return "0x%02X%02X%02X" % tuple(raw[:3])
def tapa(f):   # caja del color de fondo sobre la etiqueta de revisión
    return "null"   # los tramos ya vienen sin etiqueta (render con ETIQUETA=False)

def tramo_limpio(k):
    src, dst = TR / f"{k}.mp4", TMP / f"{k}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", tapa(src), *VENC, *AENC, str(dst)]); return dst

# ---------------------------------------------------------------- 1 · gancho
def gancho(D=4.0):
    sys.path.insert(0, str(ROOT / "build")); import s05_iphone as P
    P.SRC = P.decodifica()
    n = round(D * FPS); n_a, n_f = round(1.7 * FPS), round(.45 * FPS); n_d = n - n_a - n_f
    fr = [P.antes(i / (n_a - 1)) for i in range(n_a)]
    d = [P.despues_t(3.0 * i / max(1, n_d - 1)) for i in range(n_d)]
    fr += P.fundido(P.antes(1), d[0], n_f) + d
    escala = 1000 / P.CH; pw, ph = round(P.CW * escala) // 2 * 2, round(P.CH * escala) // 2 * 2
    dst = TMP / "e1_gancho.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-f", "lavfi", "-t", f"{D}", "-i", "anullsrc=r=44100:cl=mono",
                          "-vf", "fade=t=in:d=0.3,fade=t=out:st=%.2f:d=0.15" % (D - .15), *VENC, *AENC, "-shortest", str(dst)],
                         stdin=subprocess.PIPE)
    for i, sc in enumerate(fr):
        bg = Image.new("RGB", (W, H), CREAM)
        tel = P.compone(sc).resize((pw, ph), Image.LANCZOS)
        k = min(1, i / (.6 * FPS)); y = round((H - ph) / 2 + 30 * (1 - k * k * (3 - 2 * k)))
        bg.paste(tel, ((W - pw) // 2, y), tel); p.stdin.write(bg.tobytes())
    p.stdin.close(); p.wait(); return dst

# ---------------------------------------------------------------- 3 · ráfaga de palancas con la voz de S04
PAL = json.load(open(ROOT / "audio/originales/palabras_alba.json")); PAL = PAL if isinstance(PAL, list) else PAL.get("palabras", PAL)
def t_s04(w):
    a, b = 11.13, 19.76
    for x in PAL:
        if a - .05 <= x["s"] < b and x["w"].lower().strip(".,").startswith(w): return x["s"] - a + .5
CORTES = [("s05", 5.4, None), ("s06", 2.6, "drawbox=x=480:y=830:w=1400:h=140:color=0xF3EADF:t=fill"),   # tapa contadores PROVISIONALES
          ("s08", 6.2, None), ("s09", 9.0, None), ("s10", 12.6, None), ("s11", 16.4, None)]
def rafaga():
    D = dur(TR_ORIG / "s04.mp4")
    marcas = [0, t_s04("contenido"), t_s04("tiktok"), t_s04("influencers"), t_s04("paid"), t_s04("comunidad"), t_s04("seis")]
    trozos = []
    for i, (k, ini, extra) in enumerate(CORTES):
        d = marcas[i + 1] - marcas[i]; f = TR / f"{k}.mp4"; dst = TMP / f"e3_{i}_{k}.mp4"
        vf = tapa(f) + ("," + extra if extra else "")
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(ini), "-t", f"{d:.3f}", "-i", str(f), "-an", "-vf", vf, *VENC, str(dst)])
        trozos.append(dst)
    # cierre «6 palancas»: mosaico 3×2 con un fotograma de cada palanca
    cierre = TMP / "e3_cierre.png"; im = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(im)
    tw, th = 520, 292; gx, gy = (W - 3 * tw - 2 * 30) // 2, 300
    for i, (k, ini, extra) in enumerate(CORTES):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ini + .6), "-i", str(TR / f"{k}.mp4"), "-frames:v", "1", "-vf",
                              tapa(TR / f"{k}.mp4") + ("," + extra if extra else "") + f",scale={tw}:{th}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True).stdout
        x, y = gx + (i % 3) * (tw + 30), gy + (i // 3) * (th + 30)
        d.rounded_rectangle([x - 3, y - 3, x + tw + 2, y + th + 2], 14, outline=INK, width=3)
        im.paste(Image.frombytes("RGB", (tw, th), raw), (x, y))
    f = ImageFont.truetype(str(ROOT / "fonts/Oswald.ttf"), 120); f.set_variation_by_name("Bold")
    txt = "6 PALANCAS"; bw = d.textlength(txt, font=f); d.text(((W - bw) / 2, 110), txt, font=f, fill=INK)
    d.line([(W - bw) / 2, 255, (W + bw) / 2, 255], fill=YELLOW, width=8)
    im.save(cierre)
    dc = D - marcas[-1]; dst = TMP / "e3_6_cierre.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", str(cierre), "-t", f"{dc:.3f}",
         "-vf", "zoompan=z='1+0.03*on/%d':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=%dx%d:fps=%d,fade=t=out:st=%.2f:d=0.15"
         % (round(dc * FPS), W, H, FPS, dc - .15), *VENC, str(dst)])
    trozos.append(dst)
    lst = TMP / "e3.txt"; lst.write_text("".join(f"file '{t.name}'\n" for t in trozos))
    vid = TMP / "e3_v.mp4"; run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(vid)])
    dst = TMP / "e3_rafaga.mp4"   # voz de S04 (pista del tramo original, ya con su silencio inicial)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(TR_ORIG / "s04.mp4"), "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", *AENC, "-af", "apad", "-t", f"{dur(vid):.3f}", str(dst)])
    return dst

# ---------------------------------------------------------------- unión + música
def unir(partes):
    lst = TMP / "lista.txt"; lst.write_text("".join(f"file '{p.name}'\n" for p in partes))
    voz = TMP / "_voz.mp4"; run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(voz)])
    D = dur(voz)
    flt = (f"[1:a]atrim=0:{D:.3f},afade=t=in:d=1,afade=t=out:st={D - 2.5:.3f}:d=2.5,volume={MUSICA_DB}dB[m];"
           f"[0:a]aformat=channel_layouts=stereo[v];[v][m]amix=inputs=2:normalize=0:duration=first[a]")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(voz), "-i", str(MUSICA), "-filter_complex", flt, "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", str(FINAL)])
    print(f"{FINAL.relative_to(ROOT)} · {dur(FINAL):.1f} s")

if __name__ == "__main__":
    if "--solo-e3" in sys.argv:
        partes = [TMP / "e1_gancho.mp4", tramo_limpio("s02"), rafaga()] + [tramo_limpio(k) for k in ("s13", "s14", "s17", "s18")]
        unir(partes); sys.exit()
    partes = [gancho(), tramo_limpio("s02"), rafaga(), tramo_limpio("s13"), tramo_limpio("s14"), tramo_limpio("s17"), tramo_limpio("s18")]
    unir(partes)
