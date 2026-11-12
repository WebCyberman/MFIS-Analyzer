import tkinter as tk
from tkinter import Menu, messagebox
import threading
import traceback

import numpy as np
import pyaudio

from scipy.fft import rfft, rfftfreq

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ============================================================
# CONFIGURATION
# ============================================================

RATE = 48000
DURATION = 5
CHUNK = 1024

input_device_index = None
output_device_index = None

root = None
current_canvas = None

closing = False
analysis_running = False

status_var = None

input_devices = []
output_devices = []


# ============================================================
# AUDIO
# ============================================================

def generate_white_noise(duration, rate):
    return np.random.normal(
        0,
        1,
        int(duration * rate)
    ).astype(np.float32)


def perform_fft(signal, rate):

    n = len(signal)

    yf = rfft(signal)

    xf = rfftfreq(
        n,
        1.0 / rate
    )

    return xf, yf


# ============================================================
# DEVICE SCAN
# ============================================================

def list_audio_devices():

    p = pyaudio.PyAudio()

    inputs = []
    outputs = []

    try:

        for i in range(p.get_device_count()):

            info = p.get_device_info_by_index(i)

            name = info["name"]

            if info["maxInputChannels"] > 0:
                inputs.append((i, name))

            if info["maxOutputChannels"] > 0:
                outputs.append((i, name))

    finally:
        p.terminate()

    return inputs, outputs


# ============================================================
# ANALYSIS
# ============================================================

def start_analysis():

    global analysis_running
    global current_canvas

    if analysis_running:
        return

    analysis_running = True

    if root:
        root.after(
            0,
            lambda: status_var.set("Analyse en cours...")
        )

    p = pyaudio.PyAudio()

    stream_out = None
    stream_in = None

    try:

        white_noise = generate_white_noise(
            DURATION,
            RATE
        )

        stream_out = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=RATE,
            output=True,
            output_device_index=output_device_index
        )

        stream_in = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=RATE,
            input=True,
            input_device_index=input_device_index,
            frames_per_buffer=CHUNK
        )

        stream_out.write(
            white_noise.tobytes()
        )

        chunks = []

        remaining = int(
            RATE * DURATION
        )

        while remaining > 0 and not closing:

            count = min(
                CHUNK,
                remaining
            )

            data = stream_in.read(
                count,
                exception_on_overflow=False
            )

            chunks.append(data)

            remaining -= count

        response_data = b"".join(chunks)

        response = np.frombuffer(
            response_data,
            dtype=np.float32
        )

        if response.size == 0:
            raise RuntimeError(
                "Aucune donnée reçue depuis l'entrée audio."
            )

        n = min(
            len(response),
            len(white_noise)
        )

        response = response[:n]
        white_noise = white_noise[:n]

        xf, yf_noise = perform_fft(
            white_noise,
            RATE
        )

        _, yf_response = perform_fft(
            response,
            RATE
        )

        epsilon = 1e-12

        impedance = (
            yf_response /
            (yf_noise + epsilon)
        )

        amplitude_db = 20 * np.log10(
            np.abs(impedance) + epsilon
        )

        phase_deg = np.angle(
            impedance,
            deg=True
        )

        fig, axs = plt.subplots(
            3,
            1,
            figsize=(10, 12)
        )

        axs[0].plot(
            xf,
            np.abs(yf_noise),
            label="Bruit blanc"
        )

        axs[0].plot(
            xf,
            np.abs(yf_response),
            label="Réponse"
        )

        axs[0].legend()
        axs[0].grid(True)
        axs[0].set_title(
            "Spectres de fréquence"
        )

        axs[1].semilogx(
            xf,
            amplitude_db,
            label="Amplitude (dB)"
        )

        axs[1].semilogx(
            xf,
            phase_deg,
            label="Phase (°)"
        )

        axs[1].legend()

        axs[1].grid(
            True,
            which="both"
        )

        axs[1].set_title(
            "Diagramme de Bode"
        )

        axs[2].plot(
            np.real(impedance),
            -np.imag(impedance),
            "."
        )

        axs[2].grid(True)

        axs[2].set_title(
            "Courbe de Nyquist"
        )

        plt.tight_layout()

        if root and not closing:

            def update_plot():

                global current_canvas

                if current_canvas is not None:
                    current_canvas.get_tk_widget().destroy()

                current_canvas = FigureCanvasTkAgg(
                    fig,
                    master=root
                )

                current_canvas.draw()

                current_canvas.get_tk_widget().pack(
                    fill=tk.BOTH,
                    expand=True
                )

            root.after(
                0,
                update_plot
            )

    except Exception as e:

        print(traceback.format_exc())

        if root and not closing:

            root.after(
                0,
                lambda: messagebox.showerror(
                    "Erreur",
                    str(e)
                )
            )

    finally:

        try:
            if stream_out:
                stream_out.stop_stream()
                stream_out.close()
        except:
            pass

        try:
            if stream_in:
                stream_in.stop_stream()
                stream_in.close()
        except:
            pass

        try:
            p.terminate()
        except:
            pass

        analysis_running = False

        if root and not closing:

            root.after(
                0,
                lambda: status_var.set("Prêt")
            )


