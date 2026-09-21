#!/usr/bin/env python3
"""Descarga y analiza los tres ejemplos oficiales de EMG de PhysioNet."""

from __future__ import annotations

import argparse
import urllib.error
import urllib.request
from pathlib import Path

from emg_core import ProcessingConfig, cargar_physionet_txt, guardar_resultados, procesar_emg


BASE_URL = "https://physionet.org/files/emgdb/1.0.0"
REGISTROS = {
    "emg_healthy": "sin_enfermedad_neuromuscular",
    "emg_neuropathy": "neuropatia",
    "emg_myopathy": "miopatia",
}


def descargar(url: str, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(url, destino)
    except urllib.error.URLError as exc:
        raise SystemExit(
            f"No fue posible descargar {url}. Conserve el archivo en {destino} y vuelva a ejecutar."
        ) from exc


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", type=Path, default=Path("datos/physionet"))
    p.add_argument("--output-dir", type=Path, default=Path("resultados/physionet"))
    p.add_argument("--start", type=float, default=0.0, help="Inicio de la ventana [s]")
    p.add_argument("--duration", type=float, default=2.0, help="Duración común de la ventana [s]")
    p.add_argument("--notch", type=float, default=None)
    p.add_argument(
        "--blind",
        action="store_true",
        help="Oculta la condición en las salidas; no impide identificarla revisando el código fuente.",
    )
    return p


def main() -> None:
    args = parser().parse_args()
    config = ProcessingConfig(
        highpass_hz=20.0,
        lowpass_hz=450.0,
        notch_hz=args.notch,
        envelope_hz=5.0,
        rms_window_ms=100.0,
        power_low_hz=20.0,
        power_high_hz=450.0,
    )

    for indice, (registro, condicion) in enumerate(REGISTROS.items(), start=1):
        archivo = args.data_dir / f"{registro}.txt"
        if not archivo.exists():
            print(f"Descargando {registro}...")
            descargar(f"{BASE_URL}/{registro}.txt", archivo)

        t, x, fs = cargar_physionet_txt(archivo)
        fin = args.start + args.duration
        mascara = (t >= args.start) & (t < fin)
        if mascara.sum() < 20:
            raise SystemExit(f"La ventana solicitada no existe en {registro}.")
        tw = t[mascara] - t[mascara][0]
        xw = x[mascara]
        resultados = procesar_emg(tw, xw, fs, config)
        etiqueta = f"registro_{indice}" if args.blind else registro
        metadatos = {
            "fuente": "PhysioNet emgdb 1.0.0",
            "registro": etiqueta,
            "condicion": "oculta" if args.blind else condicion,
            "modalidad": "EMG de aguja",
            "unidad_senal": "mV",
            "separacion_mm": None,
            "ventana_inicio_s": args.start,
            "ventana_fin_s": fin,
            "url_fuente": f"{BASE_URL}/{registro}.txt",
        }
        guardar_resultados(resultados, args.output_dir, etiqueta, metadatos, config)
        print(f"Analizado: {etiqueta}")

    print(f"Resultados guardados en {args.output_dir}")


if __name__ == "__main__":
    main()
