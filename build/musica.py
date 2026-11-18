"""Música de fondo original (sintetizada por código, libre de derechos) para el borrador Amazonia 2027.

Groove cálido y luminoso a 96 BPM en Fa mayor: teclado tipo Rhodes, bajo, marimba (guiño tropical),
bombo suave y shaker. Sin melodía protagonista, para que la voz mande.

Uso: .venv/bin/python -I build/musica.py [duración_en_segundos]
Salida: audio/musica/musica_borrador.wav (estéreo, 44,1 kHz) normalizada a -36 LUFS (20 dB por debajo de la voz).
"""
import re, subprocess, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "audio/musica/musica_borrador.wav"
SR = 44100
BPM = 96
BEAT = 60 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(7)

def hz(m): return 440 * 2 ** ((m - 69) / 12)

# Fmaj7 · Am7 · Dm7 · Bbmaj7 (I · iii · vi · IV)
CHORDS = [([53, 57, 60, 64], 41), ([55, 57, 60, 64], 45), ([53, 57, 60, 62], 38), ([53, 57, 58, 62], 46)]

def env(n, a, d):
    t = np.arange(n) / SR
    e = np.exp(-t / d)
    na = max(1, int(a * SR)); e[:na] *= np.linspace(0, 1, na)
    return e

def add(buf, x, t0, pan=0.0, g=1.0):
    i = int(t0 * SR)
    if i >= buf.shape[1]: return
    x = x[: buf.shape[1] - i] * g
    buf[0, i:i + len(x)] += x * np.sqrt(0.5 * (1 - pan))
    buf[1, i:i + len(x)] += x * np.sqrt(0.5 * (1 + pan))

def keys(f, dur):
    n = int((dur + 1.2) * SR); t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * f * t) * np.exp(-t / 0.25))   # Rhodes: FM suave
    tone += 0.35 * np.sin(2 * np.pi * f * 1.003 * t) + 0.12 * np.sin(2 * np.pi * 2 * f * t)
    e = env(n, 0.006, 1.1)
    rel = int(dur * SR); e[rel:] *= np.exp(-np.arange(n - rel) / SR / 0.18)
    return tone * e

def bass(f, dur):
    n = int((dur + .2) * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    e = env(n, 0.01, 0.9); rel = int(dur * SR); e[rel:] *= np.exp(-np.arange(n - rel) / SR / 0.05)
    return np.tanh(1.4 * x) * e

def marimba(f):
    n = int(0.7 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * env(n, .002, .28) + 0.3 * np.sin(2 * np.pi * 3.93 * f * t) * env(n, .001, .05))

def kick():
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 45 + 75 * np.exp(-t / 0.04)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .001, .14)

def shaker():
    n = int(0.09 * SR)
    x = np.diff(rng.standard_normal(n + 1)); x = np.diff(np.concatenate([[0], x]))
    return x * env(n, .004, .025)

def reverb(x, secs=1.6, mix=0.22):
    n = int(secs * SR)
    ir = rng.standard_normal((2, n)) * np.exp(-np.arange(n) / SR / (secs / 5))
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    L = x.shape[1] + n - 1; N = 1 << (L - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[:, :x.shape[1]]
    return x + mix * wet

def componer(dur):
    nbars = int(np.ceil(dur / BAR)) + 1
    pads = np.zeros((2, int((nbars + 2) * BAR * SR)))
    dry = np.zeros_like(pads)
    final = nbars - 2
    for b in range(nbars):
        t0 = b * BAR
        notes, root = CHORDS[b % 4] if b < final else CHORDS[0]
        if b >= final:   # cierre: Fmaj7 largo
            if b == final:
                for j, m in enumerate(notes): add(pads, keys(hz(m), 2 * BAR), t0 + j * 0.02, pan=-.3 + .2 * j, g=.18)
                add(dry, bass(hz(root), 2 * BAR), t0, g=.3)
            continue
        # teclado: tiempo 1 largo y anticipación en el «y» del 2
        for j, m in enumerate(notes):
            add(pads, keys(hz(m), 1.4 * BEAT), t0 + j * 0.012, pan=-.3 + .2 * j, g=.16)
            add(pads, keys(hz(m), .5 * BEAT), t0 + 1.5 * BEAT + j * 0.01, pan=-.3 + .2 * j, g=.10)
            add(pads, keys(hz(m), 1.2 * BEAT), t0 + 2.5 * BEAT + j * 0.01, pan=-.3 + .2 * j, g=.12)
        if b >= 4:   # bajo y percusión
            for bt, l in ((0, 1.4), (1.5, .4), (2, .9), (3.5, .4)):
                add(dry, bass(hz(root), l * BEAT), t0 + bt * BEAT, g=.32)
            for bt in (0, 2):
                add(dry, kick(), t0 + bt * BEAT, g=.55)
        for s in range(8):   # shaker en corcheas, acento a contratiempo
            add(dry, shaker(), t0 + s * BEAT / 2 + rng.normal(0, .004), pan=.35, g=(.10 if s % 2 else .055) * (1 if b >= 2 else .5))
        if 12 <= b and (b // 16) % 2 == 0 or b >= 44:   # marimba por secciones
            arp = [notes[1] + 12, notes[3] + 12, notes[2] + 12, notes[3] + 12, notes[1] + 24, notes[3] + 12]
            for s, pos in enumerate((0, .75, 1.5, 2, 2.75, 3.5)):
                add(pads, marimba(hz(arp[s])), t0 + pos * BEAT, pan=(.4 if s % 2 else -.2), g=.13)
    mixd = reverb(pads, 1.8, .28) + reverb(dry, .9, .08)
    n = int(dur * SR); mixd = mixd[:, :n]
    fo = int(3 * SR); mixd[:, -fo:] *= np.linspace(1, 0, fo) ** 2
    fi = int(1.0 * SR); mixd[:, :fi] *= np.linspace(0, 1, fi)
    return mixd / np.abs(mixd).max() * 0.9

def main():
    dur = float(sys.argv[1]) if len(sys.argv) > 1 else 190
    OUT.parent.mkdir(parents=True, exist_ok=True)
    x = componer(dur)
    raw = OUT.with_suffix(".raw.wav")
    pcm = (np.clip(x.T, -1, 1) * 32767).astype("<i2").tobytes()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", str(raw)], input=pcm, check=True)
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(raw), "-af", "ebur128",
              "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"volume={-36 - I:.2f}dB", str(OUT)], check=True)
    raw.unlink()
    print(f"{OUT.relative_to(ROOT)}: {dur:.1f} s · de {I:.1f} a -36 LUFS")

if __name__ == "__main__":
    main()
