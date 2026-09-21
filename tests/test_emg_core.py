from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))

from emg_core import ProcessingConfig, cargar_csv_emg, guardar_resultados, procesar_emg


class TestEmgCore(unittest.TestCase):
    def test_carga_y_metricas(self):
        fs = 2000.0
        t = np.arange(0.0, 2.0, 1.0 / fs)
        x = 0.3 * np.sin(2 * np.pi * 80.0 * t) + 0.05 * np.sin(2 * np.pi * 60.0 * t)
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "registro.csv"
            pd.DataFrame({"tiempo_s": t, "emg_mV": x}).to_csv(ruta, index=False)
            tc, xc, fsc, meta = cargar_csv_emg(ruta)
            self.assertAlmostEqual(fsc, fs, places=5)
            self.assertEqual(len(tc), len(xc))
            self.assertEqual(meta["columna_senal"], "emg_mV")

            config = ProcessingConfig(lowpass_hz=400.0)
            resultado = procesar_emg(tc, xc, fsc, config)
            self.assertGreater(resultado["metricas"]["rms"], 0)
            self.assertGreater(resultado["metricas"]["potencia_espectral_banda"], 0)
            self.assertAlmostEqual(resultado["metricas"]["frecuencia_mediana_hz"], 80.0, delta=5.0)

            rutas = guardar_resultados(resultado, Path(tmp) / "salida", "prueba", meta, config)
            for salida in rutas.values():
                self.assertTrue(salida.exists())


if __name__ == "__main__":
    unittest.main()
