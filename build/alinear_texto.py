"""Alternativa a Whisper para sustituir_frase.py cuando no se puede descargar el modelo (sin red a Hugging Face).
Reparte las palabras del texto conocido sobre los tramos con voz (energía RMS), en proporción a sus letras.
Uso: python3 build/alinear_texto.py sNN archivo.mp3 "texto exacto de la locución"
"""
import re, subprocess, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sustituir_frase as S

TEXTO = sys.argv.pop(3)

def transcribe(f, umbral=-38.0, vent=0.02, hueco=0.09):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32); n = int(16000 * vent)
    r = np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + n] ** 2)) + 1e-9) for i in range(0, len(x) - n, n)])
    on = r > umbral; tramos, ini = [], None
    for i, v in enumerate(on):
        if v and ini is None: ini = i
        if not v and ini is not None: tramos.append([ini * vent, i * vent]); ini = None
    if ini is not None: tramos.append([ini * vent, len(on) * vent])
    fus = [tramos[0]]
    for a, b in tramos[1:]:
        if a - fus[-1][1] < hueco: fus[-1][1] = b
        else: fus.append([a, b])
    # si el texto tiene tantos trozos (separados por signos de puntuación) como tramos con voz, se reparte trozo a trozo
    if len(fus) > 1:   # tramos de voz muy cortos (p. ej. una «Y» suelta) se unen al siguiente
        j = []
        for k, (a, b) in enumerate(fus):
            if j and j[-1][2]: j[-1] = [j[-1][0], b, (b - j[-1][0]) < .2]
            else: j.append([a, b, (b - a) < .2])
        fus = [[a, b] for a, b, _ in j]
    trozos = [t.strip() for t in re.findall(r"[^.,:;?!]+[.,:;?!]?", TEXTO) if t.strip()]
    if len(trozos) == len(fus):
        out = []
        for (a, b), tz in zip(fus, trozos):
            ws = tz.split(); let = [max(1, len(re.sub(r"[^\wáéíóúñü]", "", w.lower()))) for w in ws]; tot = sum(let); acc = 0
            for w, l in zip(ws, let):
                out.append({"w": w, "s": round(a + (b - a) * acc / tot, 3), "e": round(a + (b - a) * (acc + l) / tot, 3)}); acc += l
        print("tramos con voz (trozo a trozo):", [(round(a, 2), round(b, 2)) for a, b in fus])
        return out
    L = sum(b - a for a, b in fus)
    ws = TEXTO.split(); let = [max(1, len(re.sub(r"[^\wáéíóúñü]", "", w.lower()))) for w in ws]; tot = sum(let)
    def t_de(frac):   # fracción del tiempo con voz → instante absoluto
        q = frac * L
        for a, b in fus:
            if q <= b - a: return a + q
            q -= b - a
        return fus[-1][1]
    out, acc = [], 0
    for w, l in zip(ws, let):
        s, e = t_de(acc / tot), t_de((acc + l) / tot); acc += l
        out.append({"w": w, "s": round(s, 3), "e": round(e, 3)})
    print("tramos con voz:", [(round(a, 2), round(b, 2)) for a, b in fus])
    return out

S.transcribe = transcribe
S.main()
