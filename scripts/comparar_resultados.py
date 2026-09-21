#!/usr/bin/env python3
"""Integra los archivos *_resumen.csv y genera una comparación del equipo."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("directorio", type=Path, help="Directorio que contiene archivos *_resumen.csv")
    p.add_argument("--output-dir", type=Path, default=Path("resultados/comparacion"))
    return p


def nombre_seguro(texto: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", texto).strip("_") or "fuente"


def etiquetas_para(tabla: pd.DataFrame) -> list[str]:
    etiquetas: list[str] = []
    for i, fila in tabla.iterrows():
        separacion = fila.get("separacion_mm", np.nan)
        if pd.notna(separacion):
            etiquetas.append(f"{separacion:g} mm")
        else:
            etiquetas.append(str(fila.get("registro", fila.get("condicion", f"R{i+1}"))))
    return etiquetas


def main() -> None:
    args = parser().parse_args()
    archivos = sorted(args.directorio.rglob("*_resumen.csv"))
    if not archivos:
        raise SystemExit("No se encontraron archivos *_resumen.csv.")

    tablas = []
    for archivo in archivos:
        tabla = pd.read_csv(archivo)
        tabla["archivo_resumen"] = str(archivo)
        tablas.append(tabla)
    integrada = pd.concat(tablas, ignore_index=True, sort=False)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if "fuente" not in integrada.columns:
        integrada["fuente"] = "sin_especificar"
    integrada["fuente"] = integrada["fuente"].fillna("sin_especificar").astype(str)

    # Las amplitudes de instrumentos diferentes no comparten necesariamente
    # unidades, ganancias ni ancho de banda. Las columnas relativas sólo se
    # normalizan dentro de cada fuente y no convierten los sistemas en equivalentes.
    for columna in ("rms", "potencia_espectral_banda"):
        if columna in integrada.columns:
            valores = pd.to_numeric(integrada[columna], errors="coerce")
            maximos = valores.groupby(integrada["fuente"]).transform("max")
            integrada[f"{columna}_relativa_fuente"] = valores / maximos.replace(0, np.nan)

    integrada.to_csv(args.output_dir / "comparacion_completa.csv", index=False)

    metricas = [
        ("rms", "RMS"),
        ("frecuencia_mediana_hz", "Frecuencia mediana [Hz]"),
        ("potencia_espectral_banda", "Potencia espectral de la señal"),
    ]
    figuras: list[Path] = []
    for fuente, grupo in integrada.groupby("fuente", sort=False):
        grupo = grupo.reset_index(drop=True)
        etiquetas = etiquetas_para(grupo)
        fig, ejes = plt.subplots(len(metricas), 1, figsize=(10, 9), constrained_layout=True)
        for eje, (columna, titulo) in zip(ejes, metricas):
            if columna in grupo.columns:
                valores = pd.to_numeric(grupo[columna], errors="coerce")
            else:
                valores = pd.Series(np.nan, index=grupo.index)
            eje.bar(np.arange(len(grupo)), valores)
            eje.set_ylabel(titulo)
            eje.grid(axis="y", alpha=0.25)
        nombre_fuente = fuente.replace("_", " ")
        ejes[0].set_title(f"Comparación dentro de la fuente: {nombre_fuente}")
        ejes[-1].set_xticks(np.arange(len(grupo)), etiquetas, rotation=35, ha="right")
        ruta_figura = args.output_dir / f"comparacion_{nombre_seguro(fuente)}.png"
        fig.savefig(ruta_figura, dpi=180)
        plt.close(fig)
        figuras.append(ruta_figura)

    print(f"Comparación guardada en {args.output_dir}")
    for figura in figuras:
        print(f"  figura: {figura}")


if __name__ == "__main__":
    main()
