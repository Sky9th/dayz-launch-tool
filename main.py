

from PySide6.QtWidgets import QApplication
from ui import MainUI

app = QApplication([])
window = MainUI()
# Redirect stderr to the error log
window.show()
app.exec()