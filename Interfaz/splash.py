# Importar las librerías necesarias
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QApplication
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import sys
from main import MainWindow
from PyQt5.QtGui import QIcon

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AmigosDB")
        self.setGeometry(500, 200, 500, 350)
        self.setStyleSheet("background-color: #1f2937; border-radius: 15px;")
        self.setWindowIcon(QIcon("ui/AmigosDB.png"))
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        # Logo
        logo = QLabel()
        pixmap = QPixmap("ui/AmigosDB.png")
        pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # Titulo
        title = QLabel("AmigosDB")
        title.setFont(QFont("Arial", 26, QFont.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Botón Iniciar
        btn = QPushButton("Iniciar")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn.clicked.connect(self.iniciar_app)
        layout.addWidget(btn)

    def iniciar_app(self):
        self.main = MainWindow()
        self.main.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    sys.exit(app.exec_())
