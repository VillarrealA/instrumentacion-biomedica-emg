#!/usr/bin/env python3
"""Genera y analiza automáticamente los tres registros sintéticos."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    raiz = Path(__file__).resolve().parents[1]
    scripts = raiz / "scripts"
    subprocess.run([sys.executable, str(scripts / "generar_datos_demo.py")], check=True)
    for distancia in (20, 40, 60):
        entrada = raiz / "datos" / "demo" / f"demo_vernier_d{distancia}mm.csv"
        comando = [
            sys.executable,
            str(scripts / "analiza_csv.py"),
            str(entrada),
            "--source", "Vernier_demo",
            "--condition", "protocolo_demo",
            "--spacing-mm", str(distancia),
            "--signal-unit", "mV",
            "--output-dir", str(raiz / "resultados" / "demo"),
            "--name", f"vernier_demo_d{distancia}mm",
        ]
        subprocess.run(comando, check=True)
    print("Demostración terminada. Revise resultados/demo/.")


if __name__ == "__main__":
    main()
