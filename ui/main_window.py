
# ui/main_window.py

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QFileDialog,
    QSplitter,
)

from models import (
    MeasurementConfig,
)

from audio import (
    AudioDeviceManager,
)

from workers import (
    WorkerManager,
)

from dsp import (
    ExportHelper,
)

from ui.widgets import (
    DeviceSelectorWidget,
    MeasurementConfigWidget,
    ControlWidget,
    StatusWidget,
    LogWidget,
)

from ui.plots import (
    PlotPanel,
)


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.worker_manager = WorkerManager()

        self.current_result = None

        self.devices_input = []
        self.devices_output = []

        self.setup_ui()
        self.connect_signals()
        self.load_devices()

    # =========================================================
    # UI
    # =========================================================

    def setup_ui(self):

        self.setWindowTitle(
            "Audio Analyzer"
        )

        self.resize(
            1200,
            800
        )

        central = QWidget()

        self.setCentralWidget(
            central
        )

        main_layout = QVBoxLayout(
            central
        )

        splitter = QSplitter(
            Qt.Horizontal
        )

        main_layout.addWidget(
            splitter
        )

        # =====================================================
        # LEFT PANEL
        # =====================================================

        left_panel = QWidget()

        left_layout = QVBoxLayout(
            left_panel
        )

        self.device_widget = (
            DeviceSelectorWidget()
        )

        self.config_widget = (
            MeasurementConfigWidget()
        )

        self.control_widget = (
            ControlWidget()
        )

        self.status_widget = (
            StatusWidget()
        )

        self.log_widget = (
            LogWidget()
        )

        left_layout.addWidget(
            self.device_widget
        )

        left_layout.addWidget(
            self.config_widget
        )

        left_layout.addWidget(
            self.control_widget
        )

        left_layout.addWidget(
            self.status_widget
        )

        left_layout.addWidget(
            self.log_widget
        )

        # =====================================================
        # RIGHT PANEL
        # =====================================================

        self.plots = PlotPanel()

        splitter.addWidget(
            left_panel
        )

        splitter.addWidget(
            self.plots
        )

        splitter.setSizes(
            [
                350,
                1250
            ]
        )

        self.statusBar().showMessage(
            "Prêt"
        )

    # =========================================================
    # SIGNALS
    # =========================================================

    def connect_signals(self):

        self.control_widget.start_requested.connect(
            self.start_measurement
        )

        self.control_widget.stop_requested.connect(
            self.stop_measurement
        )

        self.control_widget.export_requested.connect(
            self.export_csv
        )

        self.worker_manager.progress.connect(
            self.on_progress
        )

        self.worker_manager.status.connect(
            self.on_status
        )

        self.worker_manager.error.connect(
            self.on_error
        )

        self.worker_manager.result_ready.connect(
            self.on_result
        )

        self.worker_manager.measurement_ready.connect(
            self.on_measurement_ready
        )

        self.worker_manager.acquisition_finished.connect(
            self.on_acquisition_finished
        )

        self.worker_manager.analysis_finished.connect(
            self.on_analysis_finished
        )

    # =========================================================
    # DEVICES
    # =========================================================

    def load_devices(self):

        self.devices_input = (
            AudioDeviceManager.get_input_devices()
        )

        self.devices_output = (
            AudioDeviceManager.get_output_devices()
        )

        for device in self.devices_input:

            self.device_widget.add_input_device(
                device.name,
                device.index
            )

        for device in self.devices_output:

            self.device_widget.add_output_device(
                device.name,
                device.index
            )

        self.log_widget.append(
            f"{len(self.devices_input)} entrées détectées"
        )

        self.log_widget.append(
            f"{len(self.devices_output)} sorties détectées"
        )

    # =========================================================
    # CONFIGURATION
    # =========================================================

    def create_config(self):

        return MeasurementConfig(

            samplerate=
            self.config_widget.samplerate,

            duration=
            self.config_widget.duration,

            amplitude=
            self.config_widget.amplitude,

            signal_type=
            self.config_widget.signal_type,

            input_device=
            self.device_widget.input_device,

            output_device=
            self.device_widget.output_device,
        )

    # =========================================================
    # ACQUISITION
    # =========================================================

    def start_measurement(self):

        self.current_result = None

        print(
            "\n----- DEBUG -----"
        )

        print(
            "acq thread =",
            self.worker_manager.acquisition_thread
        )

        print(
            "analysis thread =",
            self.worker_manager.analysis_thread
        )

        print(
            "running =",
            self.worker_manager.is_running()
        )

        if self.worker_manager.is_running():

            QMessageBox.warning(
                self,
                "Mesure en cours",
                "Une mesure est déjà en cours."
            )

            return

        try:

            config = self.create_config()

            self.status_widget.set_progress(
                0
            )

            self.status_widget.set_status(
                "Acquisition..."
            )

            self.log_widget.append(
                "----------"
            )

            self.log_widget.append(
                "Nouvelle mesure"
            )

            self.log_widget.append(
                f"Signal : {config.signal_type.value}"
            )

            self.log_widget.append(
                f"Durée : {config.duration:.1f} s"
            )

            self.log_widget.append(
                f"Fréquence : {config.samplerate} Hz"
            )

            self.control_widget.btn_start.setEnabled(
                False
            )

            self.control_widget.btn_export.setEnabled(
                False
            )

            self.plots.clear()

            self.worker_manager.start_acquisition(
                config
            )

        except Exception as ex:

            QMessageBox.critical(
                self,
                "Erreur",
                str(ex)
            )

    # =========================================================

    def stop_measurement(self):

        self.worker_manager.stop_all()

        self.status_widget.set_status(
            "Arrêt demandé"
        )

        self.log_widget.append(
            "Arrêt demandé"
        )

        self.control_widget.btn_start.setEnabled(
            True
        )

    # =========================================================
    # CALLBACKS
    # =========================================================

    def on_progress(self, info):

        self.status_widget.set_progress(
            info.percent
        )

    # =========================================================

    def on_status(self, message):

        self.status_widget.set_status(
            message
        )

        self.statusBar().showMessage(
            message
        )

        self.log_widget.append(
            message
        )

    # =========================================================

    def on_measurement_ready(
        self,
        measurement
    ):

        self.log_widget.append(
            "Données acquises"
        )

    # =========================================================

    def on_result(
        self,
        result
    ):

        self.current_result = result

        self.plots.update_result(
            result
        )

        self.control_widget.btn_export.setEnabled(
            True
        )

        self.status_widget.set_progress(
            100
        )

        self.status_widget.set_status(
            "Analyse terminée"
        )

        self.control_widget.btn_start.setEnabled(
            True
        )

        self.log_widget.append(
            "Analyse terminée"
        )

    # =========================================================

    def on_error(self, error):

        QMessageBox.critical(
            self,
            error.title,
            error.message
        )

        self.log_widget.append(
            "ERREUR:"
        )

        self.log_widget.append(
            error.traceback_text
        )

        self.control_widget.btn_start.setEnabled(
            True
        )

    # =========================================================

    def on_acquisition_finished(self):

        self.log_widget.append(
            "Thread acquisition terminé"
        )

        self.control_widget.btn_start.setEnabled(
            True
        )

    # =========================================================

    def on_analysis_finished(self):

        self.log_widget.append(
            "Thread analyse terminé"
        )

        self.control_widget.btn_start.setEnabled(
            True
        )

    # =========================================================
    # EXPORT
    # =========================================================

    def export_csv(self):

        if self.current_result is None:
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter Bode CSV",
            str(
                Path.home()
                / "bode.csv"
            ),
            "CSV Files (*.csv)"
        )

        if not filename:
            return

        try:

            ExportHelper.bode_to_csv(
                self.current_result,
                filename
            )

            QMessageBox.information(
                self,
                "Export",
                "Export CSV réussi."
            )

            self.log_widget.append(
                f"Export CSV : {filename}"
            )

        except Exception as ex:

            QMessageBox.critical(
                self,
                "Erreur export",
                str(ex)
            )

    # =========================================================
    # FERMETURE
    # =========================================================

    def closeEvent(self, event):

        try:

            self.worker_manager.stop_all()

        except Exception:
            pass

        event.accept()
