#!/usr/bin/env python3
"""Genera señales sintéticas para comprobar el repositorio sin hardware."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal


def emg_sintetico(fs: float, duracion: float, escala: float, semilla: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(semilla)
    t = np.arange(0.0, duracion, 1.0 / fs)
    ruido = rng.normal(0.0, 1.0, len(t))
    sos = signal.butter(4, (25.0, min(350.0, 0.42 * fs)), btype="bandpass", fs=fs, output="sos")
    banda = signal.sosfiltfilt(sos, ruido)
    envolvente = np.full_like(t, 0.08)
    envolvente[(t >= 2.0) & (t < 5.0)] = 0.45
    envolvente[(t >= 6.0) & (t < 9.0)] = 1.00
    deriva = 0.02 * np.sin(2 * np.pi * 0.5 * t)
    red = 0.01 * np.sin(2 * np.pi * 60.0 * t)
    x = escala * envolvente * banda / np.std(banda) + deriva + red
    return t, x


def main() -> None:
    salida = Path(__file__).resolve().parents[1] / "datos" / "demo"
    salida.mkdir(parents=True, exist_ok=True)
    fs = 2000.0
    for distancia, escala, semilla in ((20, 0.75, 20), (40, 1.00, 40), (60, 1.12, 60)):
        t, x = emg_sintetico(fs, 10.0, escala, semilla)
        pd.DataFrame({"tiempo_s": t, "emg_mV": x}).to_csv(
            salida / f"demo_vernier_d{distancia}mm.csv", index=False
        )
    print(f"Datos sintéticos guardados en {salida}")


if __name__ == "__main__":
    main()
