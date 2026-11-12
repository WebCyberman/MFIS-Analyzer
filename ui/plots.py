
from __future__ import annotations

import numpy as np
import pyqtgraph as pg

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
)

from PySide6.QtCore import Qt

from models import AnalysisResult


# ============================================================
# STYLE
# ============================================================

pg.setConfigOptions(
    antialias=True,
    background="#202020",
    foreground="#DDDDDD",
)


# ============================================================
# BASE PLOT
# ============================================================

class BasePlot(pg.PlotWidget):

    def __init__(
        self,
        title: str,
        x_label: str,
        y_label: str,
        parent=None,
    ):
        super().__init__(parent)

        self.setTitle(title)

        self.setLabel(
            "bottom",
            x_label
        )

        self.setLabel(
            "left",
            y_label
        )

        self.showGrid(
            x=True,
            y=True,
            alpha=0.3,
        )

        self.enableAutoRange()

        self.addLegend()

        self.setMenuEnabled(True)

        self.setMouseEnabled(
            x=True,
            y=True,
        )


# ============================================================
# FFT
# ============================================================

class FFTPlot(BasePlot):

    def __init__(self):

        super().__init__(
            "FFT",
            "Fréquence (Hz)",
            "Amplitude"
        )

        self.stimulus_curve = self.plot(
            pen=pg.mkPen(
                "#00BFFF",
                width=1,
            ),
            name="Stimulus",
        )

        self.response_curve = self.plot(
            pen=pg.mkPen(
                "#FFAA00",
                width=1,
            ),
            name="Réponse",
        )

        self.setLogMode(
            x=True,
            y=False,
        )

    def update_result(
        self,
        result: AnalysisResult,
    ):

        freqs = result.fft.frequencies

        stimulus = np.abs(
            result.fft.stimulus_fft
        )

        response = np.abs(
            result.fft.response_fft
        )

        valid = freqs > 0

        self.stimulus_curve.setData(
            freqs[valid],
            stimulus[valid],
        )

        self.response_curve.setData(
            freqs[valid],
            response[valid],
        )


# ============================================================
# BODE MAGNITUDE
# ============================================================

class BodeMagnitudePlot(BasePlot):

    def __init__(self):

        super().__init__(
            "Bode Amplitude",
            "Fréquence (Hz)",
            "Amplitude (dB)"
        )

        self.curve = self.plot(
            pen=pg.mkPen(
                "#00FF88",
                width=2,
            ),
            name="Amplitude"
        )

        self.setLogMode(
            x=True,
            y=False,
        )

    def update_result(
        self,
        result: AnalysisResult,
    ):

        freqs = result.bode.frequencies

        valid = freqs > 0

        self.curve.setData(
            freqs[valid],
            result.bode.amplitude_db[
                valid
            ],
        )


# ============================================================
# BODE PHASE
# ============================================================

class BodePhasePlot(BasePlot):

    def __init__(self):

        super().__init__(
            "Bode Phase",
            "Fréquence (Hz)",
            "Phase (°)"
        )

        self.curve = self.plot(
            pen=pg.mkPen(
                "#FFD000",
                width=2,
            ),
            name="Phase"
        )

        self.setLogMode(
            x=True,
            y=False,
        )

    def update_result(
        self,
        result: AnalysisResult,
    ):

        freqs = result.bode.frequencies

        valid = freqs > 0

        self.curve.setData(
            freqs[valid],
            result.bode.phase_deg[
                valid
            ],
        )


# ============================================================
# NYQUIST
# ============================================================

class NyquistPlot(BasePlot):

    def __init__(self):

        super().__init__(
            "Nyquist",
            "Réel",
            "Imaginaire"
        )

        self.curve = self.plot(
            pen=None,
            symbol="o",
            symbolSize=4,
            symbolBrush="#00AAFF",
        )

    def update_result(
        self,
        result: AnalysisResult,
    ):

        self.curve.setData(

            result.nyquist.real,

            result.nyquist.imag,
        )


# ============================================================
# MAIN PLOT WIDGET
# ============================================================

class PlotPanel(QWidget):

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        self.fft_plot = FFTPlot()

        self.bode_mag_plot = (
            BodeMagnitudePlot()
        )

        self.bode_phase_plot = (
            BodePhasePlot()
        )

        self.nyquist_plot = (
            NyquistPlot()
        )

        splitter = QSplitter(
            Qt.Vertical
        )

        splitter.addWidget(
            self.fft_plot
        )

        splitter.addWidget(
            self.bode_mag_plot
        )

        splitter.addWidget(
            self.bode_phase_plot
        )

        splitter.addWidget(
            self.nyquist_plot
        )

        splitter.setSizes(
            [
                250,
                250,
                250,
                250,
            ]
        )

        layout = QVBoxLayout()

        layout.addWidget(
            splitter
        )

        self.setLayout(
            layout
        )

    # ------------------------------------------------

    def clear(self):
        self.fft_plot.stimulus_curve.setData([], [])
        self.fft_plot.response_curve.setData([], [])

        self.bode_mag_plot.curve.setData([], [])
        self.bode_phase_plot.curve.setData([], [])

        self.nyquist_plot.curve.setData([], [])

    # ------------------------------------------------

    def update_result(
        self,
        result: AnalysisResult,
    ):

        self.fft_plot.update_result(
            result
        )

        self.bode_mag_plot.update_result(
            result
        )

        self.bode_phase_plot.update_result(
            result
        )

        self.nyquist_plot.update_result(
            result
        )
