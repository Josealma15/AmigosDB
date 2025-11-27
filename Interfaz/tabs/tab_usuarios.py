from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHeaderView

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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Titulo
        titulo = QLabel("Gestión de Usuarios")
        titulo.setProperty("class", "title")
        layout.addWidget(titulo)

        descripcion = QLabel("Administra los usuarios de la red social")
        descripcion.setProperty("class", "description")
        layout.addWidget(descripcion)

        layout.addSpacing(10)

        # Tabla de usuarios
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Email", "País"])
        self.tabla.cellClicked.connect(self.cargar_usuario_en_formulario)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla)

        # Seccion de formulario
        seccion_form = QLabel("Datos del Usuario")
        seccion_form.setProperty("class", "section-title")
        layout.addWidget(seccion_form)

        # Formulario de entrada
        form_layout = QHBoxLayout()
        form_layout.setSpacing(10)

        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre completo")

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("correo@ejemplo.com")

        self.input_pais = QLineEdit()
        self.input_pais.setPlaceholderText("País")

        form_layout.addWidget(self.input_nombre)
        form_layout.addWidget(self.input_email)
        form_layout.addWidget(self.input_pais)

        layout.addLayout(form_layout)

        # Botones de accion
        botones = QHBoxLayout()
        botones.setSpacing(10)

        btn_cargar = QPushButton("🔄 Refrescar")
        btn_cargar.setProperty("class", "secondary")
        btn_cargar.clicked.connect(self.cargar_usuarios)

        btn_agregar = QPushButton("➕ Agregar Usuario")
        btn_agregar.setProperty("class", "success")
        btn_agregar.clicked.connect(self.agregar_usuario)

        btn_actualizar = QPushButton("✏️ Actualizar")
        btn_actualizar.setProperty("class", "warning")
        btn_actualizar.clicked.connect(self.actualizar_usuario_btn)

        btn_eliminar = QPushButton("🗑️ Eliminar")
        btn_eliminar.setProperty("class", "danger")
        btn_eliminar.clicked.connect(self.eliminar_usuario_btn)

        botones.addWidget(btn_cargar)
        botones.addStretch()
        botones.addWidget(btn_agregar)
        botones.addWidget(btn_actualizar)
        botones.addWidget(btn_eliminar)

        layout.addLayout(botones)

        # Referencias a botones
        self.btn_actualizar = btn_actualizar
        self.btn_eliminar = btn_eliminar

        # Desactivar botones al inicio
        self.btn_actualizar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)

        # Cargar usuarios
        self.cargar_usuarios()

    def mensaje(self, texto):
        # Mostrar mensaje emergente
        msg = QMessageBox()
        msg.setWindowTitle("Información")
        msg.setText(texto)
        msg.setWindowIcon(QIcon("ui/AmigosDB.png"))
        msg.exec_()

    def cargar_usuarios(self):
        # Obtener usuarios de la base de datos y mostrarlos en la tabla
        usuarios = obtener_usuarios()
        self.tabla.setRowCount(len(usuarios))

        for row, u in enumerate(usuarios):
            self.tabla.setItem(row, 0, QTableWidgetItem(str(u[0])))
            self.tabla.setItem(row, 1, QTableWidgetItem(u[1]))
            self.tabla.setItem(row, 2, QTableWidgetItem(u[2]))
            self.tabla.setItem(row, 3, QTableWidgetItem(u[3]))

    def cargar_usuario_en_formulario(self, row, col):
        # Cargar datos del usuario seleccionado en el formulario
        self.input_nombre.setText(self.tabla.item(row, 1).text())
        self.input_email.setText(self.tabla.item(row, 2).text())
        self.input_pais.setText(self.tabla.item(row, 3).text())

        # Activar botones de actualizar y eliminar
        self.btn_actualizar.setEnabled(True)
        self.btn_eliminar.setEnabled(True)

    def agregar_usuario(self):
        # Crear un nuevo usuario
        nombre = self.input_nombre.text().strip()
        email  = self.input_email.text().strip()
        pais   = self.input_pais.text().strip()

        if not nombre or not email or not pais:
            self.mensaje("Debe llenar todos los campos.")
            return

        crear_usuario(nombre, email, pais)
        migrar_desde_postgres()

        self.cargar_usuarios()
        self.refrescar_otras_pestanas()
        self.mensaje("Usuario agregado correctamente.")
        self.limpiar_formulario()

    def actualizar_usuario_btn(self):
        # Actualizar un usuario existente
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
        self.refrescar_otras_pestanas()
        self.mensaje("Usuario actualizado.")
        self.limpiar_formulario()

    def eliminar_usuario_btn(self):
        # Eliminar un usuario
        row = self.tabla.currentRow()
        if row < 0:
            self.mensaje("Seleccione un usuario primero.")
            return

        id_usuario = int(self.tabla.item(row, 0).text())
        eliminar_usuario(id_usuario)
        migrar_desde_postgres()
        self.cargar_usuarios()
        self.refrescar_otras_pestanas()
        self.mensaje("Usuario eliminado.")
        self.limpiar_formulario()

    def limpiar_formulario(self):
        # Limpiar campos del formulario
        self.input_nombre.clear()
        self.input_email.clear()
        self.input_pais.clear()
        self.tabla.clearSelection()

        # Desactivar botones
        self.btn_actualizar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)

    def refrescar_otras_pestanas(self):
        # Refrescar las otras pestañas cuando cambian los usuarios
        parent_window = self.parent().parent()

        try:
            # Refrescar amistades
            from tabs.tab_amistades import TabAmistades
            for tab in parent_window.findChildren(TabAmistades):
                try:
                    tab.cargar_usuarios()
                except:
                    pass

            # Refrescar recomendaciones
            from tabs.tab_recomendaciones import TabRecomendaciones
            for tab in parent_window.findChildren(TabRecomendaciones):
                try:
                    tab.cargar_usuarios()
                except:
                    pass

            # Refrescar feed
            from tabs.tab_feed import TabFeed
            for tab in parent_window.findChildren(TabFeed):
                try:
                    tab.cargar_usuarios_en_combo()
                except:
                    pass

        except Exception as e:
            print(f"Error refrescando pestañas: {e}")
