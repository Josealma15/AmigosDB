from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox
)

from PyQt5.QtWidgets import QHeaderView

from database.postgres import (
    obtener_usuarios,
    obtener_amistades,
    crear_amistad_procedure,
    actualizar_estado_amistad,
    obtener_amistades_por_usuario
)

from database.neo4j_conn import migrar_desde_postgres


class TabAmistades(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # ============================================================
        # SECCIÓN 1 — CREAR NUEVA AMISTAD
        # ============================================================

        layout.addWidget(QLabel("Crear nueva amistad"))

        crear_layout = QHBoxLayout()

        self.combo_user1 = QComboBox()
        self.combo_user2 = QComboBox()

        crear_layout.addWidget(QLabel("Usuario 1:"))
        crear_layout.addWidget(self.combo_user1)

        crear_layout.addWidget(QLabel("Usuario 2:"))
        crear_layout.addWidget(self.combo_user2)

        layout.addLayout(crear_layout)

        self.combo_user1.currentIndexChanged.connect(self.verificar_creacion)
        self.combo_user2.currentIndexChanged.connect(self.verificar_creacion)

        self.btn_crear = QPushButton("Enviar solicitud de amistad")
        self.btn_crear.setEnabled(False)
        self.btn_crear.clicked.connect(self.crear_amistad)
        layout.addWidget(self.btn_crear)

        self.lbl_msg = QLabel("")
        layout.addWidget(self.lbl_msg)

        # ============================================================
        # SECCIÓN 2 — GESTIONAR MIS AMISTADES
        # ============================================================

        layout.addWidget(QLabel("\nMis amistades"))

        yo_layout = QHBoxLayout()
        yo_layout.addWidget(QLabel("Yo soy:"))
        self.combo_mi_usuario = QComboBox()
        yo_layout.addWidget(self.combo_mi_usuario)
        layout.addLayout(yo_layout)

        self.combo_mi_usuario.currentIndexChanged.connect(self.cargar_mis_amistades)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["ID", "Amigo", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.cellClicked.connect(self.seleccionar_amistad)
        layout.addWidget(self.tabla)

        # Botón Refrescar
        btn_refresh = QPushButton("Refrescar amistades")
        btn_refresh.clicked.connect(self.cargar_mis_amistades)
        layout.addWidget(btn_refresh)

        # Botones acción
        opciones = QHBoxLayout()

        self.btn_aceptar = QPushButton("Aceptar")
        self.btn_aceptar.clicked.connect(lambda: self.cambiar_estado("ACEPTADA"))
        opciones.addWidget(self.btn_aceptar)

        self.btn_rechazar = QPushButton("Rechazar")
        self.btn_rechazar.clicked.connect(lambda: self.cambiar_estado("RECHAZADA"))
        opciones.addWidget(self.btn_rechazar)

        self.btn_bloquear = QPushButton("Bloquear")
        self.btn_bloquear.clicked.connect(lambda: self.cambiar_estado("BLOQUEADA"))
        opciones.addWidget(self.btn_bloquear)

        self.btn_eliminar = QPushButton("Eliminar amistad")
        self.btn_eliminar.clicked.connect(lambda: self.cambiar_estado("ELIMINADA"))
        opciones.addWidget(self.btn_eliminar)

        self.btn_desbloquear = QPushButton("Desbloquear")
        self.btn_desbloquear.clicked.connect(lambda: self.cambiar_estado("PENDIENTE"))
        opciones.addWidget(self.btn_desbloquear)

        layout.addLayout(opciones)

        self.fila_seleccionada = -1
        self.desactivar_botones()

        self.cargar_usuarios()

    # ============================================================
    # UTILS
    # ============================================================

    def mensaje(self, t):
        QMessageBox.information(self, "Información", t)

    # ============================================================
    # CREAR AMISTAD
    # ============================================================

    def cargar_usuarios(self):
        usuarios = obtener_usuarios()

        self.combo_user1.clear()
        self.combo_user2.clear()
        self.combo_mi_usuario.clear()

        for u in usuarios:
            text = f"{u[0]} - {u[1]}"
            self.combo_user1.addItem(text, u[0])
            self.combo_user2.addItem(text, u[0])
            self.combo_mi_usuario.addItem(text, u[0])

    def existe_amistad(self, id1, id2):
        for a in obtener_amistades():
            if (a[4] == id1 and a[5] == id2) or (a[4] == id2 and a[5] == id1):
                return True
        return False

    def verificar_creacion(self):
        id1 = self.combo_user1.currentData()
        id2 = self.combo_user2.currentData()

        if not id1 or not id2 or id1 == id2:
            self.btn_crear.setEnabled(False)
            return

        if self.existe_amistad(id1, id2):
            self.btn_crear.setEnabled(False)
            self.lbl_msg.setText("Ya existe una relación de amistad.")
            return

        self.lbl_msg.setText("")
        self.btn_crear.setEnabled(True)

    def crear_amistad(self):
        id1 = self.combo_user1.currentData()
        id2 = self.combo_user2.currentData()

        msg = crear_amistad_procedure(id1, id2)
        self.lbl_msg.setText(msg)

        migrar_desde_postgres()
        self.cargar_mis_amistades()

    # ============================================================
    # MIS AMISTADES
    # ============================================================

    def cargar_mis_amistades(self):
        id_usuario = self.combo_mi_usuario.currentData()

        datos = obtener_amistades_por_usuario(id_usuario)

        datos = [a for a in datos if a[2] != "ELIMINADA"]

        self.tabla.setRowCount(len(datos))

        for row, a in enumerate(datos):
            self.tabla.setItem(row, 0, QTableWidgetItem(str(a[0])))
            self.tabla.setItem(row, 1, QTableWidgetItem(a[1]))
            self.tabla.setItem(row, 2, QTableWidgetItem(a[2]))

        self.fila_seleccionada = -1
        self.desactivar_botones()

    # ============================================================
    # SELECCIÓN Y BOTONES
    # ============================================================

    def desactivar_botones(self):
        self.btn_aceptar.setEnabled(False)
        self.btn_rechazar.setEnabled(False)
        self.btn_bloquear.setEnabled(False)
        self.btn_eliminar.setEnabled(False)
        self.btn_desbloquear.setEnabled(False)

    def seleccionar_amistad(self, row, col):
        self.fila_seleccionada = row
        estado = self.tabla.item(row, 2).text()

        id_usuario = self.combo_mi_usuario.currentData()

        self.desactivar_botones()

        id_amistad = int(self.tabla.item(row, 0).text())
        fila = obtener_amistades_por_usuario(id_usuario)
        fila = [x for x in fila if x[0] == id_amistad][0]

        solicitante = fila[3]
        receptor = fila[4]

        soy_solicitante = id_usuario == solicitante
        soy_receptor = id_usuario == receptor

        if estado == "PENDIENTE":
            if soy_receptor:
                self.btn_aceptar.setEnabled(True)
                self.btn_rechazar.setEnabled(True)
            if soy_solicitante:
                self.btn_eliminar.setEnabled(True)

        elif estado == "ACEPTADA":
            self.btn_bloquear.setEnabled(True)
            self.btn_eliminar.setEnabled(True)

        elif estado == "BLOQUEADA":
            if soy_solicitante:
                self.btn_desbloquear.setEnabled(True)

        elif estado == "RECHAZADA":
            if soy_receptor:
                self.btn_aceptar.setEnabled(True)

    # ============================================================
    # CAMBIO DE ESTADO
    # ============================================================

    def cambiar_estado(self, nuevo):
        if self.fila_seleccionada < 0:
            self.mensaje("Seleccione una amistad.")
            return

        id_amistad = int(self.tabla.item(self.fila_seleccionada, 0).text())

        actualizar_estado_amistad(id_amistad, nuevo)
        migrar_desde_postgres()

        self.cargar_mis_amistades()

        self.mensaje(f"Estado cambiado a {nuevo}.")
