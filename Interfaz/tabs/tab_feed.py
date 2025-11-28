from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel,
    QTableWidget, QTableWidgetItem, QComboBox, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHeaderView

from database.postgres import (
    obtener_publicaciones, crear_publicacion,
    actualizar_publicacion, eliminar_publicacion,
    obtener_usuarios, obtener_feed
)

from database.neo4j_conn import migrar_desde_postgres

class TabFeed(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Titulo
        titulo = QLabel("Gestión de Publicaciones")
        titulo.setProperty("class", "title")
        layout.addWidget(titulo)

        descripcion = QLabel("Crea, edita y visualiza publicaciones de la red social")
        descripcion.setProperty("class", "description")
        layout.addWidget(descripcion)

        layout.addSpacing(10)

        # Seccion de publicaciones
        seccion_posts = QLabel("Administrar Publicaciones")
        seccion_posts.setProperty("class", "section-title")
        layout.addWidget(seccion_posts)

        # Tabla de posts
        self.tabla_posts = QTableWidget()
        self.tabla_posts.setColumnCount(3)
        self.tabla_posts.setHorizontalHeaderLabels(["ID", "Contenido", "Autor_ID"])
        self.tabla_posts.cellClicked.connect(self.cargar_post_en_formulario)
        self.tabla_posts.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla_posts)

        # Formulario para crear/editar posts
        form = QHBoxLayout()
        form.setSpacing(10)

        self.input_texto = QLineEdit()
        self.input_texto.setPlaceholderText("¿Qué estás pensando?")

        self.combo_autor = QComboBox()
        self.cargar_usuarios_en_combo()

        form.addWidget(self.input_texto)
        form.addWidget(self.combo_autor)

        layout.addLayout(form)

        # Botones crud
        botones = QHBoxLayout()
        botones.setSpacing(10)

        btn_refrescar = QPushButton("🔄 Refrescar")
        btn_refrescar.setProperty("class", "secondary")
        btn_refrescar.clicked.connect(self.actualizar_todo)

        btn_crear = QPushButton("➕ Crear Publicación")
        btn_crear.setProperty("class", "success")
        btn_crear.clicked.connect(self.crear_post)

        btn_actualizar = QPushButton("✏️ Actualizar")
        btn_actualizar.setProperty("class", "warning")
        btn_actualizar.clicked.connect(self.actualizar_post)

        btn_eliminar = QPushButton("🗑️ Eliminar")
        btn_eliminar.setProperty("class", "danger")
        btn_eliminar.clicked.connect(self.eliminar_post)

        botones.addWidget(btn_refrescar)
        botones.addStretch()
        botones.addWidget(btn_crear)
        botones.addWidget(btn_actualizar)
        botones.addWidget(btn_eliminar)

        layout.addLayout(botones)

        # Guardar referencias a los botones
        self.btn_actualizar_post = btn_actualizar
        self.btn_eliminar_post = btn_eliminar

        # Desactivar botones al inicio
        self.btn_actualizar_post.setEnabled(False)
        self.btn_eliminar_post.setEnabled(False)

        # Cargar los posts inicialmente
        self.cargar_posts()

        # Vista feed
        layout.addSpacing(15)
        seccion_feed = QLabel("Feed de Noticias")
        seccion_feed.setProperty("class", "section-title")
        layout.addWidget(seccion_feed)

        self.tabla_feed = QTableWidget()
        self.tabla_feed.setColumnCount(4)
        self.tabla_feed.setHorizontalHeaderLabels(
            ["Usuario", "Contenido", "Fecha", "Comentarios"]
        )
        self.tabla_feed.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla_feed)

        btn_feed = QPushButton("🔄 Refrescar Feed")
        btn_feed.setProperty("class", "secondary")
        btn_feed.clicked.connect(self.actualizar_todo)
        layout.addWidget(btn_feed)

        self.cargar_feed()

    def mensaje(self, msg_text):
        msg = QMessageBox()
        msg.setWindowTitle("Información")
        msg.setText(msg_text)
        msg.setWindowIcon(QIcon("ui/AmigosDB.png"))
        msg.exec_()

    # Crud posts
    def cargar_usuarios_en_combo(self):
        self.combo_autor.clear()
        for u in obtener_usuarios():
            self.combo_autor.addItem(f"{u[0]} - {u[1]}", u[0])

    def cargar_posts(self):
        posts = obtener_publicaciones()
        self.tabla_posts.setRowCount(len(posts))

        for row, p in enumerate(posts):
            self.tabla_posts.setItem(row, 0, QTableWidgetItem(str(p[0])))
            self.tabla_posts.setItem(row, 1, QTableWidgetItem(p[1]))
            self.tabla_posts.setItem(row, 2, QTableWidgetItem(str(p[2])))

        self.cargar_usuarios_en_combo()

    def cargar_post_en_formulario(self, row, col):
        self.input_texto.setText(self.tabla_posts.item(row, 1).text())
        autor_id = self.tabla_posts.item(row, 2).text()

        self.cargar_usuarios_en_combo()

        for i in range(self.combo_autor.count()):
            if str(self.combo_autor.itemData(i)) == autor_id:
                self.combo_autor.setCurrentIndex(i)
                break

        # activar botones cuando hay selección
        self.btn_actualizar_post.setEnabled(True)
        self.btn_eliminar_post.setEnabled(True)

    def crear_post(self):
        texto = self.input_texto.text().strip()
        autor = self.combo_autor.currentData()

        if not texto:
            self.mensaje("Debe ingresar contenido.")
            return

        crear_publicacion(texto, autor)
        migrar_desde_postgres()
        self.actualizar_todo()
        self.mensaje("Post creado.")
        self.limpiar_formulario()

    def actualizar_post(self):
        row = self.tabla_posts.currentRow()
        if row < 0:
            self.mensaje("Seleccione un post.")
            return

        id_post = int(self.tabla_posts.item(row, 0).text())
        texto = self.input_texto.text().strip()

        if not texto:
            self.mensaje("Debe ingresar contenido.")
            return

        actualizar_publicacion(id_post, texto)
        migrar_desde_postgres()
        self.actualizar_todo()
        self.mensaje("Post actualizado.")
        self.limpiar_formulario()

    def eliminar_post(self):
        row = self.tabla_posts.currentRow()
        if row < 0:
            self.mensaje("Seleccione un post.")
            return

        id_post = int(self.tabla_posts.item(row, 0).text())
        eliminar_publicacion(id_post)
        migrar_desde_postgres()
        self.actualizar_todo()
        self.mensaje("Post eliminado.")
        self.limpiar_formulario()

    # Vista feed
    def cargar_feed(self):
        feed = obtener_feed()
        self.tabla_feed.setRowCount(len(feed))

        for row, f in enumerate(feed):
            self.tabla_feed.setItem(row, 0, QTableWidgetItem(f[0]))
            self.tabla_feed.setItem(row, 1, QTableWidgetItem(f[1]))
            self.tabla_feed.setItem(row, 2, QTableWidgetItem(str(f[2])))
            self.tabla_feed.setItem(row, 3, QTableWidgetItem(str(f[3])))

    # Actualizar todos los registros
    def actualizar_todo(self):
        self.cargar_usuarios_en_combo()
        self.cargar_posts()
        self.cargar_feed()

    # Limpiar formulario
    def limpiar_formulario(self):
        self.input_texto.clear()
        self.combo_autor.setCurrentIndex(0)
        self.tabla_posts.clearSelection()

        # desactivar botones al limpiar
        self.btn_actualizar_post.setEnabled(False)
        self.btn_eliminar_post.setEnabled(False)