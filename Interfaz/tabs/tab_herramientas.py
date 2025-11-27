import webbrowser
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from database.neo4j_conn import (
    migrar_desde_postgres,
    migrar_json_a_neo4j,
    migrar_neo4j_a_postgres,
    get_driver)
from database.json_loader import cargar_json_file, migrar_json_a_postgres

class TabHerramientas(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        self.setLayout(layout)
        
        # Titulo
        titulo = QLabel("Herramientas de Migración")
        titulo.setProperty("class", "title")
        layout.addWidget(titulo)

        descripcion = QLabel("Gestiona la sincronización de datos entre PostgreSQL, Neo4j y archivos JSON")
        descripcion.setProperty("class", "description")
        layout.addWidget(descripcion)

        layout.addSpacing(15)

        # Postgresql a neo4j
        seccion1 = QLabel("🔄 Sincronización PostgreSQL → Neo4j")
        seccion1.setProperty("class", "section-title")
        layout.addWidget(seccion1)

        box_pg = QHBoxLayout()
        lbl_pg = QLabel("Migrar datos desde PostgreSQL:")
        btn_pg = QPushButton("➡️ PostgreSQL a Neo4j")
        btn_pg.clicked.connect(self.migrar_pg)
        box_pg.addWidget(lbl_pg)
        box_pg.addStretch()
        box_pg.addWidget(btn_pg)
        layout.addLayout(box_pg)

        self.btn_pg = btn_pg
        self.add_separator(layout)

        # Json a neo4j
        seccion2 = QLabel("📄 Importar desde JSON")
        seccion2.setProperty("class", "section-title")
        layout.addWidget(seccion2)

        box_json1 = QHBoxLayout()
        self.lbl_json = QLabel("Archivo JSON: Ninguno")
        btn_sel_json = QPushButton("📂 Seleccionar JSON")
        btn_sel_json.setProperty("class", "secondary")
        btn_sel_json.clicked.connect(self.seleccionar_json)
        box_json1.addWidget(self.lbl_json)
        box_json1.addStretch()
        box_json1.addWidget(btn_sel_json)
        layout.addLayout(box_json1)

        box_json2 = QHBoxLayout()
        lbl_json2 = QLabel("Migrar JSON seleccionado:")
        btn_migrar_json = QPushButton("➡️ JSON a Neo4j")
        btn_migrar_json.clicked.connect(self.migrar_json)
        box_json2.addWidget(lbl_json2)
        box_json2.addStretch()
        box_json2.addWidget(btn_migrar_json)
        layout.addLayout(box_json2)

        self.btn_migrar_json = btn_migrar_json
        self.btn_migrar_json.setEnabled(False)

        # Json a postgresql
        box_json_pg = QHBoxLayout()
        lbl_json_pg = QLabel("Guardar JSON en PostgreSQL:")
        btn_json_pg = QPushButton("➡️ JSON a PostgreSQL")
        btn_json_pg.clicked.connect(self.migrar_json_a_postgres_btn)
        box_json_pg.addWidget(lbl_json_pg)
        box_json_pg.addStretch()
        box_json_pg.addWidget(btn_json_pg)
        layout.addLayout(box_json_pg)

        self.btn_json_pg = btn_json_pg
        self.btn_json_pg.setEnabled(False)

        self.add_separator(layout)

        # Neo4j a postgresql
        seccion3 = QLabel("🔄 Sincronización Neo4j → PostgreSQL")
        seccion3.setProperty("class", "section-title")
        layout.addWidget(seccion3)

        box_neo_pg = QHBoxLayout()
        lbl_neo_pg = QLabel("Migrar datos desde Neo4j a PostgreSQL:")
        btn_neo_pg = QPushButton("➡️ Neo4j a PostgreSQL")
        btn_neo_pg.clicked.connect(self.migrar_neo_pg)
        box_neo_pg.addWidget(lbl_neo_pg)
        box_neo_pg.addStretch()
        box_neo_pg.addWidget(btn_neo_pg)
        layout.addLayout(box_neo_pg)

        self.btn_neo_pg = btn_neo_pg

        self.add_separator(layout)

        # Limpiar grafo
        seccion4 = QLabel("🧹 Mantenimiento")
        seccion4.setProperty("class", "section-title")
        layout.addWidget(seccion4)

        box_clean = QHBoxLayout()
        lbl_clean = QLabel("Limpiar grafo completamente:")
        btn_clean = QPushButton("🗑️ Limpiar Grafo")
        btn_clean.setProperty("class", "danger")
        btn_clean.clicked.connect(self.limpiar_grafo)
        box_clean.addWidget(lbl_clean)
        box_clean.addStretch()
        box_clean.addWidget(btn_clean)
        layout.addLayout(box_clean)

        self.btn_clean = btn_clean

        self.add_separator(layout)

        # Abrir browser neo4j
        box_browser = QHBoxLayout()
        lbl_browser = QLabel("Abrir visualizador de grafo Neo4j:")
        btn_browser = QPushButton("🌐 Abrir Neo4j Browser")
        btn_browser.setProperty("class", "secondary")
        btn_browser.clicked.connect(self.abrir_browser)
        box_browser.addWidget(lbl_browser)
        box_browser.addStretch()
        box_browser.addWidget(btn_browser)
        layout.addLayout(box_browser)

        self.btn_browser = btn_browser

        # Estado
        self.lbl_estado = QLabel("")
        layout.addWidget(self.lbl_estado)

        # Ruta json
        self.json_path = None

    # Separador visual
    def add_separator(self, layout):
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        sep.setStyleSheet("background-color: #e2e8f0; max-height: 2px;")
        layout.addWidget(sep)

    # Mensaje emergente
    def mensaje(self, txt):
        msg = QMessageBox()
        msg.setWindowTitle("Información")
        msg.setText(txt)
        msg.setWindowIcon(QIcon("ui/AmigosDB.png"))
        msg.exec_()

    # Migrar postgresql a neo4j
    def migrar_pg(self):
        self.btn_pg.setEnabled(False)
        migrar_desde_postgres()
        self.btn_pg.setEnabled(True)
        self.lbl_estado.setText("Migración PostgreSQL a Neo4j completada.")
        self.mensaje("Migración finalizada.")

    # Seleccionar json
    def seleccionar_json(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo JSON", "", "JSON (*.json)"
        )
        if ruta:
            self.json_path = ruta
            self.lbl_json.setText(f"Archivo JSON seleccionado: {ruta}")
            self.btn_migrar_json.setEnabled(True)
            self.btn_json_pg.setEnabled(True)
        else:
            self.btn_migrar_json.setEnabled(False)
            self.btn_json_pg.setEnabled(False)

    # Json a neo4j
    def migrar_json(self):
        if not self.json_path:
            self.mensaje("Seleccione primero un archivo JSON.")
            return

        self.btn_migrar_json.setEnabled(False)
        datos = cargar_json_file(self.json_path)
        migrar_json_a_neo4j(datos)

        self.lbl_estado.setText("Migración JSON a Neo4j completada.")
        self.mensaje("Datos migrados correctamente.")
        self.limpiar_json()

    # Json a postgresql
    def migrar_json_a_postgres_btn(self):
        if not self.json_path:
            self.mensaje("Seleccione primero un archivo JSON.")
            return

        self.btn_json_pg.setEnabled(False)
        datos = cargar_json_file(self.json_path)
        migrar_json_a_postgres(datos)

        self.lbl_estado.setText("JSON a PostgreSQL completado.")
        self.mensaje("Datos escritos en PostgreSQL correctamente.")
        self.limpiar_json()

    # Neo4j a postgresql
    def migrar_neo_pg(self):
        self.btn_neo_pg.setEnabled(False)
        migrar_neo4j_a_postgres()
        
        # Sincronizar de vuelta a Neo4j para que las recomendaciones funcionen
        migrar_desde_postgres()
        
        self.btn_neo_pg.setEnabled(True)

        self.lbl_estado.setText("Neo4j a PostgreSQL completado y sincronizado.")
        self.mensaje("Datos migrados desde Neo4j correctamente.")

        parent_window = self.parent().parent()

        try:
            # Refrescar usuarios
            from tabs.tab_usuarios import TabUsuarios
            for tab in parent_window.findChildren(TabUsuarios):
                tab.cargar_usuarios()

            # Refrescar amistades
            from tabs.tab_amistades import TabAmistades
            for tab in parent_window.findChildren(TabAmistades):
                try:
                    tab.cargar_usuarios()
                except:
                    pass

                try:
                    tab.cargar_mis_amistades()
                except:
                    pass

            # Refrescar feed
            from tabs.tab_feed import TabFeed
            for tab in parent_window.findChildren(TabFeed):
                tab.actualizar_todo()

            # Refrescar recomendaciones
            from tabs.tab_recomendaciones import TabRecomendaciones
            for tab in parent_window.findChildren(TabRecomendaciones):
                try:
                    tab.cargar_usuarios()
                    tab.cargar_recomendaciones()
                except:
                    pass

            print("Interfaz refrescada después de migración.")

        except Exception as e:
            print("Error refrescando interfaz:", e)

    # Limpiar grafo
    def limpiar_grafo(self):
        self.btn_clean.setEnabled(False)

        driver = get_driver()
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        driver.close()

        self.btn_clean.setEnabled(True)
        self.lbl_estado.setText("Grafo completamente limpiado.")
        self.mensaje("Grafo vaciado exitosamente.")
   
    # Abrir browser neo4j
    def abrir_browser(self):
        webbrowser.open("http://localhost:7474/browser/")
        self.lbl_estado.setText("Abriendo Neo4j Browser…")

    # Limpiar seleccion json
    def limpiar_json(self):
        self.json_path = None
        self.lbl_json.setText("Archivo JSON: Ninguno")
        self.btn_migrar_json.setEnabled(False)
        self.btn_json_pg.setEnabled(False)