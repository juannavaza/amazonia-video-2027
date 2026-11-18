"""Alarga una pista de música repitiendo un bloque de N compases, con el empalme ajustado a la muestra.

Uso: .venv/bin/python -I build/alargar_musica.py <entrada> <salida.wav> <segundos_objetivo> [bpm]
- Busca el bloque de compases cuyo final se parece más a su principio (similitud espectral),
  coloca el empalme sobre un golpe de percusión y afina el desfase por correlación de onda.
- Funde 40 ms en el empalme y normaliza a -36 LUFS (20 dB por debajo de la voz).
"""
import re, subprocess, sys
import numpy as np

SR = 44100

def lee(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

def flujo(mono, hop=256):
    n = len(mono) // hop - 4
    fr = np.lib.stride_tricks.sliding_window_view(mono, 1024)[::hop][:n] * np.hanning(1024)
    S = np.log1p(np.abs(np.fft.rfft(fr, axis=1)))
    return S, np.r_[0, np.maximum(np.diff(S, axis=0), 0).sum(1)], SR / hop

def main():
    src, out, objetivo = sys.argv[1], sys.argv[2], float(sys.argv[3])
    x = lee(src); mono = x.mean(1); dur = len(x) / SR
    falta = objetivo - dur
    # 1) buscar la repetición real: correlación normalizada de onda (8 kHz) entre una ventana de 2 s
    #    y la misma música N compases después, probando puntos de partida en la zona central
    sr8 = 8000
    m8 = np.interp(np.arange(0, len(mono), SR / sr8), np.arange(len(mono)), mono)
    cs = np.r_[0, np.cumsum(m8 * m8)]
    def busca(p, Lmin, Lmax, win=2.0):
        P = int(p * sr8); w = int(win * sr8); ref = m8[P:P + w]
        s0 = P + int(Lmin * sr8); seg = m8[s0:P + int(Lmax * sr8) + w]
        n = 1 << int(np.ceil(np.log2(len(seg) + w)))
        c = np.fft.irfft(np.fft.rfft(seg, n) * np.conj(np.fft.rfft(ref, n)), n)[:len(seg) - w + 1]
        e = np.sqrt(cs[s0 + w:s0 + w + len(c)] - cs[s0:s0 + len(c)])
        c = c / (np.linalg.norm(ref) * e + 1e-9); k = int(np.argmax(c)); return c[k], Lmin + k / sr8
    cand = []
    for p in np.arange(20, dur - 40, 0.5):
        Lmin, Lmax = max(falta, 4.0), max(falta, 4.0) + 3.0
        if p + Lmax + 3 < dur:
            c, L = busca(p, Lmin, Lmax); cand.append((c, p, L))
    corr, p, L0 = max(cand)
    # 2) afinar a la muestra (44,1 kHz, ±2 ms)
    w = int(0.5 * SR); P = int(p * SR); ref = mono[P:P + w]
    best, Lbest = -1e9, int(L0 * SR)
    for d in range(-int(0.002 * SR), int(0.002 * SR) + 1):
        q = P + int(L0 * SR) + d; c = float(np.dot(ref, mono[q:q + w]))
        if c > best: best, Lbest = c, int(L0 * SR) + d
    bpm = float("nan"); nb = "?"
    # 4) montar: x[0 : P+L] + x[P : ] con fundido de 40 ms
    J = P + Lbest; xf = int(0.04 * SR)
    head, tail = x[:J + xf].copy(), x[P:].copy()
    ramp = np.linspace(0, 1, xf)[:, None]
    head[-xf:] = head[-xf:] * (1 - ramp) + tail[:xf] * ramp
    y = np.concatenate([head, tail[xf:]])
    corr = best / (np.linalg.norm(ref) * np.linalg.norm(mono[J:J + w]) + 1e-9)
    print(f"bloque de {Lbest / SR:.4f} s repetido desde {p:.2f}s · "
          f"correlación del empalme {corr:.3f} · {dur:.2f}s → {len(y) / SR:.2f}s")
    tmp = out + ".raw.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s16le", tmp],
                   input=np.clip(y, -1, 1).astype("<f4").tobytes(), check=True)
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", tmp, "-af", "ebur128",
              "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", f"volume={-36 - I:.2f}dB", "-c:a", "pcm_s16le", out], check=True)
    import os; os.remove(tmp)
    print(f"{out}: de {I:.1f} a -36 LUFS")

if __name__ == "__main__":
    main()
