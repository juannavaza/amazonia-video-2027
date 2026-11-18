"""Sustituye la locución de UNA sección por una regrabación suelta (p. ej. una frase nueva de ElevenLabs).

Uso: .venv/bin/python -I build/sustituir_frase.py <sNN> <archivo.mp3> [voz]
- Guarda el original en audio/originales/regrabaciones/ y la pista anterior en audio/originales/reemplazadas/.
- Transcribe con faster-whisper (tiempos por palabra), recorta el silencio, nivela a -16 LUFS (dos pasadas)
  y añade 0,5 s de silencio a cada lado, igual que build/locucion.py.
- Actualiza audio/tiempos.json: la sección pasa a llevar sus propias "palabras" (relativas al inicio de la voz).
"""
import json, re, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
PAD = 0.5

def lufs(f, objetivo=-16.0):
    """Segunda pasada (igual que build/locucion.py): ganancia + limitador si queda a más de 0,3 LU del objetivo."""
    med = lambda: float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f),
                        "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
    g = objetivo - med()
    if abs(g) > 0.3:
        tmp = f.with_suffix(".tmp.mp3")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-af", f"volume={g:.2f}dB,alimiter=limit=0.84:level=false,asetpts=N/SR/TB",
                        "-c:a", "libmp3lame", "-b:a", "192k", str(tmp)], check=True)
        tmp.replace(f)

def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                capture_output=True, text=True).stdout)

def transcribe(f):
    from faster_whisper import WhisperModel
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(np.frombuffer(raw, np.float32), language="es", word_timestamps=True, vad_filter=False)
    return [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for s in segs for w in s.words]

def limites_voz(f, total, umbral=-40.0, vent=0.02):
    """Primer y último instante con voz (RMS por ventanas de 20 ms por encima de umbral dBFS), con margen."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32); n = int(16000 * vent)
    r = np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + n] ** 2)) + 1e-9) for i in range(0, len(x) - n, n)])
    on = np.where(r > umbral)[0]
    return max(0.0, on[0] * vent - .04), min(total, (on[-1] + 1) * vent + .1)

def main():
    sl, src = sys.argv[1].lower(), Path(sys.argv[2]).expanduser()
    voz = sys.argv[3] if len(sys.argv) > 3 else "alba"
    audio_dir = ROOT / ("audio" if voz == "alba" else f"audio/{voz}")
    tj = audio_dir / "tiempos.json"; T = json.load(open(tj))
    nombre = T[sl]["archivo"] if sl in T else f"{sl}_v01.mp3"   # sección nueva sin locución previa
    out = audio_dir / nombre
    sello = time.strftime("%Y%m%d_%H%M%S")
    for sub in ("regrabaciones", "reemplazadas"): (ROOT / "audio/originales" / sub).mkdir(parents=True, exist_ok=True)
    orig = ROOT / "audio/originales/regrabaciones" / f"{sl}_{voz}_{sello}{src.suffix}"
    shutil.copy2(src, orig)
    if out.exists(): shutil.copy2(out, ROOT / "audio/originales/reemplazadas" / f"{out.stem}_{sello}{out.suffix}")
    ws = transcribe(orig)
    total = dur(orig)
    t0, t1 = limites_voz(orig, total)   # por energía real: Whisper suele dar el final de la última palabra antes de tiempo
    flt = f"atrim={t0:.3f}:{t1:.3f},asetpts=PTS-STARTPTS,"
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(orig), "-af",
                           flt + "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    j = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    ln = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(orig), "-af",
                    flt + ln + f",aresample=44100,adelay={int(PAD * 1000)}:all=1,apad=pad_dur={PAD},asetpts=N/SR/TB",
                    "-ac", "1", "-c:a", "libmp3lame", "-b:a", "192k", str(out)], check=True)
    lufs(out)
    frases, cur = [], None
    for w in ws:
        if cur is None: cur = w["s"]
        if re.search(r"[.?!]$", w["w"]): frases.append(round(cur - t0 + PAD, 3)); cur = None
    if cur is not None: frases.append(round(cur - t0 + PAD, 3))
    T[sl] = {"archivo": nombre, "duracion": round(dur(out), 3), "voz": round(t1 - t0, 3), "frases": frases,
             "texto_oido": " ".join(w["w"] for w in ws), "origen": [0, 0],
             "palabras": [{"w": w["w"], "s": round(w["s"] - t0, 3), "e": round(w["e"] - t0, 3)} for w in ws],
             "regrabada": orig.name}
    json.dump(T, open(tj, "w"), ensure_ascii=False, indent=1)
    print(f"{sl}: {out.relative_to(ROOT)} · {T[sl]['duracion']:.2f} s\n  oído: {T[sl]['texto_oido']}")

if __name__ == "__main__":
    main()
