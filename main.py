

from PySide6.QtWidgets import QApplication
from ui import MainUI


if __name__ == "__main__":
    app = QApplication([])


    window = MainUI()
    # Redirect stderr to the error log

    window.show()
    app.exec()