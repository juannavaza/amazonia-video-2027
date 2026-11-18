"""Voz de un vídeo con ElevenLabs y los tiempos de cada palabra, para sincronizar la imagen con lo que se dice.

Uso:
  python3 voz.py --proyecto DIR guion.json --simular          # cuenta caracteres, no gasta
  python3 voz.py --proyecto DIR guion.json --tope 5000        # genera lo que falte (con caché)
  python3 voz.py --proyecto DIR guion.json --tope 5000 --bloque intro --rehacer

guion.json:
  {"id": "venta", "pausa": 0.2, "hueco_bloques": 0.6,
   "voz": {"id": "...", "modelo": "eleven_v4", "estabilidad": 0.35, "similitud": 0.7},   (opcional)
   "diccionario": [["Skool", "Skul"]],                                                   (opcional)
   "bloques": [{"id": "intro", "frases": [{"id": "hook", "texto": "..."}]}]}

Cada bloque se genera en UNA toma (la voz enlaza las frases como una persona). Los silencios largos se acortan a
`pausa`. Salida en DIR/voz/<id>/: voz.wav (mono, 48 kHz), tiempos.json y tiempos.js (window.TIEMPOS) con bloques,
frases y palabras. Cada llamada se apunta en DIR/voz/gasto.json; nunca se pasa de --tope.
"""
import argparse
import base64
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

import numpy as np

AQUI = pathlib.Path(__file__).resolve().parent
SR = 48000
# Receta por defecto: la que mejor sonó en las pruebas A/B (eleven_v4, mejor que Multilingual v2). La voz sale, por
# orden, de "voz" en el guion, de voz-defecto.json junto a este script o de la que se eligió en el Estudio de Vídeos.
ESTUDIO = pathlib.Path(os.environ.get("ESTUDIO_DATOS", pathlib.Path.home() / ".estudio-de-videos"))
VOZ_DEFECTO = {"id": None, "modelo": "eleven_v4", "estabilidad": 0.35, "similitud": 0.7, "estilo": 0, "velocidad": 1.0}
_elegida = ESTUDIO / "voz.json"
if _elegida.exists():
    _v = json.loads(_elegida.read_text())
    if _v.get("proveedor", "elevenlabs") == "elevenlabs" and _v.get("id"):
        VOZ_DEFECTO.update({k: _v[k] for k in ("id", "modelo", "estabilidad", "similitud", "velocidad") if k in _v})
if (AQUI / "voz-defecto.json").exists():
    VOZ_DEFECTO.update(json.loads((AQUI / "voz-defecto.json").read_text()))

# Lo que se escribe en pantalla → lo que se le da a la voz (español con anglicismos). Lo más largo, primero.
DICCIONARIO = [
    (r"\bLLM\b", "ele ele eme"), (r"\bOS\b", "o ese"), (r"\bIA\b", "i a"), (r"\bClaude\b", "Clod"), (r"\bSkool\b", "Skul"), (r"\bLoom\b", "Lum"),
    (r"\bGitHub\b", "Guit Jab"), (r"\bgit\b", "guit"), (r"\bGmail\b", "Yimeil"), (r"\bDrive\b", "Draiv"),
    (r"\bZIP\b", "zip"), (r"\bAPI\b", "a pe i"), (r"\bSaaS\b", "sas"), (r"\bCRM\b", "ce erre eme"),
    (r"/([a-z][\w-]*)", lambda m: "barra " + m.group(1).replace("-", " ")),
]


def dicho(texto, extra):
    for a, b in list(extra) + DICCIONARIO:
        texto = re.sub(a, b, texto)
    return texto


def clave(proyecto):
    if os.environ.get("ELEVENLABS_API_KEY"):
        return os.environ["ELEVENLABS_API_KEY"]
    for env in (proyecto / ".env.local", ESTUDIO / ".env.local"):
        if env.exists():
            for linea in env.read_text().splitlines():
                if linea.startswith("ELEVENLABS_API_KEY=") and linea.split("=", 1)[1].strip():
                    return linea.split("=", 1)[1].strip().strip('"')
    sys.exit("Falta la clave de ElevenLabs: guárdala con la página del Estudio de Vídeos\n"
             "(node <estudio-de-videos>/herramientas/clave.mjs), nunca en el chat.")


