import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QFile, QTextStream, QIODevice
from main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 加载样式表
    file = QFile("style.qss")
    if file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())