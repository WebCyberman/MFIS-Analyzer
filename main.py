
# main.py

from __future__ import annotations

import sys
import traceback

from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
)

from ui.main_window import MainWindow


# ============================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================

def exception_hook(exc_type, exc_value, exc_traceback):

    error_text = "".join(
        traceback.format_exception(
            exc_type,
            exc_value,
            exc_traceback
        )
    )

    print(error_text)

    QMessageBox.critical(
        None,
        "Erreur inattendue",
        error_text,
    )


# ============================================================
# APPLICATION
# ============================================================

def main():

    sys.excepthook = exception_hook

    app = QApplication(sys.argv)

    app.setApplicationName(
        "Audio Analyzer"
    )

    app.setOrganizationName(
        "Open Audio Tools"
    )

    app.setQuitOnLastWindowClosed(
        True
    )

    window = MainWindow()

    window.show()

    return app.exec()


# ============================================================
# ENTRYPOINT
# ============================================================

if __name__ == "__main__":

    sys.exit(main())
