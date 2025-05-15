import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import TexturePackerWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application-wide icon
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.ico")
    app.setWindowIcon(QIcon(icon_path))

    window = TexturePackerWindow()
    window.show()
    sys.exit(app.exec())