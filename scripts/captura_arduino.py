#!/usr/bin/env python3
"""Captura ``t_us,adc``, grafica la señal y guarda datos y metadatos."""

from __future__ import annotations

import argparse
import json
import time
from collections import deque
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--port", required=True, help="Puerto serie, por ejemplo COM3 o /dev/ttyACM0")
    p.add_argument("--baud", type=int, default=500000)
    p.add_argument("--seconds", type=float, default=30.0)
    p.add_argument("--output", type=Path, required=True, help="Archivo CSV de salida")
    p.add_argument("--adc-bits", type=int, default=10)
    p.add_argument("--vref", type=float, default=5.0)
    p.add_argument("--source", default="Arduino")
    p.add_argument("--condition", default="sin_especificar")
    p.add_argument("--spacing-mm", type=float, default=None)
    p.add_argument("--subject-code", default="anonimo")
    p.add_argument(
        "--live-plot",
        action="store_true",
        help="Muestra durante la captura los últimos segundos de señal.",
    )
    p.add_argument("--plot-window", type=float, default=5.0, help="Ventana visible [s].")
    return p


def preparar_grafica():
    plt.ion()
    figura, eje = plt.subplots(figsize=(9, 4.5), constrained_layout=True)
    linea, = eje.plot([], [], lw=0.8)
    eje.set(xlabel="Tiempo [s]", ylabel="Voltaje [V]", title="EMG adquirido con Arduino")
    eje.grid(alpha=0.25)
    return figura, eje, linea


def main() -> None:
    args = parser().parse_args()
    try:
        import serial
    except ImportError as exc:
        raise SystemExit("Falta pyserial. Ejecute: python -m pip install pyserial") from exc

    print("ADVERTENCIA: utilice únicamente la configuración de adquisición revisada por el docente.")
    print("No conecte a una persona un sistema sin aislamiento y evaluación de seguridad.")

    filas: list[tuple[int, int]] = []
    max_puntos = max(1000, int(5000 * args.plot_window))
    vista: deque[tuple[int, int]] = deque(maxlen=max_puntos)
    figura = eje = linea_grafica = None
    if args.live_plot:
        figura, eje, linea_grafica = preparar_grafica()

    with serial.Serial(args.port, args.baud, timeout=1.0) as puerto:
        time.sleep(2.0)
        puerto.reset_input_buffer()
        inicio = time.monotonic()
        ultima_actualizacion = inicio
        while time.monotonic() - inicio < args.seconds:
            linea = puerto.readline().decode("ascii", errors="ignore").strip()
            if not linea or linea.lower().startswith("t_us"):
                continue
            partes = linea.split(",")
            if len(partes) != 2:
                continue
            try:
                fila = (int(partes[0]), int(partes[1]))
                filas.append(fila)
                vista.append(fila)
            except ValueError:
                continue

            ahora = time.monotonic()
            if args.live_plot and ahora - ultima_actualizacion >= 0.20 and len(vista) > 2:
                datos_vista = np.asarray(vista, dtype=float)
                tv = (datos_vista[:, 0] - datos_vista[-1, 0]) / 1_000_000.0
                vv = datos_vista[:, 1] * args.vref / (2**args.adc_bits - 1)
                mascara = tv >= -args.plot_window
                linea_grafica.set_data(tv[mascara], vv[mascara])
                eje.set_xlim(-args.plot_window, 0.0)
                minimo, maximo = float(np.min(vv[mascara])), float(np.max(vv[mascara]))
                margen = max(0.05, 0.10 * (maximo - minimo))
                eje.set_ylim(minimo - margen, maximo + margen)
                figura.canvas.draw_idle()
                plt.pause(0.001)
                ultima_actualizacion = ahora

    if len(filas) < 20:
        raise SystemExit("Se recibieron muy pocas muestras; revise puerto, baud rate y cableado.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    tabla = pd.DataFrame(filas, columns=["t_us", "adc"])
    tabla["tiempo_s"] = (tabla["t_us"] - tabla["t_us"].iloc[0]) / 1_000_000.0
    tabla["voltaje_v"] = tabla["adc"] * args.vref / (2**args.adc_bits - 1)
    tabla[["t_us", "tiempo_s", "adc", "voltaje_v"]].to_csv(args.output, index=False)

    dt = tabla["tiempo_s"].diff().dropna()
    fs = 1.0 / float(dt.median())
    dt_us = dt.to_numpy(dtype=float) * 1_000_000.0
    periodo_mediano_us = float(np.median(dt_us))
    saltos_estimados = np.maximum(np.rint(dt_us / periodo_mediano_us).astype(int) - 1, 0)
    max_adc = 2**args.adc_bits - 1
    metadatos = {
        "fuente": args.source,
        "condicion": args.condition,
        "separacion_mm": args.spacing_mm,
        "codigo_sujeto": args.subject_code,
        "puerto": args.port,
        "baud": args.baud,
        "adc_bits": args.adc_bits,
        "vref_v": args.vref,
        "muestras": int(len(tabla)),
        "fs_estimada_hz": fs,
        "periodo_mediano_us": periodo_mediano_us,
        "jitter_dt_std_us": float(np.std(dt_us, ddof=1)),
        "muestras_perdidas_estimadas": int(np.sum(saltos_estimados)),
        "adc_min": int(tabla["adc"].min()),
        "adc_max": int(tabla["adc"].max()),
        "voltaje_min_v": float(tabla["voltaje_v"].min()),
        "voltaje_max_v": float(tabla["voltaje_v"].max()),
        "muestras_cerca_riel_inferior": int((tabla["adc"] <= 0.01 * max_adc).sum()),
        "muestras_cerca_riel_superior": int((tabla["adc"] >= 0.99 * max_adc).sum()),
    }
    args.output.with_suffix(".json").write_text(
        json.dumps(metadatos, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    figura_final, eje_final = plt.subplots(figsize=(10, 4.5), constrained_layout=True)
    eje_final.plot(tabla["tiempo_s"], tabla["voltaje_v"], lw=0.7)
    eje_final.set(
        xlabel="Tiempo [s]",
        ylabel="Voltaje [V]",
        title="Captura EMG con Arduino",
    )
    eje_final.grid(alpha=0.25)
    ruta_figura = args.output.with_name(f"{args.output.stem}_captura.png")
    figura_final.savefig(ruta_figura, dpi=180)
    plt.close(figura_final)
    if figura is not None:
        plt.close(figura)

    print(f"Captura guardada en {args.output}")
    print(f"Gráfica guardada en {ruta_figura}")
    print(f"Muestras: {len(tabla)}; frecuencia estimada: {fs:.2f} Hz")
    print(
        "Jitter de periodo: "
        f"{metadatos['jitter_dt_std_us']:.2f} us; "
        f"muestras perdidas estimadas: {metadatos['muestras_perdidas_estimadas']}"
    )


if __name__ == "__main__":
    main()
