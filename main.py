import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import TexturePackerWindow
from utils.path_utils import resource_path

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application-wide icon
    icon_path = resource_path("resources/icon.ico")
    app.setWindowIcon(QIcon(icon_path))

    window = TexturePackerWindow()
    window.show()
    sys.exit(app.exec())