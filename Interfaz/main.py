# Importar módulos necesarios
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget

# Importar pestañas
from tabs.tab_usuarios import TabUsuarios
from tabs.tab_amistades import TabAmistades
from tabs.tab_feed import TabFeed
from tabs.tab_herramientas import TabHerramientas
from tabs.tab_recomendaciones import TabRecomendaciones
from PyQt5.QtGui import QIcon

# Importar estilos
from ui.styles import load_styles

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AmigosDB")
        self.setGeometry(100, 50, 1400, 900)
        
        # Maximizar ventana al iniciar
        self.showMaximized()

        # Crear widget de pestañas
        self.tabs = QTabWidget()
        self.tabs.setContentsMargins(10, 10, 10, 10)
        self.setCentralWidget(self.tabs)

        # Añadir pestañas
        self.tabs.addTab(TabUsuarios(), "👤 Usuarios")
        self.tabs.addTab(TabAmistades(), "🤝 Amistades")
        self.tabs.addTab(TabRecomendaciones(), "✨ Recomendaciones")
        self.tabs.addTab(TabFeed(), "📰 Feed")
        self.tabs.addTab(TabHerramientas(), "🛠️ Herramientas")
        
        self.setWindowIcon(QIcon("ui/AmigosDB.png"))

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setStyleSheet(load_styles())
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