# ============================================================
# GUI
# ============================================================

def update_input_device(name):
    global input_device_index

    for idx, devname in input_devices:
        if devname == name:
            input_device_index = idx
            return


def update_output_device(name):
    global output_device_index

    for idx, devname in output_devices:
        if devname == name:
            output_device_index = idx
            return


def launch_analysis():

    threading.Thread(
        target=start_analysis,
        daemon=True
    ).start()


def on_closing():

    global closing

    closing = True

    try:
        plt.close("all")
    except:
        pass

    try:
        root.quit()
    except:
        pass

    try:
        root.destroy()
    except:
        pass


def create_gui():

    global root
    global status_var
    global input_devices
    global output_devices

    input_devices, output_devices = list_audio_devices()

    root = tk.Tk()

    root.title("Analyse MFIS")

    root.geometry("1200x900")

    root.protocol(
        "WM_DELETE_WINDOW",
        on_closing
    )

    menu_bar = Menu(root)

    root.config(menu=menu_bar)

    # --------------------
    # Fichier
    # --------------------

    file_menu = Menu(
        menu_bar,
        tearoff=0
    )

    menu_bar.add_cascade(
        label="Fichier",
        menu=file_menu
    )

    file_menu.add_command(
        label="Quitter",
        command=on_closing
    )

    # --------------------
    # Périphériques
    # --------------------

    device_menu = Menu(
        menu_bar,
        tearoff=0
    )

    menu_bar.add_cascade(
        label="Périphériques",
        menu=device_menu
    )

    input_var = tk.StringVar()
    output_var = tk.StringVar()

    input_menu = Menu(
        device_menu,
        tearoff=0
    )

    output_menu = Menu(
        device_menu,
        tearoff=0
    )

    if input_devices:

        input_var.set(
            input_devices[0][1]
        )

        update_input_device(
            input_devices[0][1]
        )

    if output_devices:

        output_var.set(
            output_devices[0][1]
        )

        update_output_device(
            output_devices[0][1]
        )

    for idx, name in input_devices:

        input_menu.add_radiobutton(
            label=name,
            variable=input_var,
            value=name,
            command=lambda n=name:
            update_input_device(n)
        )

    for idx, name in output_devices:

        output_menu.add_radiobutton(
            label=name,
            variable=output_var,
            value=name,
            command=lambda n=name:
            update_output_device(n)
        )

    device_menu.add_cascade(
        label="Entrées",
        menu=input_menu
    )

    device_menu.add_cascade(
        label="Sorties",
        menu=output_menu
    )

    # --------------------
    # Analyse
    # --------------------

    analysis_menu = Menu(
        menu_bar,
        tearoff=0
    )

    menu_bar.add_cascade(
        label="Analyse",
        menu=analysis_menu
    )

    analysis_menu.add_command(
        label="Lancer l'analyse",
        command=launch_analysis
    )

    # --------------------
    # Status Bar
    # --------------------

    status_var = tk.StringVar()

    status_var.set("Prêt")

    status = tk.Label(
        root,
        textvariable=status_var,
        anchor="w"
    )

    status.pack(
        side=tk.BOTTOM,
        fill=tk.X
    )

    return root


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    create_gui()

    root.mainloop()