
from __future__ import annotations

import threading
from datetime import datetime

import numpy as np
import sounddevice as sd

from scipy.signal import chirp

from models import (
    AudioDevice,
    MeasurementConfig,
    MeasurementData,
    SignalType,
)


# ============================================================
# DEVICE MANAGER
# ============================================================

class AudioDeviceManager:

    @staticmethod
    def get_devices():

        devices = []

        for index, device in enumerate(sd.query_devices()):

            devices.append(
                AudioDevice(
                    index=index,
                    name=device["name"],
                    max_input_channels=device["max_input_channels"],
                    max_output_channels=device["max_output_channels"],
                    default_samplerate=float(
                        device["default_samplerate"]
                    ),
                )
            )

        return devices

    @staticmethod
    def get_input_devices():

        return [
            d
            for d in AudioDeviceManager.get_devices()
            if d.is_input
        ]

    @staticmethod
    def get_output_devices():

        return [
            d
            for d in AudioDeviceManager.get_devices()
            if d.is_output
        ]


# ============================================================
# SIGNAL GENERATOR
# ============================================================

class SignalGenerator:

    @staticmethod
    def generate_log_sweep(
        samplerate: int,
        duration: float,
        f0: float,
        f1: float,
        amplitude: float,
    ):

        t = np.linspace(
            0,
            duration,
            int(duration * samplerate),
            endpoint=False,
        )

        sweep = chirp(
            t,
            f0=f0,
            f1=f1,
            t1=duration,
            method="logarithmic",
        )

        return (
            sweep * amplitude
        ).astype(np.float32)

    @staticmethod
    def generate_white_noise(
        samplerate: int,
        duration: float,
        amplitude: float,
    ):

        n = int(duration * samplerate)

        return (
            np.random.normal(
                0,
                amplitude,
                n,
            )
        ).astype(np.float32)

    @staticmethod
    def generate_pink_noise(
        samplerate: int,
        duration: float,
        amplitude: float,
    ):

        n = int(duration * samplerate)

        white = np.random.randn(n)

        spectrum = np.fft.rfft(white)

        freqs = np.fft.rfftfreq(n)

        freqs[0] = 1

        spectrum /= np.sqrt(freqs)

        pink = np.fft.irfft(
            spectrum,
            n=n,
        )

        pink /= np.max(
            np.abs(pink)
        )

        return (
            pink * amplitude
        ).astype(np.float32)

    @staticmethod
    def generate_signal(
        config: MeasurementConfig,
    ):

        if config.signal_type == SignalType.LOG_SWEEP:

            return SignalGenerator.generate_log_sweep(
                config.samplerate,
                config.duration,
                config.sweep_start_hz,
                config.sweep_stop_hz,
                config.amplitude,
            )

        elif config.signal_type == SignalType.WHITE_NOISE:

            return SignalGenerator.generate_white_noise(
                config.samplerate,
                config.duration,
                config.amplitude,
            )

        elif config.signal_type == SignalType.PINK_NOISE:

            return SignalGenerator.generate_pink_noise(
                config.samplerate,
                config.duration,
                config.amplitude,
            )

        raise ValueError(
            "Signal type non supporté"
        )


# ============================================================
# RECORDER
# ============================================================

class AudioRecorder:

    def __init__(self):

        self._stop_event = threading.Event()

    def stop(self):

        self._stop_event.set()

    def reset(self):

        self._stop_event.clear()

    def is_stopped(self):

        return self._stop_event.is_set()

    def record_measurement(
        self,
        config: MeasurementConfig,
        progress_callback=None,
    ) -> MeasurementData:

        self.reset()

        stimulus = SignalGenerator.generate_signal(
            config
        )

        input_buffer = []

        total_frames = len(stimulus)

        chunk_size = min(
            2048,
            total_frames
        )

        current_frame = 0

        def callback(
            indata,
            outdata,
            frames,
            time,
            status
        ):

            nonlocal current_frame

            if status:
                print(status)

            if self._stop_event.is_set():

                raise sd.CallbackAbort

            start = current_frame
            end = current_frame + frames

            if end > total_frames:

                end = total_frames

            chunk = stimulus[start:end]

            if len(chunk) < frames:

                padded = np.zeros(
                    frames,
                    dtype=np.float32
                )

                padded[: len(chunk)] = chunk

                chunk = padded

            outdata[:, 0] = chunk

            input_buffer.append(
                indata[:, 0].copy()
            )

            current_frame += frames

            if progress_callback:

                percent = int(
                    (
                        current_frame
                        / total_frames
                    )
                    * 100
                )

                progress_callback(
                    min(
                        percent,
                        100
                    )
                )

        try:

            with sd.Stream(
                samplerate=config.samplerate,
                blocksize=chunk_size,
                channels=1,
                dtype="float32",
                callback=callback,
                device=(
                    config.input_device,
                    config.output_device,
                ),
            ):

                sd.sleep(
                    int(
                        config.duration
                        * 1000
                    )
                    + 500
                )

        except sd.CallbackAbort:
            pass

        if not input_buffer:
            raise RuntimeError(
                "Aucune donnée audio reçue."
            )

        response = np.concatenate(
            input_buffer
        )

        response = response[: total_frames]

        timestamp = (
            datetime.now()
            .strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        return MeasurementData(
            stimulus=stimulus,
            response=response,
            samplerate=config.samplerate,
            duration=config.duration,
            timestamp=timestamp,
            metadata={
                "input_device":
                    config.input_device,
                "output_device":
                    config.output_device,
                "signal_type":
                    config.signal_type.value,
            },
        )


# ============================================================
# HELPER
# ============================================================

def list_audio_devices():

    inputs = (
        AudioDeviceManager
        .get_input_devices()
    )

    outputs = (
        AudioDeviceManager
        .get_output_devices()
    )

    return inputs, outputs
