
from __future__ import annotations

from PySide6.QtCore import Signal

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QProgressBar,
    QTextEdit,
    QGroupBox,
)

from models import SignalType


# ============================================================
# DEVICE SELECTOR
# ============================================================

class DeviceSelectorWidget(QGroupBox):

    def __init__(self, parent=None):

        super().__init__(
            "Périphériques Audio",
            parent
        )

        self.cmb_input = QComboBox()
        self.cmb_output = QComboBox()

        layout = QGridLayout()

        layout.addWidget(
            QLabel("Entrée"),
            0,
            0
        )

        layout.addWidget(
            self.cmb_input,
            0,
            1
        )

        layout.addWidget(
            QLabel("Sortie"),
            1,
            0
        )

        layout.addWidget(
            self.cmb_output,
            1,
            1
        )

        self.setLayout(layout)

    # -------------------------------------

    def add_input_device(
        self,
        name,
        index
    ):
        self.cmb_input.addItem(
            name,
            index
        )

    # -------------------------------------

    def add_output_device(
        self,
        name,
        index
    ):
        self.cmb_output.addItem(
            name,
            index
        )

    # -------------------------------------

    @property
    def input_device(self):

        return self.cmb_input.currentData()

    # -------------------------------------

    @property
    def output_device(self):

        return self.cmb_output.currentData()


# ============================================================
# CONFIGURATION WIDGET
# ============================================================

class MeasurementConfigWidget(QGroupBox):

    def __init__(self, parent=None):

        super().__init__(
            "Configuration",
            parent
        )

        self.cmb_signal = QComboBox()

        self.cmb_signal.addItem(
            "Log Sweep",
            SignalType.LOG_SWEEP
        )

        self.cmb_signal.addItem(
            "White Noise",
            SignalType.WHITE_NOISE
        )

        self.cmb_signal.addItem(
            "Pink Noise",
            SignalType.PINK_NOISE
        )

        self.spin_samplerate = QSpinBox()

        self.spin_samplerate.setRange(
            8000,
            384000
        )

        self.spin_samplerate.setValue(
            48000
        )

        self.spin_duration = (
            QDoubleSpinBox()
        )

        self.spin_duration.setRange(
            0.1,
            60.0
        )

        self.spin_duration.setValue(
            5.0
        )

        self.spin_duration.setDecimals(
            1
        )

        self.spin_amplitude = (
            QDoubleSpinBox()
        )

        self.spin_amplitude.setRange(
            0.01,
            1.0
        )

        self.spin_amplitude.setValue(
            0.7
        )

        self.spin_amplitude.setSingleStep(
            0.05
        )

        layout = QGridLayout()

        layout.addWidget(
            QLabel("Signal"),
            0,
            0
        )

        layout.addWidget(
            self.cmb_signal,
            0,
            1
        )

        layout.addWidget(
            QLabel("Fréquence"),
            1,
            0
        )

        layout.addWidget(
            self.spin_samplerate,
            1,
            1
        )

        layout.addWidget(
            QLabel("Durée"),
            2,
            0
        )

        layout.addWidget(
            self.spin_duration,
            2,
            1
        )

        layout.addWidget(
            QLabel("Amplitude"),
            3,
            0
        )

        layout.addWidget(
            self.spin_amplitude,
            3,
            1
        )

        self.setLayout(layout)

    # -------------------------------------

    @property
    def samplerate(self):
        return self.spin_samplerate.value()

    # -------------------------------------

    @property
    def duration(self):
        return self.spin_duration.value()

    # -------------------------------------

    @property
    def amplitude(self):
        return self.spin_amplitude.value()

    # -------------------------------------

    @property
    def signal_type(self):
        return self.cmb_signal.currentData()


# ============================================================
# CONTROL WIDGET
# ============================================================

class ControlWidget(QGroupBox):

    start_requested = Signal()
    stop_requested = Signal()
    export_requested = Signal()

    def __init__(self, parent=None):

        super().__init__(
            "Contrôles",
            parent
        )

        self.btn_start = QPushButton(
            "▶ Lancer"
        )

        self.btn_stop = QPushButton(
            "■ Stop"
        )

        self.btn_export = QPushButton(
            "💾 Export CSV"
        )

        self.btn_export.setEnabled(
            False
        )

        layout = QVBoxLayout()

        layout.addWidget(
            self.btn_start
        )

        layout.addWidget(
            self.btn_stop
        )

        layout.addWidget(
            self.btn_export
        )

        self.setLayout(layout)

        self.btn_start.clicked.connect(
            self.start_requested
        )

        self.btn_stop.clicked.connect(
            self.stop_requested
        )

        self.btn_export.clicked.connect(
            self.export_requested
        )


# ============================================================
# STATUS WIDGET
# ============================================================

class StatusWidget(QGroupBox):

    def __init__(self, parent=None):

        super().__init__(
            "Etat",
            parent
        )

        self.progress = QProgressBar()

        self.status = QLabel(
            "Prêt"
        )

        layout = QVBoxLayout()

        layout.addWidget(
            self.progress
        )

        layout.addWidget(
            self.status
        )

        self.setLayout(layout)

    # -------------------------------------

    def set_progress(
        self,
        value
    ):
        self.progress.setValue(
            value
        )

    # -------------------------------------

    def set_status(
        self,
        message
    ):
        self.status.setText(
            message
        )


# ============================================================
# LOG WIDGET
# ============================================================

class LogWidget(QGroupBox):

    def __init__(self, parent=None):

        super().__init__(
            "Journal",
            parent
        )

        self.text = QTextEdit()

        self.text.setReadOnly(
            True
        )

        layout = QVBoxLayout()

        layout.addWidget(
            self.text
        )

        self.setLayout(layout)

    # -------------------------------------

    def append(
        self,
        text
    ):

        self.text.append(
            text
        )

    # -------------------------------------

    def clear(self):

        self.text.clear()
