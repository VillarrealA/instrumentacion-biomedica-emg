"""Funciones comunes para cargar, procesar y resumir señales EMG.

El módulo trabaja con señales superficiales o de aguja, pero conserva en los
metadatos la fuente de adquisición para evitar comparaciones inadecuadas.
"""

from __future__ import annotations

import json
import math
import re
import warnings
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import signal
from scipy.integrate import trapezoid


@dataclass
class ProcessingConfig:
    highpass_hz: float = 20.0
    lowpass_hz: float = 450.0
    notch_hz: float | None = None
    envelope_hz: float = 5.0
    rms_window_ms: float = 250.0
    power_low_hz: float = 20.0
    power_high_hz: float = 450.0


def _normalizar_nombre(texto: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(texto).strip().lower())


def _columna_por_preferencia(columnas: list[str], preferencias: tuple[str, ...]) -> str | None:
    normalizadas = {_normalizar_nombre(c): c for c in columnas}
    for preferencia in preferencias:
        objetivo = _normalizar_nombre(preferencia)
        for normalizada, original in normalizadas.items():
            if objetivo == normalizada or objetivo in normalizada:
                return original
    return None


def cargar_csv_emg(
    ruta: str | Path,
    fs: float | None = None,
    columna_tiempo: str | None = None,
    columna_senal: str | None = None,
    separador: str | None = None,
    decimal: str = ".",
) -> tuple[np.ndarray, np.ndarray, float, dict[str, Any]]:
    """Carga un CSV de Vernier, Arduino o un archivo genérico.

    Si no existe columna de tiempo, ``fs`` es obligatorio. El lector intenta
    identificar automáticamente las columnas, pero permite especificarlas.
    """

    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el archivo: {ruta}")

    kwargs: dict[str, Any] = {
        "comment": "#",
        "decimal": decimal,
        "on_bad_lines": "skip",
    }
    if separador:
        kwargs["sep"] = separador
    else:
        kwargs["sep"] = None
        kwargs["engine"] = "python"

    tabla = pd.read_csv(ruta, **kwargs)
    tabla.columns = [str(c).strip() for c in tabla.columns]
    if tabla.empty or len(tabla.columns) < 1:
        raise ValueError("El archivo no contiene datos tabulares utilizables.")

    numericas = pd.DataFrame()
    for columna in tabla.columns:
        numericas[columna] = pd.to_numeric(tabla[columna], errors="coerce")

    if columna_tiempo and columna_tiempo not in numericas.columns:
        raise ValueError(f"No existe la columna de tiempo '{columna_tiempo}'.")
    if columna_senal and columna_senal not in numericas.columns:
        raise ValueError(f"No existe la columna de señal '{columna_senal}'.")

    if columna_tiempo is None:
        columna_tiempo = _columna_por_preferencia(
            list(numericas.columns),
            ("tiempo", "time", "seconds", "segundos", "t_s", "t"),
        )

    if columna_senal is None:
        candidatas = [c for c in numericas.columns if c != columna_tiempo]
        columna_senal = _columna_por_preferencia(
            candidatas,
            ("emg", "potential", "potencial", "voltage", "voltaje", "signal", "senal", "adc"),
        )
        if columna_senal is None and candidatas:
            conteos = {c: int(numericas[c].notna().sum()) for c in candidatas}
            columna_senal = max(conteos, key=conteos.get)

    if columna_senal is None:
        raise ValueError("No fue posible identificar una columna de señal.")

    if columna_tiempo is not None:
        seleccion = numericas[[columna_tiempo, columna_senal]].dropna()
        t = seleccion[columna_tiempo].to_numpy(dtype=float)
        x = seleccion[columna_senal].to_numpy(dtype=float)
        orden = np.argsort(t)
        t, x = t[orden], x[orden]
        indices_unicos = np.concatenate(([True], np.diff(t) > 0))
        t, x = t[indices_unicos], x[indices_unicos]
        if len(t) < 4:
            raise ValueError("Hay muy pocas muestras válidas.")
        dt = np.diff(t)
        fs_estimada = 1.0 / float(np.median(dt))
        if not np.isfinite(fs_estimada) or fs_estimada <= 0:
            raise ValueError("No fue posible estimar la frecuencia de muestreo.")
        fs_final = float(fs) if fs else fs_estimada
    else:
        if fs is None or fs <= 0:
            raise ValueError("Debe proporcionar --fs cuando el archivo no contiene tiempo.")
        x = numericas[columna_senal].dropna().to_numpy(dtype=float)
        fs_final = float(fs)
        t = np.arange(len(x), dtype=float) / fs_final

    if len(x) < max(20, int(fs_final * 0.1)):
        raise ValueError("La señal es demasiado corta para el análisis solicitado.")

    metadatos = {
        "archivo": str(ruta),
        "columna_tiempo": columna_tiempo,
        "columna_senal": columna_senal,
        "fs_hz": fs_final,
        "muestras": int(len(x)),
        "duracion_s": float(t[-1] - t[0]) if len(t) > 1 else 0.0,
    }
    return t - t[0], x, fs_final, metadatos


