
from __future__ import annotations

import numpy as np

from scipy.fft import (
    rfft,
    rfftfreq,
)

from scipy.signal import (
    windows,
    savgol_filter,
)

from models import (
    MeasurementData,
    FFTResult,
    BodeResult,
    NyquistResult,
    AnalysisResult,
    SignalStatistics,
)


# ============================================================
# DSP CONFIG
# ============================================================

EPSILON = 1e-12


# ============================================================
# SIGNAL UTILITIES
# ============================================================

class SignalUtils:

    @staticmethod
    def remove_dc(signal: np.ndarray):

        return signal - np.mean(signal)

    @staticmethod
    def normalize(signal: np.ndarray):

        peak = np.max(np.abs(signal))

        if peak < EPSILON:
            return signal.copy()

        return signal / peak

    @staticmethod
    def window(signal: np.ndarray):

        return (
            signal *
            windows.hann(len(signal))
        )


# ============================================================
# FFT ANALYZER
# ============================================================

class FFTAnalyzer:

    @staticmethod
    def compute_fft(
        signal: np.ndarray,
        samplerate: int,
    ):

        signal = SignalUtils.remove_dc(
            signal
        )

        signal = SignalUtils.window(
            signal
        )

        spectrum = rfft(signal)

        frequencies = rfftfreq(
            len(signal),
            d=1.0 / samplerate
        )

        return frequencies, spectrum

    @staticmethod
    def transfer_function(
        stimulus_fft: np.ndarray,
        response_fft: np.ndarray,
    ):

        return (
            response_fft
            /
            (
                stimulus_fft
                + EPSILON
            )
        )


# ============================================================
# SMOOTHING
# ============================================================

class Smoothing:

    @staticmethod
    def apply(
        data: np.ndarray,
        window_length: int = 101,
        polyorder: int = 3,
    ):

        if len(data) < window_length:

            return data

        if window_length % 2 == 0:

            window_length += 1

        return savgol_filter(
            data,
            window_length=window_length,
            polyorder=polyorder,
        )


# ============================================================
# BODE
# ============================================================

class BodeAnalyzer:

    @staticmethod
    def compute(
        frequencies: np.ndarray,
        transfer_function: np.ndarray,
        smooth: bool = True,
    ):

        magnitude = np.abs(
            transfer_function
        )

        amplitude_db = (
            20
            * np.log10(
                magnitude + EPSILON
            )
        )

        phase_deg = np.degrees(
            np.unwrap(
                np.angle(
                    transfer_function
                )
            )
        )

        if smooth:

            amplitude_db = (
                Smoothing.apply(
                    amplitude_db
                )
            )

            phase_deg = (
                Smoothing.apply(
                    phase_deg
                )
            )

        return BodeResult(
            frequencies=frequencies,
            amplitude_db=amplitude_db,
            phase_deg=phase_deg,
        )


# ============================================================
# NYQUIST
# ============================================================

class NyquistAnalyzer:

    @staticmethod
    def compute(
        transfer_function: np.ndarray
    ):

        return NyquistResult(
            real=np.real(
                transfer_function
            ),
            imag=np.imag(
                transfer_function
            ),
        )


# ============================================================
# SIGNAL STATISTICS
# ============================================================

class StatisticsAnalyzer:

    @staticmethod
    def compute(
        signal: np.ndarray
    ):

        peak = float(
            np.max(
                np.abs(signal)
            )
        )

        rms = float(
            np.sqrt(
                np.mean(
                    signal ** 2
                )
            )
        )

        mean = float(
            np.mean(signal)
        )

        std = float(
            np.std(signal)
        )

        crest_factor = (
            peak / (rms + EPSILON)
        )

        return SignalStatistics(
            peak=peak,
            rms=rms,
            crest_factor=float(
                crest_factor
            ),
            mean=mean,
            std=std,
        )


# ============================================================
# MAIN ANALYZER
# ============================================================

class MeasurementAnalyzer:

    @staticmethod
    def analyze(
        measurement: MeasurementData,
        smooth=True,
    ):

        frequencies, stimulus_fft = (
            FFTAnalyzer.compute_fft(
                measurement.stimulus,
                measurement.samplerate,
            )
        )

        _, response_fft = (
            FFTAnalyzer.compute_fft(
                measurement.response,
                measurement.samplerate,
            )
        )

        transfer_function = (
            FFTAnalyzer.transfer_function(
                stimulus_fft,
                response_fft,
            )
        )

        fft_result = FFTResult(
            frequencies=frequencies,
            stimulus_fft=stimulus_fft,
            response_fft=response_fft,
            transfer_function=transfer_function,
        )

        bode_result = (
            BodeAnalyzer.compute(
                frequencies,
                transfer_function,
                smooth=smooth,
            )
        )

        nyquist_result = (
            NyquistAnalyzer.compute(
                transfer_function
            )
        )

        return AnalysisResult(
            raw=measurement,
            fft=fft_result,
            bode=bode_result,
            nyquist=nyquist_result,
        )

    @staticmethod
    def statistics(
        measurement: MeasurementData
    ):

        return (
            StatisticsAnalyzer.compute(
                measurement.response
            )
        )


# ============================================================
# EXPORT HELPERS
# ============================================================

class ExportHelper:

    @staticmethod
    def bode_to_csv(
        result: AnalysisResult,
        filename: str,
    ):

        data = np.column_stack(
            [
                result.bode.frequencies,
                result.bode.amplitude_db,
                result.bode.phase_deg,
            ]
        )

        np.savetxt(
            filename,
            data,
            delimiter=",",
            header=(
                "Frequency,"
                "Amplitude_dB,"
                "Phase_deg"
            ),
            comments="",
        )

    @staticmethod
    def nyquist_to_csv(
        result: AnalysisResult,
        filename: str,
    ):

        data = np.column_stack(
            [
                result.nyquist.real,
                result.nyquist.imag,
            ]
        )

        np.savetxt(
            filename,
            data,
            delimiter=",",
            header="Real,Imag",
            comments="",
        )