def pedir(k, voz, texto, antes, despues):
    cuerpo = {"text": texto, "model_id": voz["modelo"],
              "voice_settings": {"stability": voz["estabilidad"], "similarity_boost": voz["similitud"],
                                 "style": voz.get("estilo", 0), "speed": voz.get("velocidad", 1.0), "use_speaker_boost": True}}
    if antes: cuerpo["previous_text"] = antes
    if despues: cuerpo["next_text"] = despues
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voz['id']}/with-timestamps?output_format=mp3_44100_128"
    req = urllib.request.Request(url, data=json.dumps(cuerpo).encode(), method="POST",
                                 headers={"xi-api-key": k, "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 400 and (antes or despues):  # hay modelos que no aceptan el contexto de los vecinos
            return pedir(k, voz, texto, None, None)
        sys.exit(f"ElevenLabs dijo {e.code}: {e.read()[:300]!r}")


def decodificar(f):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(f), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def palabras_alineadas(al):
    """Palabras con inicio y fin; el fin es el de su última letra o cifra, no el del signo de puntuación."""
    out, cur = [], None
    for ch, a, b in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if ch.isspace():
            if cur: out.append(cur)
            cur = None
            continue
        if cur is None: cur = {"texto": "", "inicio": a, "fin": b}
        cur["texto"] += ch
        if ch.isalnum(): cur["fin"] = b
    if cur: out.append(cur)
    return out


def recortar(audio, palabras, pausa):
    margen = .05
    tramos, t0 = [], max(0.0, palabras[0]["inicio"] - margen)
    for p, q in zip(palabras, palabras[1:]):
        if q["inicio"] - p["fin"] > pausa + 2 * margen:
            tramos.append((t0, p["fin"] + pausa / 2))
            t0 = q["inicio"] - pausa / 2
    tramos.append((t0, min(len(audio) / SR, palabras[-1]["fin"] + .35)))
    trozos, mapa, acum, fade = [], [], 0.0, int(.008 * SR)
    for a, b in tramos:
        s = audio[int(a * SR):int(b * SR)].copy()
        if len(s) > 2 * fade:
            s[:fade] *= np.linspace(0, 1, fade); s[-fade:] *= np.linspace(1, 0, fade)
        trozos.append(s); mapa.append((a, b, acum)); acum += len(s) / SR

    def corre(t):
        for a, b, base in mapa:
            if t <= b: return base + max(0.0, t - a)
        a, b, base = mapa[-1]
        return base + (b - a)
    return np.concatenate(trozos), [{**p, "inicio": round(corre(p["inicio"]), 3), "fin": round(corre(p["fin"]), 3)} for p in palabras]


def repartir(texto, oidas):
    vistas = texto.split()
    if len(vistas) == len(oidas):
        return [{"texto": v, "inicio": o["inicio"], "fin": o["fin"]} for v, o in zip(vistas, oidas)]
    a, b = oidas[0]["inicio"], oidas[-1]["fin"]
    pesos = [max(2, len(re.sub(r"\W", "", v)) + 1) for v in vistas]
    total, t, out = sum(pesos), a, []
    for v, w in zip(vistas, pesos):
        d = (b - a) * w / total
        out.append({"texto": v, "inicio": round(t, 3), "fin": round(t + d, 3)}); t += d
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion")
    ap.add_argument("--proyecto", default=".")
    ap.add_argument("--tope", type=int, help="caracteres de ElevenLabs autorizados para este proyecto (obligatorio para gastar)")
    ap.add_argument("--bloque")
    ap.add_argument("--rehacer", action="store_true")
    ap.add_argument("--simular", action="store_true")
    a = ap.parse_args()
    proyecto = pathlib.Path(a.proyecto).resolve()
    guion = json.loads(pathlib.Path(a.guion).read_text())
    voz = {**VOZ_DEFECTO, **guion.get("voz", {})}
    if not voz.get("id"):
        sys.exit("No hay voz elegida: elígela una vez con el Estudio de Vídeos\n"
                 "(node <estudio-de-videos>/herramientas/voces.mjs) o pon \"voz\": {\"id\": \"…\"} en el guion.")
    extra = [tuple(x) for x in guion.get("diccionario", [])]
    salida = proyecto / "voz" / guion["id"]
    cache = salida / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    ledger = proyecto / "voz" / "gasto.json"
    gasto = json.loads(ledger.read_text()) if ledger.exists() else {"usados": 0, "llamadas": []}
    pausa, bloques = guion.get("pausa", .2), guion["bloques"]
    dichos = [" ".join(dicho(f["texto"], extra) for f in b["frases"]) for b in bloques]

    pendientes = []
    for i, b in enumerate(bloques):
        antes = " ".join(dichos[i - 1].split(". ")[-2:]) if i else None
        despues = dichos[i + 1].split(". ")[0] if i + 1 < len(bloques) else None
        h = hashlib.sha1(json.dumps([voz, dichos[i], antes, despues]).encode()).hexdigest()[:12]
        f = cache / f"{b['id']}-{h}.json"
        if (a.rehacer and a.bloque in (None, b["id"])) or not f.exists():
            pendientes.append((i, f, antes, despues))
    n = sum(len(dichos[i]) for i, *_ in pendientes)
    print(f"{guion['id']}: {len(pendientes)} bloques por generar · {n} caracteres · gastados en el proyecto {gasto['usados']}"
          + (f" de {a.tope}" if a.tope else ""))
    if a.simular:
        for i, *_ in pendientes: print(f"  · {bloques[i]['id']}: «{dichos[i][:90]}…»")
        return
    if pendientes:
        if not a.tope: sys.exit("Para gastar hace falta --tope (los caracteres que el usuario ha autorizado).")
        if gasto["usados"] + n > a.tope: sys.exit("Pasaría del tope autorizado: no genero nada.")
        k = clave(proyecto)
    for i, f, antes, despues in pendientes:
        r = pedir(k, voz, dichos[i], antes, despues)
        gasto["usados"] += len(dichos[i]); gasto["llamadas"].append({"caracteres": len(dichos[i]), "que": f"{guion['id']}/{bloques[i]['id']}"})
        ledger.write_text(json.dumps(gasto, ensure_ascii=False, indent=1))
        f.with_suffix(".mp3").write_bytes(base64.b64decode(r["audio_base64"]))
        f.write_text(json.dumps({"alignment": r.get("alignment") or r.get("normalized_alignment")}, ensure_ascii=False))
        print(f"  ✓ {bloques[i]['id']} ({len(dichos[i])} caracteres)")

    pista, t, ib, ifr, ip = [], 0.0, [], [], []
    for i, b in enumerate(bloques):
        f = sorted(cache.glob(f"{b['id']}-*.json"), key=lambda p: p.stat().st_mtime)[-1]
        audio, ws = recortar(decodificar(f.with_suffix(".mp3")), palabras_alineadas(json.loads(f.read_text())["alignment"]), pausa)
        if i:
            hueco = np.zeros(int(guion.get("hueco_bloques", .6) * SR), dtype=np.float32)
            pista.append(hueco); t += len(hueco) / SR
        ib.append({"id": b["id"], "inicio": round(t, 3), "fin": round(t + len(audio) / SR, 3)})
        k_ = 0
        for fr in b["frases"]:
            n_ = len(dicho(fr["texto"], extra).split())
            oidas = [{**w, "inicio": w["inicio"] + t, "fin": w["fin"] + t} for w in ws[k_:k_ + n_]]
            k_ += n_
            if not oidas: sys.exit(f"Sin palabras para {fr['id']}: revisa la alineación")
            ifr.append({"id": fr["id"], "bloque": b["id"], "texto": fr["texto"], "inicio": round(oidas[0]["inicio"], 3), "fin": round(oidas[-1]["fin"], 3)})
            ip += [{**v, "inicio": round(v["inicio"], 3), "fin": round(v["fin"], 3), "frase": fr["id"]} for v in repartir(fr["texto"], oidas)]
        if k_ != len(ws): print(f"  ⚠ {b['id']}: {len(ws)} palabras oídas y {k_} esperadas")
        pista.append(audio); t += len(audio) / SR
    v = np.concatenate(pista)
    v = v / max(1e-6, float(np.max(np.abs(v)))) * .89
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", str(salida / "voz.wav")],
                   input=v.astype(np.float32).tobytes(), check=True)
    datos = {"id": guion["id"], "duracion": round(len(v) / SR, 3), "voz": voz, "pausa": pausa, "bloques": ib, "frases": ifr, "palabras": ip}
    (salida / "tiempos.json").write_text(json.dumps(datos, ensure_ascii=False, indent=1))
    (salida / "tiempos.js").write_text("window.TIEMPOS=" + json.dumps(datos, ensure_ascii=False) + ";\n")
    print(f"{guion['id']}: {datos['duracion']} s · {len(ifr)} frases · {len(ip)} palabras → {salida}")


if __name__ == "__main__":
    main()