def cargar_physionet_txt(ruta: str | Path) -> tuple[np.ndarray, np.ndarray, float]:
    # Los archivos originales se sirven como texto ISO-8859-1.
    # ``genfromtxt`` permite descartar alguna línea mal formada sin perder el
    # resto del registro oficial.
    datos = np.genfromtxt(
        ruta,
        dtype=float,
        encoding="latin-1",
        invalid_raise=False,
        usecols=(0, 1),
    )
    datos = datos[np.isfinite(datos).all(axis=1)]
    if datos.ndim != 2 or datos.shape[1] < 2:
        raise ValueError("El archivo PhysioNet debe contener tiempo y amplitud.")
    t = datos[:, 0]
    x = datos[:, 1]
    fs = 1.0 / float(np.median(np.diff(t)))
    return t - t[0], x, fs


def _sos_filtro(tipo: str, corte: float | tuple[float, float], fs: float, orden: int = 4):
    return signal.butter(orden, corte, btype=tipo, fs=fs, output="sos")


def _filtfilt_seguro(sos: np.ndarray, x: np.ndarray) -> np.ndarray:
    try:
        return signal.sosfiltfilt(sos, x)
    except ValueError:
        return signal.sosfilt(sos, x)


def procesar_emg(
    t: np.ndarray,
    x: np.ndarray,
    fs: float,
    configuracion: ProcessingConfig,
) -> dict[str, np.ndarray | float | dict[str, float]]:
    if fs <= 0:
        raise ValueError("La frecuencia de muestreo debe ser positiva.")
    if len(x) != len(t):
        raise ValueError("Tiempo y señal deben tener la misma longitud.")

    x = np.asarray(x, dtype=float)
    centrada = x - np.nanmedian(x)
    nyquist = fs / 2.0

    hp = max(0.0, float(configuracion.highpass_hz))
    lp = min(float(configuracion.lowpass_hz), 0.90 * nyquist)
    if configuracion.lowpass_hz >= 0.40 * fs:
        warnings.warn(
            "La frecuencia pasa-bajas está muy próxima a Nyquist. "
            "Interprete el espectro con cautela y revise el filtrado antialias analógico.",
            RuntimeWarning,
        )
    if hp > 0 and lp > hp and len(x) >= 16:
        filtrada = _filtfilt_seguro(_sos_filtro("bandpass", (hp, lp), fs), centrada)
    elif lp > 0 and len(x) >= 16:
        filtrada = _filtfilt_seguro(_sos_filtro("lowpass", lp, fs), centrada)
    else:
        filtrada = centrada.copy()

    if configuracion.notch_hz and configuracion.notch_hz < 0.45 * fs:
        b, a = signal.iirnotch(float(configuracion.notch_hz), Q=30.0, fs=fs)
        try:
            filtrada = signal.filtfilt(b, a, filtrada)
        except ValueError:
            filtrada = signal.lfilter(b, a, filtrada)

    rectificada = np.abs(filtrada)
    corte_env = min(float(configuracion.envelope_hz), 0.20 * nyquist)
    if corte_env > 0 and len(x) >= 16:
        envolvente = _filtfilt_seguro(_sos_filtro("lowpass", corte_env, fs), rectificada)
        envolvente = np.maximum(envolvente, 0.0)
    else:
        envolvente = rectificada.copy()

    ventana = max(1, int(round(configuracion.rms_window_ms * fs / 1000.0)))
    kernel = np.ones(ventana, dtype=float) / ventana
    rms_movil = np.sqrt(np.convolve(filtrada**2, kernel, mode="same"))

    nperseg = min(len(filtrada), max(256, int(round(fs))))
    f, psd = signal.welch(filtrada, fs=fs, nperseg=nperseg, detrend="constant")

    power_low = max(0.0, configuracion.power_low_hz)
    power_high = min(configuracion.power_high_hz, f[-1])
    mascara = (f >= power_low) & (f <= power_high)
    if not np.any(mascara):
        mascara = np.ones_like(f, dtype=bool)
    f_banda = f[mascara]
    psd_banda = psd[mascara]
    potencia_espectral = (
        float(trapezoid(psd_banda, f_banda)) if len(f_banda) > 1 else 0.0
    )

    if potencia_espectral > 0 and len(f_banda) > 1:
        frecuencia_media = float(
            trapezoid(f_banda * psd_banda, f_banda) / potencia_espectral
        )
        df = np.diff(f_banda, prepend=f_banda[0])
        acumulada = np.cumsum(psd_banda * df)
        frecuencia_mediana = float(f_banda[np.searchsorted(acumulada, acumulada[-1] / 2.0)])
    else:
        frecuencia_media = math.nan
        frecuencia_mediana = math.nan

    umbral_cruce = 0.01 * float(np.std(filtrada))
    cruces = np.sum(
        ((filtrada[:-1] >= 0) & (filtrada[1:] < 0))
        | ((filtrada[:-1] < 0) & (filtrada[1:] >= 0))
    )
    if umbral_cruce > 0:
        cambios = np.abs(np.diff(filtrada))
        cruces = int(np.sum(
            (((filtrada[:-1] >= 0) & (filtrada[1:] < 0))
             | ((filtrada[:-1] < 0) & (filtrada[1:] >= 0)))
            & (cambios >= umbral_cruce)
        ))

    metricas = {
        "fs_hz": float(fs),
        "duracion_s": float(t[-1] - t[0]),
        "muestras": int(len(x)),
        "rms": float(np.sqrt(np.mean(filtrada**2))),
        "mav": float(np.mean(rectificada)),
        "iemg": float(trapezoid(rectificada, t)),
        "pico_a_pico": float(np.ptp(filtrada)),
        "desviacion_estandar": float(np.std(filtrada, ddof=1)),
        "longitud_forma_onda": float(np.sum(np.abs(np.diff(filtrada)))),
        "cruces_por_cero": int(cruces),
        "potencia_espectral_banda": potencia_espectral,
        "banda_potencia_inferior_hz": float(power_low),
        "banda_potencia_superior_hz": float(power_high),
        "frecuencia_media_hz": frecuencia_media,
        "frecuencia_mediana_hz": frecuencia_mediana,
    }

    return {
        "tiempo": t,
        "cruda": x,
        "centrada": centrada,
        "filtrada": filtrada,
        "rectificada": rectificada,
        "envolvente": envolvente,
        "rms_movil": rms_movil,
        "frecuencia": f,
        "psd": psd,
        "metricas": metricas,
    }


