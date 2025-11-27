from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHeaderView

from database.postgres import obtener_usuarios, crear_amistad_procedure
from database.neo4j_conn import obtener_recomendaciones_amigos, migrar_desde_postgres


class TabRecomendaciones(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Titulo y descripcion
        titulo = QLabel("Recomendaciones de Amigos")
        titulo.setProperty("class", "title")
        layout.addWidget(titulo)

        descripcion = QLabel("Descubre personas que son amigas de tus amigos pero no son tus amigos directos")
        descripcion.setProperty("class", "description")
        layout.addWidget(descripcion)

        layout.addSpacing(10)

        # Seleccion de usuario
        seccion_usuario = QLabel("Seleccionar Usuario")
        seccion_usuario.setProperty("class", "section-title")
        layout.addWidget(seccion_usuario)

        usuario_layout = QHBoxLayout()
        usuario_layout.addWidget(QLabel("Yo soy:"))
        self.combo_usuario = QComboBox()
        usuario_layout.addWidget(self.combo_usuario)
        usuario_layout.addStretch()
        layout.addLayout(usuario_layout)

        self.combo_usuario.currentIndexChanged.connect(self.cargar_recomendaciones)

        layout.addSpacing(10)

        # Tabla de recomendaciones
        seccion_tabla = QLabel("Personas Recomendadas")
        seccion_tabla.setProperty("class", "section-title")
        layout.addWidget(seccion_tabla)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Email", "Amigos en Común"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla)

        # Botones
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)

        btn_refresh = QPushButton("🔄 Actualizar Recomendaciones")
        btn_refresh.setProperty("class", "secondary")
        btn_refresh.clicked.connect(self.cargar_recomendaciones)
        botones_layout.addWidget(btn_refresh)

        botones_layout.addStretch()

        self.btn_enviar_solicitud = QPushButton("➕ Enviar Solicitud al Seleccionado")
        self.btn_enviar_solicitud.setProperty("class", "success")
        self.btn_enviar_solicitud.clicked.connect(self.enviar_solicitud)
        self.btn_enviar_solicitud.setEnabled(False)
        botones_layout.addWidget(self.btn_enviar_solicitud)

        layout.addLayout(botones_layout)

        self.tabla.cellClicked.connect(self.seleccionar_recomendacion)

        # Mensaje de estado
        self.lbl_mensaje = QLabel("")
        layout.addWidget(self.lbl_mensaje)

        # Variables de estado
        self.fila_seleccionada = -1

        # Cargar datos iniciales
        self.cargar_usuarios()

    # Cargar usuarios
    def cargar_usuarios(self):
        """Cargar usuarios en el combo box"""
        usuarios = obtener_usuarios()
        
        self.combo_usuario.clear()
        
        for u in usuarios:
            text = f"{u[0]} - {u[1]}"
            self.combo_usuario.addItem(text, u[0])

    # Cargar recomendaciones
    def cargar_recomendaciones(self):
        """Cargar recomendaciones de amigos desde Neo4j"""
        id_usuario = self.combo_usuario.currentData()
        
        if not id_usuario:
            return

        try:
            recomendaciones = obtener_recomendaciones_amigos(id_usuario)
            
            self.tabla.setRowCount(len(recomendaciones))
            
            if len(recomendaciones) == 0:
                self.lbl_mensaje.setText("No hay recomendaciones disponibles para este usuario.")
                self.lbl_mensaje.setStyleSheet("color: #666;")
            else:
                self.lbl_mensaje.setText(f"Se encontraron {len(recomendaciones)} recomendaciones")
                self.lbl_mensaje.setStyleSheet("color: green;")
            
            for row, rec in enumerate(recomendaciones):
                self.tabla.setItem(row, 0, QTableWidgetItem(str(rec['id'])))
                self.tabla.setItem(row, 1, QTableWidgetItem(rec['nombre']))
                self.tabla.setItem(row, 2, QTableWidgetItem(rec['email']))
                self.tabla.setItem(row, 3, QTableWidgetItem(str(rec['amigos_en_comun'])))
            
            self.fila_seleccionada = -1
            self.btn_enviar_solicitud.setEnabled(False)
            
        except Exception as e:
            self.mensaje_error(f"Error al cargar recomendaciones: {str(e)}")
            print(f"Error en cargar_recomendaciones: {e}")

    # Seleccion de recomendacion
    def seleccionar_recomendacion(self, row, col):
        """Manejar selección de una recomendación"""
        self.fila_seleccionada = row
        self.btn_enviar_solicitud.setEnabled(True)

    # Enviar solicitud de amistad
    def enviar_solicitud(self):
        """Enviar solicitud de amistad a la persona recomendada"""
        if self.fila_seleccionada < 0:
            self.mensaje_error("Seleccione una recomendación primero.")
            return

        id_usuario = self.combo_usuario.currentData()
        id_recomendado = int(self.tabla.item(self.fila_seleccionada, 0).text())
        nombre_recomendado = self.tabla.item(self.fila_seleccionada, 1).text()

        try:
            # Crear amistad en PostgreSQL
            mensaje = crear_amistad_procedure(id_usuario, id_recomendado)
            
            # Sincronizar con Neo4j
            migrar_desde_postgres()
            
            # Recargar recomendaciones
            self.cargar_recomendaciones()
            
            self.mensaje_info(f"Solicitud enviada a {nombre_recomendado}. {mensaje}")
            
        except Exception as e:
            self.mensaje_error(f"Error al enviar solicitud: {str(e)}")
            print(f"Error en enviar_solicitud: {e}")

    # Mensajes
    def mensaje_info(self, texto):
        """Mostrar mensaje de información"""
        msg = QMessageBox()
        msg.setWindowTitle("Información")
        msg.setText(texto)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowIcon(QIcon("ui/AmigosDB.png"))
        msg.exec_()

    def mensaje_error(self, texto):
        """Mostrar mensaje de error"""
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(texto)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowIcon(QIcon("ui/AmigosDB.png"))
        msg.exec_()
