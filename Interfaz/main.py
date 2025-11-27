# Importar módulos necesarios
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget

# Importar pestañas
from tabs.tab_usuarios import TabUsuarios
from tabs.tab_amistades import TabAmistades
from tabs.tab_feed import TabFeed
from tabs.tab_herramientas import TabHerramientas
from PyQt5.QtGui import QIcon

# Importar estilos
from ui.styles import load_styles

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AmigosDB")
        self.setGeometry(200, 100, 900, 600)

        # Crear widget de pestañas
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Añadir pestañas
        self.tabs.addTab(TabUsuarios(), "Usuarios")
        self.tabs.addTab(TabAmistades(), "Amistades")
        self.tabs.addTab(TabFeed(), "Feed")
        self.tabs.addTab(TabHerramientas(), "Herramientas")
        
        self.setWindowIcon(QIcon("ui/AmigosDB.png"))

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setStyleSheet(load_styles())
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
