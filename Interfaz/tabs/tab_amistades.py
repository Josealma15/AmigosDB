from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtGui import QIcon
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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Titulo
        titulo = QLabel("Gestión de Amistades")
        titulo.setProperty("class", "title")
        layout.addWidget(titulo)

        descripcion = QLabel("Administra las relaciones de amistad entre usuarios")
        descripcion.setProperty("class", "description")
        layout.addWidget(descripcion)

        layout.addSpacing(10)

        # Seccion crear nueva amistad
        seccion1 = QLabel("Crear Nueva Amistad")
        seccion1.setProperty("class", "section-title")
        layout.addWidget(seccion1)

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

        self.btn_crear = QPushButton("➕ Enviar Solicitud de Amistad")
        self.btn_crear.setProperty("class", "success")
        self.btn_crear.setEnabled(False)
        self.btn_crear.clicked.connect(self.crear_amistad)
        layout.addWidget(self.btn_crear)

        self.lbl_msg = QLabel("")
        layout.addWidget(self.lbl_msg)

        layout.addSpacing(15)

        # Seccion mis amistades
        seccion2 = QLabel("Mis Amistades")
        seccion2.setProperty("class", "section-title")
        layout.addWidget(seccion2)

        yo_layout = QHBoxLayout()
        yo_layout.addWidget(QLabel("Yo soy:"))
        self.combo_yo = QComboBox()
        yo_layout.addWidget(self.combo_yo)
        layout.addLayout(yo_layout)

        self.combo_yo.currentIndexChanged.connect(self.cargar_mis_amistades)

        # Tabla de amistades
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)  # +1 para ID solicitante (oculto)
        self.tabla.setHorizontalHeaderLabels(["ID Amistad", "Amigo", "Email", "Estado", "Fecha", "SolicitanteID"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setColumnHidden(5, True)  # Ocultar columna ID solicitante
        layout.addWidget(self.tabla)

        # Boton refrescar
        self.btn_refresh = QPushButton("🔄 Refrescar Amistades")
        self.btn_refresh.setProperty("class", "secondary")
        self.btn_refresh.clicked.connect(self.cargar_mis_amistades)
        layout.addWidget(self.btn_refresh)

        # Botones de accion
        opciones = QHBoxLayout()

        self.btn_aceptar = QPushButton("✅ Aceptar")
        self.btn_aceptar.setProperty("class", "success")
        self.btn_aceptar.clicked.connect(lambda: self.cambiar_estado("ACEPTADA"))
        opciones.addWidget(self.btn_aceptar)

        self.btn_rechazar = QPushButton("❌ Rechazar")
        self.btn_rechazar.setProperty("class", "danger")
        self.btn_rechazar.clicked.connect(lambda: self.cambiar_estado("RECHAZADA"))
        opciones.addWidget(self.btn_rechazar)

        self.btn_bloquear = QPushButton("🚫 Bloquear")
        self.btn_bloquear.setProperty("class", "warning")
        self.btn_bloquear.clicked.connect(lambda: self.cambiar_estado("BLOQUEADA"))
        opciones.addWidget(self.btn_bloquear)

        self.btn_eliminar = QPushButton("🗑️ Eliminar")
        self.btn_eliminar.setProperty("class", "danger")
        self.btn_eliminar.clicked.connect(lambda: self.cambiar_estado("ELIMINADA"))
        opciones.addWidget(self.btn_eliminar)

        self.btn_desbloquear = QPushButton("🔓 Desbloquear")
        self.btn_desbloquear.clicked.connect(lambda: self.cambiar_estado("PENDIENTE"))
        opciones.addWidget(self.btn_desbloquear)

        layout.addLayout(opciones)

        # Desactivar botones al inicio
        self.btn_aceptar.setEnabled(False)
        self.btn_rechazar.setEnabled(False)
        self.btn_bloquear.setEnabled(False)
        self.btn_eliminar.setEnabled(False)
        self.btn_desbloquear.setEnabled(False)

        self.tabla.itemSelectionChanged.connect(self.habilitar_botones)

        # Cargar datos iniciales
        self.cargar_usuarios()

    def mensaje(self, texto):
        # Mostrar mensaje emergente
        msg = QMessageBox()
        msg.setWindowTitle("Información")
        msg.setText(texto)
        msg.setWindowIcon(QIcon("ui/AmigosDB.png"))
        msg.exec_()

    def cargar_usuarios(self):
        # Cargar usuarios en los combos
        usuarios = obtener_usuarios()

        self.combo_user1.clear()
        self.combo_user2.clear()
        self.combo_yo.clear()

        for u in usuarios:
            texto = f"{u[0]} - {u[1]}"
            self.combo_user1.addItem(texto, u[0])
            self.combo_user2.addItem(texto, u[0])
            self.combo_yo.addItem(texto, u[0])

    def verificar_creacion(self):
        # Verificar que no se seleccione el mismo usuario dos veces
        id1 = self.combo_user1.currentData()
        id2 = self.combo_user2.currentData()

        if id1 and id2 and id1 != id2:
            self.btn_crear.setEnabled(True)
            self.lbl_msg.setText("")
        else:
            self.btn_crear.setEnabled(False)
            if id1 == id2:
                self.lbl_msg.setText("No puede crear amistad consigo mismo.")

    def crear_amistad(self):
        # Crear una nueva solicitud de amistad
        id1 = self.combo_user1.currentData()
        id2 = self.combo_user2.currentData()

        if not id1 or not id2:
            self.mensaje("Seleccione dos usuarios.")
            return

        try:
            resultado = crear_amistad_procedure(id1, id2)
            migrar_desde_postgres()
            self.cargar_mis_amistades()
            self.refrescar_recomendaciones()
            self.mensaje(f"Solicitud enviada. {resultado}")
        except Exception as e:
            self.mensaje(f"Error: {str(e)}")

    def cargar_mis_amistades(self):
        # Cargar las amistades del usuario seleccionado
        id_usuario = self.combo_yo.currentData()

        if not id_usuario:
            return

        amistades = obtener_amistades_por_usuario(id_usuario)
        self.tabla.setRowCount(len(amistades))

        for row, a in enumerate(amistades):
            self.tabla.setItem(row, 0, QTableWidgetItem(str(a[0])))
            self.tabla.setItem(row, 1, QTableWidgetItem(a[1]))
            self.tabla.setItem(row, 2, QTableWidgetItem(a[2]))
            self.tabla.setItem(row, 3, QTableWidgetItem(a[3]))
            self.tabla.setItem(row, 4, QTableWidgetItem(str(a[4])))
            self.tabla.setItem(row, 5, QTableWidgetItem(str(a[5])))  # ID Solicitante

    def habilitar_botones(self):
        # Habilitar botones según el estado de la amistad
        row = self.tabla.currentRow()
        if row < 0:
            self.desactivar_botones()
            return

        estado = self.tabla.item(row, 3).text().strip()
        id_solicitante = int(self.tabla.item(row, 5).text())
        id_usuario_actual = self.combo_yo.currentData()

        # Solo el receptor puede aceptar (si yo NO soy el solicitante)
        soy_receptor = (id_usuario_actual != id_solicitante)

        if estado == "PENDIENTE":
            self.btn_aceptar.setEnabled(soy_receptor)
            self.btn_rechazar.setEnabled(soy_receptor)
            self.btn_bloquear.setEnabled(False)
            self.btn_eliminar.setEnabled(True)
            self.btn_desbloquear.setEnabled(False)

        elif estado == "ACEPTADA":
            self.btn_aceptar.setEnabled(False)
            self.btn_rechazar.setEnabled(False)
            self.btn_bloquear.setEnabled(True)
            self.btn_eliminar.setEnabled(True)
            self.btn_desbloquear.setEnabled(False)

        elif estado == "RECHAZADA":
            self.btn_aceptar.setEnabled(True)   # Permitir reconsiderar
            self.btn_rechazar.setEnabled(False)
            self.btn_bloquear.setEnabled(True)
            self.btn_eliminar.setEnabled(True)
            self.btn_desbloquear.setEnabled(False)

        elif estado == "BLOQUEADA":
            self.btn_aceptar.setEnabled(False)
            self.btn_rechazar.setEnabled(False)
            self.btn_bloquear.setEnabled(False)
            self.btn_eliminar.setEnabled(True)
            self.btn_desbloquear.setEnabled(True)

        else:
            self.desactivar_botones()

    def desactivar_botones(self):
        self.btn_aceptar.setEnabled(False)
        self.btn_rechazar.setEnabled(False)
        self.btn_bloquear.setEnabled(False)
        self.btn_eliminar.setEnabled(False)
        self.btn_desbloquear.setEnabled(False)

    def mousePressEvent(self, event):
        self.tabla.clearSelection()
        self.desactivar_botones()
        super().mousePressEvent(event)

    def cambiar_estado(self, nuevo_estado):
        # Cambiar el estado de una amistad
        row = self.tabla.currentRow()
        if row < 0:
            self.mensaje("Seleccione una amistad primero.")
            return

        id_amistad = int(self.tabla.item(row, 0).text())

        try:
            actualizar_estado_amistad(id_amistad, nuevo_estado)
            migrar_desde_postgres()
            self.cargar_mis_amistades()
            self.refrescar_recomendaciones()
            self.mensaje(f"Estado actualizado a: {nuevo_estado}")
        except Exception as e:
            self.mensaje(f"Error: {str(e)}")

    def refrescar_recomendaciones(self):
        # Refrescar la pestaña de recomendaciones
        parent_window = self.parent().parent()

        try:
            from tabs.tab_recomendaciones import TabRecomendaciones
            for tab in parent_window.findChildren(TabRecomendaciones):
                try:
                    tab.cargar_usuarios()
                    tab.cargar_recomendaciones()
                except:
                    pass
        except Exception as e:
            print(f"Error refrescando recomendaciones: {e}")
