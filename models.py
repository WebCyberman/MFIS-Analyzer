# models.py

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np


# ============================================================
# TYPES DE SIGNAL
# ============================================================

class SignalType(Enum):
    LOG_SWEEP = "Log Sweep"
    WHITE_NOISE = "White Noise"
    PINK_NOISE = "Pink Noise"


# ============================================================
# ETAT APPLICATION
# ============================================================

class AnalysisState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    FINISHED = "finished"


# ============================================================
# PERIPHERIQUE AUDIO
# ============================================================

@dataclass
class AudioDevice:
    index: int
    name: str
    max_input_channels: int = 0
    max_output_channels: int = 0
    default_samplerate: float = 48000.0

    @property
    def is_input(self) -> bool:
        return self.max_input_channels > 0

    @property
    def is_output(self) -> bool:
        return self.max_output_channels > 0


# ============================================================
# CONFIGURATION DE MESURE
# ============================================================

@dataclass
class MeasurementConfig:

    samplerate: int = 48000

    duration: float = 5.0

    amplitude: float = 0.7

    sweep_start_hz: float = 20.0

    sweep_stop_hz: float = 20000.0

    signal_type: SignalType = SignalType.LOG_SWEEP

    input_device: Optional[int] = None

    output_device: Optional[int] = None

    fft_size: Optional[int] = None

    smoothing_window: int = 101

    smoothing_polyorder: int = 3


# ============================================================
# DONNEES BRUTES ACQUISES
# ============================================================

@dataclass
class MeasurementData:

    stimulus: np.ndarray

    response: np.ndarray

    samplerate: int

    duration: float

    timestamp: str = ""

    metadata: dict = field(default_factory=dict)

    @property
    def sample_count(self) -> int:
        return len(self.response)


# ============================================================
# RESULTATS FFT
# ============================================================

@dataclass
class FFTResult:

    frequencies: np.ndarray

    stimulus_fft: np.ndarray

    response_fft: np.ndarray

    transfer_function: np.ndarray

    @property
    def magnitude(self) -> np.ndarray:
        return np.abs(self.transfer_function)

    @property
    def phase_rad(self) -> np.ndarray:
        return np.angle(self.transfer_function)

    @property
    def phase_deg(self) -> np.ndarray:
        return np.degrees(self.phase_rad)


# ============================================================
# RESULTATS BODE
# ============================================================

@dataclass
class BodeResult:

    frequencies: np.ndarray

    amplitude_db: np.ndarray

    phase_deg: np.ndarray


# ============================================================
# RESULTATS NYQUIST
# ============================================================

@dataclass
class NyquistResult:

    real: np.ndarray

    imag: np.ndarray


# ============================================================
# RESULTAT COMPLET
# ============================================================

@dataclass
class AnalysisResult:

    raw: MeasurementData

    fft: FFTResult

    bode: BodeResult

    nyquist: NyquistResult


# ============================================================
# PROGRESSION WORKER
# ============================================================

@dataclass
class ProgressInfo:

    percent: int

    current_step: str

    message: str = ""


# ============================================================
# MESSAGE D'ERREUR
# ============================================================

@dataclass
class ErrorInfo:

    title: str

    message: str

    traceback_text: str = ""


# ============================================================
# STATISTIQUES DE SIGNAL
# ============================================================

@dataclass
class SignalStatistics:

    peak: float

    rms: float

    crest_factor: float

    mean: float

    std: float


# ============================================================
# SESSION DE MESURE
# ============================================================

@dataclass
class MeasurementSession:

    config: MeasurementConfig

    result: Optional[AnalysisResult] = None

    statistics: Optional[SignalStatistics] = None

    state: AnalysisState = AnalysisState.IDLE

    filename: Optional[str] = None