def guardar_resultados(
    resultados: dict[str, Any],
    directorio: str | Path,
    nombre: str,
    metadatos: dict[str, Any],
    configuracion: ProcessingConfig,
) -> dict[str, Path]:
    directorio = Path(directorio)
    directorio.mkdir(parents=True, exist_ok=True)
    base = re.sub(r"[^A-Za-z0-9_.-]+", "_", nombre).strip("_") or "registro"

    tabla = pd.DataFrame({
        "tiempo_s": resultados["tiempo"],
        "senal_cruda": resultados["cruda"],
        "senal_filtrada": resultados["filtrada"],
        "rectificada": resultados["rectificada"],
        "envolvente": resultados["envolvente"],
        "rms_movil": resultados["rms_movil"],
    })
    ruta_procesada = directorio / f"{base}_procesada.csv"
    tabla.to_csv(ruta_procesada, index=False)

    metricas = dict(resultados["metricas"])
    metricas.update(metadatos)
    metricas["procesamiento"] = asdict(configuracion)
    ruta_metricas = directorio / f"{base}_metricas.json"
    ruta_metricas.write_text(json.dumps(metricas, indent=2, ensure_ascii=False), encoding="utf-8")

    ruta_resumen = directorio / f"{base}_resumen.csv"
    resumen_plano = {
        k: v for k, v in metricas.items()
        if not isinstance(v, (dict, list, tuple))
    }
    pd.DataFrame([resumen_plano]).to_csv(ruta_resumen, index=False)

    unidad = str(metadatos.get("unidad_senal", "unidad de entrada"))
    fig, ejes = plt.subplots(3, 1, figsize=(10, 8), constrained_layout=True)
    t = resultados["tiempo"]
    ejes[0].plot(t, resultados["cruda"], lw=0.7, label="Cruda", alpha=0.7)
    ejes[0].plot(t, resultados["filtrada"], lw=0.8, label="Filtrada")
    ejes[0].set(xlabel="Tiempo [s]", ylabel=f"Amplitud [{unidad}]", title="Señal EMG")
    ejes[0].legend(loc="upper right")
    ejes[0].grid(alpha=0.25)

    ejes[1].plot(t, resultados["rectificada"], lw=0.5, label="Rectificada", alpha=0.5)
    ejes[1].plot(t, resultados["envolvente"], lw=1.2, label="Envolvente")
    ejes[1].plot(t, resultados["rms_movil"], lw=1.0, label="RMS móvil")
    ejes[1].set(
        xlabel="Tiempo [s]",
        ylabel=f"Amplitud [{unidad}]",
        title="Actividad temporal",
    )
    ejes[1].legend(loc="upper right")
    ejes[1].grid(alpha=0.25)

    f = resultados["frecuencia"]
    psd = resultados["psd"]
    ejes[2].semilogy(f, np.maximum(psd, np.finfo(float).tiny), lw=1.0)
    ejes[2].set(
        xlabel="Frecuencia [Hz]",
        ylabel=f"PSD [{unidad}²/Hz]",
        title="Densidad espectral de potencia",
    )
    ejes[2].set_xlim(0, min(float(f[-1]), configuracion.power_high_hz * 1.1))
    ejes[2].grid(alpha=0.25)

    ruta_figura = directorio / f"{base}_analisis.png"
    fig.savefig(ruta_figura, dpi=180)
    plt.close(fig)

    ruta_psd = directorio / f"{base}_psd.csv"
    pd.DataFrame({"frecuencia_hz": f, "psd": psd}).to_csv(ruta_psd, index=False)

    return {
        "procesada": ruta_procesada,
        "metricas": ruta_metricas,
        "resumen": ruta_resumen,
        "figura": ruta_figura,
        "psd": ruta_psd,
    }
