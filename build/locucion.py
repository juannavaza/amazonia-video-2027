"""Corta la locución completa en una pista por vídeo, normaliza a -16 LUFS y añade 0,5 s de silencio.

Uso: .venv/bin/python -I build/locucion.py <voz>     (p. ej. juaniyo, alba)
Entrada: audio/originales/locucion_completa_<voz>.mp3 + audio/originales/palabras_<voz>.json (faster-whisper)
Salida:  audio/sNN_v01_<nombre>.mp3  y  audio/tiempos.json (duración + inicio de cada frase, en segundos del MP3 final)
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOZ = sys.argv[1] if len(sys.argv) > 1 else "alba"
SRC = ROOT / f"audio/originales/locucion_completa_{VOZ}.mp3"
PALABRAS = f"audio/originales/palabras_{VOZ}.json"
WORDS = json.load(open(ROOT / PALABRAS))
PAD = 0.5

# (slide, nombre de vídeo, palabra ancla, desplazamiento desde el ancla hasta la 1.ª palabra)
SLIDES = [
    ("s02", "s02_v01_grid_2024", "inicios", -1),
    ("s03", "s03_v01_transicion_grid", "Desde", 0),
    ("s04", "s04_v01_montaje_palancas", "Identidad", 0),
    ("s05", "s05_v01_grid_antes_despues", "Primero", 0),
    ("s06", "s06_v01_street", "Salimos", 0),
    ("s07", "s07_v01_receta", "Recetas", 0),
    ("s08", "s08_v01_tiktok", "Abrimos", 0),
    ("s09", "s09_v01_colab", "Elegimos", 0),
    ("s10", "s10_v01_paid", "Pautamos", 0),
    ("s11", "s11_v01_sorteo", "activamos", -1),
    ("s12", "s12_v01_contador_53M", "resultados", -2),
    ("s13", "s13_v01_contadores", "53", 0),
    ("s14", "s14_v01_rafaga_cifras", "encargo", -1),
    ("s15", "s15_v01_barra_impactos", "1", -1),
    ("s16", "s16_v01_pregunta", "¿qué", -3),
    ("s17", "s17_v01_notoriedad_comunidad", "pasamos", -2),
    ("s18", "s18_v01_comentarios_dm", "Esa", 0),
    ("s19", "s19_v01_montaje_5_palancas", "palancas", -1),
    ("s20", "s20_v01_antes_despues_caras", "Mismos", 0),
    ("s21", "s21_v01_host", "Una", 0),
    ("s22", "s22_v01_timeline_embajadores", "mismos", -1),
    ("s23", "s23_v01_votacion", "decide", -2),
    ("s24", "s24_v01_dos_bolsas", "Notoriedad", 0),
    ("s25", "s25_v01_run_club", "sampling", -1),
    ("s26", "s26_v01_web_club", "Club", -1),
    ("s27", "s27_v01_montaje_referencias", "Marcas", 0),
    ("s29", "s29_v01_genz", "generación", -1),
    ("s30", "s30_v01_loop_cierre", None, None),   # últimas palabras: «En 2027, Amazonia es otra historia.»
]

def clean(w): return re.sub(r"[^\wáéíóúñü¿?]", "", w.lower())

def silences(noise="-35dB", d=0.12):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(SRC), "-af",
                          f"silencedetect=noise={noise}:d={d}", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return list(zip(st, en))

def lufs(f, objetivo=-16.0):
    """Segunda pasada: si la pista queda a más de 0,3 LU del objetivo, ganancia + limitador a -1,5 dBTP."""
    med = lambda: float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f),
                        "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
    g = objetivo - med()
    if abs(g) > 0.3:
        tmp = f.with_suffix(".tmp.mp3")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-af", f"volume={g:.2f}dB,alimiter=limit=0.84:level=false,asetpts=N/SR/TB",
                        "-c:a", "libmp3lame", "-b:a", "192k", str(tmp)], check=True)
        tmp.replace(f)

def main():
    # índice de la 1.ª palabra de cada slide (búsqueda secuencial)
    starts, pos = [], 0
    for sl, name, anchor, off in SLIDES:
        if anchor is None:
            i = len(WORDS) - 6
        else:
            i = next(k for k in range(pos, len(WORDS)) if clean(WORDS[k]["w"]) == clean(anchor)) + off
        starts.append(i); pos = i + 1
    sil = silences()
    total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(SRC)],
                                 capture_output=True, text=True).stdout)
    # fronteras: el silencio más largo entre la última palabra de una slide y la 1.ª de la siguiente
    bounds = []
    for k in range(1, len(starts)):
        a, b = WORDS[starts[k] - 1]["s"], WORDS[starts[k]]["e"]
        cand = [(e - s, s, e) for s, e in sil if s < b and e > a]
        if cand:
            _, s, e = max(cand); bounds.append((s, e))
        else:
            m = (WORDS[starts[k] - 1]["e"] + WORDS[starts[k]]["s"]) / 2; bounds.append((m, m))
    lead = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
    tail = sil[-1][0] if sil and sil[-1][1] > total - 0.05 else total
    tiempos = {}
    (ROOT / "audio").mkdir(exist_ok=True)
    for k, (sl, name, _, _) in enumerate(SLIDES):
        t0 = (bounds[k - 1][1] - 0.04) if k else max(0, lead - 0.04)
        t1 = (bounds[k][0] + 0.06) if k < len(bounds) else min(total, tail + 0.06)
        wend = starts[k + 1] if k + 1 < len(starts) else len(WORDS)
        ws = WORDS[starts[k]:wend]
        # frases (por puntuación final del reconocimiento) → inicio relativo al MP3 final
        frases, cur = [], None
        for w in ws:
            if cur is None: cur = max(w["s"], t0)
            if re.search(r"[.?!]$", w["w"]):
                frases.append(round(cur - t0 + PAD, 3)); cur = None
        if cur is not None: frases.append(round(cur - t0 + PAD, 3))
        out = ROOT / "audio" / f"{name}.mp3"
        flt = f"atrim={t0:.3f}:{t1:.3f},asetpts=PTS-STARTPTS,"
        meas = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(SRC), "-af",
                               flt + "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                              capture_output=True, text=True).stderr
        j = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
        ln = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
              f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-af",
                        flt + ln + f",aresample=44100,adelay={int(PAD*1000)}:all=1,apad=pad_dur={PAD},asetpts=N/SR/TB",
                        "-ac", "1", "-c:a", "libmp3lame", "-b:a", "192k", str(out)], check=True)
        lufs(out)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                                   capture_output=True, text=True).stdout)
        tiempos[sl] = {"archivo": out.name, "duracion": round(dur, 3), "voz": round(t1 - t0, 3), "frases": frases,
                       "texto_oido": " ".join(w["w"] for w in ws), "origen": [round(t0, 2), round(t1, 2)]}
        print(f"{sl}  {dur:5.2f}s  [{t0:6.2f}–{t1:6.2f}]  {tiempos[sl]['texto_oido']}")
    tiempos["_meta"] = {"voz": VOZ, "palabras": PALABRAS}
    json.dump(tiempos, open(ROOT / "audio/tiempos.json", "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
