#!/usr/bin/env python3
"""Analiza archivos CSV de Vernier, Arduino u otras fuentes EMG."""

from __future__ import annotations

import argparse
from pathlib import Path

from emg_core import ProcessingConfig, cargar_csv_emg, guardar_resultados, procesar_emg


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archivo", type=Path, help="CSV que contiene tiempo y señal EMG")
    parser.add_argument("--fs", type=float, default=None, help="Frecuencia de muestreo si el CSV no contiene tiempo")
    parser.add_argument("--time-column", default=None, help="Nombre exacto de la columna de tiempo")
    parser.add_argument("--signal-column", default=None, help="Nombre exacto de la columna de señal")
    parser.add_argument("--sep", default=None, help="Separador del CSV, por ejemplo ';'")
    parser.add_argument("--decimal", default=".", choices=(".", ","), help="Separador decimal")
    parser.add_argument("--source", default="CSV", help="Vernier, Arduino u otra fuente")
    parser.add_argument("--condition", default="sin_especificar", help="Reposo, contracción, etc.")
    parser.add_argument("--spacing-mm", type=float, default=None, help="Separación centro a centro; omitir si no aplica")
    parser.add_argument("--subject-code", default="anonimo", help="Código anónimo, nunca nombre del estudiante")
    parser.add_argument(
        "--signal-unit",
        default="unidad de entrada",
        help="Unidad de la columna analizada, por ejemplo V o mV.",
    )
    parser.add_argument("--start", type=float, default=None, help="Inicio de la ventana en segundos")
    parser.add_argument("--end", type=float, default=None, help="Fin de la ventana en segundos")
    parser.add_argument("--highpass", type=float, default=20.0)
    parser.add_argument("--lowpass", type=float, default=450.0)
    parser.add_argument("--notch", type=float, default=None, help="Frecuencia notch; úsela sólo si está justificada")
    parser.add_argument("--envelope", type=float, default=5.0)
    parser.add_argument("--rms-window-ms", type=float, default=250.0)
    parser.add_argument("--output-dir", type=Path, default=Path("resultados"))
    parser.add_argument("--name", default=None, help="Nombre base de los archivos de salida")
    return parser


def main() -> None:
    args = construir_parser().parse_args()
    t, x, fs, metadatos_carga = cargar_csv_emg(
        args.archivo,
        fs=args.fs,
        columna_tiempo=args.time_column,
        columna_senal=args.signal_column,
        separador=args.sep,
        decimal=args.decimal,
    )

    inicio = 0.0 if args.start is None else args.start
    final = float(t[-1]) if args.end is None else args.end
    if inicio < 0 or final <= inicio:
        raise SystemExit("La ventana solicitada no es válida.")
    mascara = (t >= inicio) & (t <= final)
    if mascara.sum() < 20:
        raise SystemExit("La ventana contiene muy pocas muestras.")
    t_ventana = t[mascara] - t[mascara][0]
    x_ventana = x[mascara]

    config = ProcessingConfig(
        highpass_hz=args.highpass,
        lowpass_hz=args.lowpass,
        notch_hz=args.notch,
        envelope_hz=args.envelope,
        rms_window_ms=args.rms_window_ms,
        power_low_hz=args.highpass,
        power_high_hz=args.lowpass,
    )
    resultados = procesar_emg(t_ventana, x_ventana, fs, config)
    metadatos = {
        **metadatos_carga,
        "fuente": args.source,
        "condicion": args.condition,
        "separacion_mm": args.spacing_mm,
        "codigo_sujeto": args.subject_code,
        "unidad_senal": args.signal_unit,
        "ventana_inicio_s": inicio,
        "ventana_fin_s": final,
    }
    nombre = args.name or f"{args.source}_{args.condition}_{args.archivo.stem}"
    rutas = guardar_resultados(resultados, args.output_dir, nombre, metadatos, config)
    print("Análisis terminado:")
    for etiqueta, ruta in rutas.items():
        print(f"  {etiqueta}: {ruta}")


if __name__ == "__main__":
    main()
