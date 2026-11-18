import sys
from pathlib import Path
sys.argv = ["borrador.py"]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import borrador as Bm
Bm.ETIQUETA = False
Bm.TRAMOS_DIR = Bm.OUTDIR / "tramos_alba_sin_etiqueta"
for k in sys.argv_k if hasattr(sys, "argv_k") else []: pass
