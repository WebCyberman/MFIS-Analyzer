# workers.py

from __future__ import annotations

import traceback

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
    QThread,
)

from audio import AudioRecorder
from dsp import MeasurementAnalyzer

from models import (
    MeasurementConfig,
    MeasurementData,
    AnalysisResult,
    ProgressInfo,
    ErrorInfo,
)


# ============================================================
# ACQUISITION WORKER
# ============================================================

class AcquisitionWorker(QObject):

    finished = Signal()

    progress = Signal(object)
    status = Signal(str)

    measurement_ready = Signal(object)
    error = Signal(object)

    def __init__(
        self,
        config: MeasurementConfig,
    ):
        super().__init__()

        self.config = config

        self.recorder = AudioRecorder()

        self._stop_requested = False

    # --------------------------------------------------------

    def stop(self):

        self._stop_requested = True

        self.recorder.stop()

    # --------------------------------------------------------

    @Slot()
    def run(self):

        try:

            self.status.emit(
                "Acquisition en cours..."
            )

            measurement = (
                self.recorder.record_measurement(
                    config=self.config,
                    progress_callback=
                    self._report_progress,
                )
            )

            if self._stop_requested:

                return

            self.measurement_ready.emit(
                measurement
            )

            self.status.emit(
                "Acquisition terminée"
            )

        except Exception:

            tb = traceback.format_exc()

            self.error.emit(
                ErrorInfo(
                    title="Erreur d'acquisition",
                    message=tb.splitlines()[-1],
                    traceback_text=tb,
                )
            )

        finally:

            self.status.emit(

                "Thread acquisition terminé"

            )

            self.finished.emit()

    # --------------------------------------------------------

    def _report_progress(
        self,
        percent: int
    ):

        self.progress.emit(
            ProgressInfo(
                percent=percent,
                current_step="Acquisition",
                message=f"{percent}%"
            )
        )


# ============================================================
# ANALYSIS WORKER
# ============================================================

class AnalysisWorker(QObject):

    finished = Signal()

    progress = Signal(object)
    status = Signal(str)

    result_ready = Signal(object)
    error = Signal(object)

    def __init__(
        self,
        measurement: MeasurementData,
    ):
        super().__init__()

        self.measurement = measurement

        self._stop_requested = False

    # --------------------------------------------------------

    def stop(self):

        self._stop_requested = True

    # --------------------------------------------------------

    @Slot()
    def run(self):

        try:

            self.status.emit(
                "Analyse fréquentielle..."
            )

            self.progress.emit(
                ProgressInfo(
                    percent=10,
                    current_step="Analyse",
                    message="FFT"
                )
            )

            result = (
                MeasurementAnalyzer.analyze(
                    self.measurement
                )
            )

            if self._stop_requested:

                return

            self.progress.emit(
                ProgressInfo(
                    percent=100,
                    current_step="Analyse",
                    message="Terminé"
                )
            )

            self.result_ready.emit(
                result
            )

            self.status.emit(
                "Analyse terminée"
            )

        except Exception:

            tb = traceback.format_exc()

            self.error.emit(
                ErrorInfo(
                    title="Erreur d'analyse",
                    message=tb.splitlines()[-1],
                    traceback_text=tb,
                )
            )

        finally:

            self.status.emit(

                "Thread analyse terminé"

            )

            self.finished.emit()

# ============================================================
# WORKER MANAGER
# ============================================================

class WorkerManager(QObject):

    progress = Signal(object)
    status = Signal(str)

    error = Signal(object)

    measurement_ready = Signal(object)

    result_ready = Signal(object)

    acquisition_finished = Signal()

    analysis_finished = Signal()

    def __init__(self):

        super().__init__()

        self.acquisition_thread = None
        self.analysis_thread = None

        self.acquisition_worker = None
        self.analysis_worker = None

    # --------------------------------------------------------

    def is_running(self):

        acquisition_running = False
        analysis_running = False

        try:

            if self.acquisition_thread is not None:
                acquisition_running = (
                    self.acquisition_thread.isRunning()
                )

        except RuntimeError:

            self.acquisition_thread = None
            self.acquisition_worker = None

        try:

            if self.analysis_thread is not None:
                analysis_running = (
                    self.analysis_thread.isRunning()
                )

        except RuntimeError:

            self.analysis_thread = None
            self.analysis_worker = None

        return (
                acquisition_running
                or
                analysis_running
        )

    # --------------------------------------------------------

    def start_acquisition(
        self,
        config: MeasurementConfig,
    ):

        if self.acquisition_thread is not None:
            return

        self.stop_all()

        self.acquisition_thread = QThread()

        self.acquisition_worker = (
            AcquisitionWorker(
                config
            )
        )

        self.acquisition_worker.moveToThread(
            self.acquisition_thread
        )

        self.acquisition_thread.started.connect(
            self.acquisition_worker.run
        )

        self.acquisition_worker.progress.connect(
            self.progress.emit
        )

        self.acquisition_worker.status.connect(
            self.status.emit
        )

        self.acquisition_worker.error.connect(
            self.error.emit
        )

        self.acquisition_worker.measurement_ready.connect(
            self._on_measurement_ready
        )

        self.acquisition_worker.finished.connect(
            self.acquisition_thread.quit
        )

        self.acquisition_worker.finished.connect(
            self.acquisition_finished.emit
        )

        self.acquisition_thread.finished.connect(
            self._cleanup_acquisition_thread
        )

        self.acquisition_thread.start()

    # --------------------------------------------------------

    def _on_measurement_ready(
        self,
        measurement
    ):

        self.measurement_ready.emit(
            measurement
        )

        self.start_analysis(
            measurement
        )

    # --------------------------------------------------------

    def start_analysis(
        self,
        measurement
    ):

        if (
                self.analysis_thread is not None
        ):
            return

        self.analysis_thread = QThread()

        self.analysis_worker = (
            AnalysisWorker(
                measurement
            )
        )

        self.analysis_worker.moveToThread(
            self.analysis_thread
        )

        self.analysis_thread.started.connect(
            self.analysis_worker.run
        )

        self.analysis_worker.progress.connect(
            self.progress.emit
        )

        self.analysis_worker.status.connect(
            self.status.emit
        )

        self.analysis_worker.error.connect(
            self.error.emit
        )

        self.analysis_worker.result_ready.connect(
            self.result_ready.emit
        )

        self.analysis_worker.finished.connect(
            self.analysis_thread.quit
        )

        self.analysis_worker.finished.connect(
            self.analysis_finished.emit
        )

        self.analysis_thread.finished.connect(
            self._cleanup_analysis_thread
        )

        self.analysis_thread.start()

    # --------------------------------------------------------

    def _cleanup_acquisition_thread(self):

        print("Cleanup acquisition")

        try:
            if self.acquisition_thread:
                self.acquisition_thread.deleteLater()
        except RuntimeError:
            pass

        self.acquisition_thread = None
        self.acquisition_worker = None

        self.acquisition_finished.emit()

    # --------------------------------------------------------

    def _cleanup_analysis_thread(self):

        print("Cleanup analyse")

        try:
            if self.analysis_thread:
                self.analysis_thread.deleteLater()
        except RuntimeError:
            pass

        self.analysis_thread = None
        self.analysis_worker = None

        self.analysis_finished.emit()

    # --------------------------------------------------------

    def stop_all(self):

        if self.acquisition_worker:
            self.acquisition_worker.stop()

        if self.analysis_worker:
            self.analysis_worker.stop()

        self.acquisition_worker = None
        self.analysis_worker = None
