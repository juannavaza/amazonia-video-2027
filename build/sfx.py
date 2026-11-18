"""Efectos de transición sintetizados (sin librerías de terceros): whoosh y pop.

Uso: .venv/bin/python -I build/sfx.py   → audio/sfx/whoosh.wav, whoosh_corto.wav, pop.wav (mono, 44,1 kHz)
"""
import subprocess
from pathlib import Path
import numpy as np

SR = 44100
OUT = Path(__file__).resolve().parent.parent / "audio" / "sfx"
rng = np.random.default_rng(7)

def guarda(nombre, x, pico_db):
    x = x / (np.abs(x).max() + 1e-9) * 10 ** (pico_db / 20)
    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-c:a", "pcm_s16le", str(OUT / f"{nombre}.wav")], input=x.astype("<f4").tobytes(), check=True)
    print(OUT / f"{nombre}.wav", f"{len(x) / SR:.2f}s")

def whoosh(dur=0.7, f0=300, f1=2600, q=2.2, pico=0.42):
    """Ruido filtrado por un paso banda que barre de f0 a f1, con envolvente asimétrica."""
    n = int(dur * SR); t = np.arange(n) / n
    ruido = rng.standard_normal(n)
    fc = f0 * (f1 / f0) ** (np.sin(np.pi * t / 2) ** 2)   # barrido suave
    y = np.zeros(n); y1 = y2 = 0.0; x1 = x2 = 0.0
    for i in range(n):                                     # biquad paso banda con coeficientes variables
        w = 2 * np.pi * fc[i] / SR; al = np.sin(w) / (2 * q); a0 = 1 + al
        b0, b2, a1, a2 = al / a0, -al / a0, -2 * np.cos(w) / a0, (1 - al) / a0
        yi = b0 * ruido[i] + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1 = x1, ruido[i]; y2, y1 = y1, yi; y[i] = yi
    env = np.where(t < pico, (t / pico) ** 2, ((1 - t) / (1 - pico)) ** 1.6)
    return y * env

def pop(dur=0.18):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 900 * np.exp(-t * 18) + 180                       # tono que cae rápido
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28)
    return x + 0.15 * rng.standard_normal(n) * np.exp(-t * 90)

if __name__ == "__main__":
    guarda("whoosh", whoosh(), -9)
    guarda("whoosh_corto", whoosh(0.42, 500, 3200, pico=0.35), -11)
    guarda("pop", pop(), -14)
