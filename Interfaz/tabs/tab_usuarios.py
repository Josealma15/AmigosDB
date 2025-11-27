from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)

from database.postgres import (
    obtener_usuarios, crear_usuario,
    actualizar_usuario, eliminar_usuario
)

from database.neo4j_conn import migrar_desde_postgres
from PyQt5.QtWidgets import QHeaderView

class TabUsuarios(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Tabla de usuarios
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Email", "País"])
        self.tabla.cellClicked.connect(self.cargar_usuario_en_formulario)
        layout.addWidget(self.tabla)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Formulario de entrada
        form_layout = QHBoxLayout()

        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre")

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Email")

        self.input_pais = QLineEdit()
        self.input_pais.setPlaceholderText("País")

        form_layout.addWidget(self.input_nombre)
        form_layout.addWidget(self.input_email)
        form_layout.addWidget(self.input_pais)

        layout.addLayout(form_layout)

        # Botones de acción
        botones = QHBoxLayout()

        btn_cargar = QPushButton("Refrescar Usuarios")
        btn_cargar.clicked.connect(self.cargar_usuarios)

        btn_agregar = QPushButton("Agregar")
        btn_agregar.clicked.connect(self.agregar_usuario)

        btn_actualizar = QPushButton("Actualizar")
        btn_actualizar.clicked.connect(self.actualizar_usuario)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.clicked.connect(self.eliminar_usuario)

        botones.addWidget(btn_cargar)
        botones.addWidget(btn_agregar)
        botones.addWidget(btn_actualizar)
        botones.addWidget(btn_eliminar)

        layout.addLayout(botones)

        # Referencias para activar/desactivar botones
        self.btn_actualizar = btn_actualizar
        self.btn_eliminar = btn_eliminar

        # Botones desactivados al inicio
        self.btn_actualizar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)

        # Cargar usuarios
        self.cargar_usuarios()

    # Mostrar mensajes
    def mensaje(self, texto):
        msg = QMessageBox()
        msg.setWindowTitle("Información")
        msg.setText(texto)
        msg.exec_()

    # Autollenar formulario al seleccionar fila
    def cargar_usuario_en_formulario(self, row, col):
        nombre = self.tabla.item(row, 1).text()
        email  = self.tabla.item(row, 2).text()
        pais   = self.tabla.item(row, 3).text()

        self.input_nombre.setText(nombre)
        self.input_email.setText(email)
        self.input_pais.setText(pais)

        # activar botones cuando hay selección
        self.btn_actualizar.setEnabled(True)
        self.btn_eliminar.setEnabled(True)

    # Funciones CRUD
    def cargar_usuarios(self):
        usuarios = obtener_usuarios()
        self.tabla.setRowCount(len(usuarios))

        for row, u in enumerate(usuarios):
            self.tabla.setItem(row, 0, QTableWidgetItem(str(u[0])))
            self.tabla.setItem(row, 1, QTableWidgetItem(u[1]))
            self.tabla.setItem(row, 2, QTableWidgetItem(u[2]))
            self.tabla.setItem(row, 3, QTableWidgetItem(u[3]))

    def agregar_usuario(self):
        nombre = self.input_nombre.text().strip()
        email  = self.input_email.text().strip()
        pais   = self.input_pais.text().strip()

        if not nombre or not email or not pais:
            self.mensaje("Debe llenar todos los campos.")
            return

        crear_usuario(nombre, email, pais)
        migrar_desde_postgres()

        self.cargar_usuarios()
        self.mensaje("Usuario agregado correctamente.")
        self.limpiar_formulario()

    def actualizar_usuario(self):
        row = self.tabla.currentRow()
        if row < 0:
            self.mensaje("Seleccione un usuario primero.")
            return

        id_usuario = int(self.tabla.item(row, 0).text())

        nombre = self.input_nombre.text().strip()
        email  = self.input_email.text().strip()
        pais   = self.input_pais.text().strip()

        if not nombre or not email or not pais:
            self.mensaje("Debe llenar todos los campos para actualizar.")
            return

        actualizar_usuario(id_usuario, nombre, email, pais)
        migrar_desde_postgres()
        self.cargar_usuarios()
        self.mensaje("Usuario actualizado.")
        self.limpiar_formulario()

    def eliminar_usuario(self):
        row = self.tabla.currentRow()
        if row < 0:
            self.mensaje("Seleccione un usuario primero.")
            return

        id_usuario = int(self.tabla.item(row, 0).text())

        eliminar_usuario(id_usuario)
        migrar_desde_postgres()

        self.cargar_usuarios()
        self.mensaje("Usuario eliminado.")
        self.limpiar_formulario()
    
    # Limpiar formulario cuando se actualiza o elimina un usuario
    def limpiar_formulario(self):
        self.input_nombre.clear()
        self.input_email.clear()
        self.input_pais.clear()
        self.tabla.clearSelection()

        # desactivar botones sin selección
        self.btn_actualizar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)
