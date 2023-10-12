import os
import PySide6
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication,QLabel

dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname,'Qt','plugins','platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

if __name__ == '__main__':
    app = QApplication(sys.argv)
    label = QLabel('sdf',alignment=Qt.AlignCenter)
    label.show()
    sys.exit(app.exec())