# config_dialog.py
import sqlite3
<<<<<<< HEAD
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTabWidget, QWidget, QTableView, QPushButton, QHBoxLayout, QHeaderView, QMessageBox, QDialogButtonBox, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox)
from PySide6.QtSql import QSqlDatabase, QSqlTableModel
from PySide6.QtCore import Qt
=======
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTabWidget, QWidget,
                             QTableView, QPushButton, QHBoxLayout, QHeaderView,
                             QMessageBox, QDialogButtonBox, QFormLayout,
                             QLineEdit, QComboBox, QDoubleSpinBox)
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtCore import Qt
>>>>>>> 0196544f8e5655a970364ed0b9eed3d8ba9459cb

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
<<<<<<< HEAD
        self.setWindowTitle("Configuración de Costes"); self.setMinimumSize(800, 600)
        self.db = QSqlDatabase.database()
        if not self.db.isOpen(): QMessageBox.critical(self, "Error", "La conexión a la base de datos no está disponible."); return
        main_layout = QVBoxLayout(self); self.tabs = QTabWidget(); main_layout.addWidget(self.tabs)
        self.tab_materiales = QWidget(); self.modelo_materiales = self.crear_modelo_tabla("Materiales", ["ID", "Tipo", "Subtipo", "Precio Coste", "Unidad"]); self.crear_pestana(self.tab_materiales, self.modelo_materiales, self.abrir_dialogo_material)
        self.tab_maquinaria = QWidget(); self.modelo_maquinaria = self.crear_modelo_tabla("Maquinaria", ["ID", "Nombre Máquina", "Coste por Hora"]); self.crear_pestana(self.tab_maquinaria, self.modelo_maquinaria, self.abrir_dialogo_maquinaria)
        self.tab_personal = QWidget(); self.modelo_personal = self.crear_modelo_tabla("RolesPersonal", ["ID", "Nombre del Rol", "Coste por Hora"]); self.crear_pestana(self.tab_personal, self.modelo_personal, self.abrir_dialogo_personal)
        self.tabs.addTab(self.tab_materiales, "Materiales"); self.tabs.addTab(self.tab_maquinaria, "Maquinaria"); self.tabs.addTab(self.tab_personal, "Personal")

    def crear_modelo_tabla(self, nombre_tabla, cabeceras):
        modelo = QSqlTableModel(self, self.db); modelo.setTable(nombre_tabla); modelo.select()
        for i, cabecera in enumerate(cabeceras): modelo.setHeaderData(i, Qt.Orientation.Horizontal, cabecera)
        return modelo

    def crear_pestana(self, tab_widget, modelo, funcion_anadir):
        layout = QVBoxLayout(tab_widget); tabla = QTableView(); tabla.setModel(modelo)
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); tabla.hideColumn(0); layout.addWidget(tabla)
        botones_layout = QHBoxLayout(); botones_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        btn_anadir = QPushButton("Añadir Nuevo"); btn_editar = QPushButton("Editar Seleccionado"); btn_eliminar = QPushButton("Eliminar Seleccionado")
        botones_layout.addWidget(btn_anadir); botones_layout.addWidget(btn_editar); botones_layout.addWidget(btn_eliminar); layout.addLayout(botones_layout)
        btn_anadir.clicked.connect(funcion_anadir)

    def abrir_dialogo_material(self):
        dialogo = QDialog(self); dialogo.setWindowTitle("Añadir Nuevo Material"); layout = QFormLayout(dialogo)
        combo_tipo = QComboBox(); combo_tipo.addItems(["fleje", "madera", "goma"]); input_subtipo = QLineEdit()
        input_precio = QDoubleSpinBox(); input_precio.setDecimals(2); input_precio.setMaximum(9999.99); input_precio.setSuffix(" €")
        combo_unidad = QComboBox(); combo_unidad.addItems(["m", "m2"])
        layout.addRow("Tipo:", combo_tipo); layout.addRow("Descripción:", input_subtipo); layout.addRow("Precio:", input_precio); layout.addRow("Unidad:", combo_unidad)
        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel); botones.accepted.connect(dialogo.accept); botones.rejected.connect(dialogo.reject); layout.addRow(botones)
        if dialogo.exec():
            tipo, subtipo, precio, unidad = combo_tipo.currentText(), input_subtipo.text(), input_precio.value(), combo_unidad.currentText()
            if not subtipo: QMessageBox.warning(self, "Campo Vacío", "La descripción no puede estar vacía."); return
            conn = sqlite3.connect("troquelgest.db"); cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO Materiales (tipo_material, subtipo, precio_coste, unidad) VALUES (?, ?, ?, ?)", (tipo, subtipo, precio, unidad))
                conn.commit(); self.modelo_materiales.select()
            except sqlite3.Error as e: QMessageBox.critical(self, "Error", f"{e}")
            finally: conn.close()

    def abrir_dialogo_maquinaria(self):
        dialogo = QDialog(self); dialogo.setWindowTitle("Añadir Máquina"); layout = QFormLayout(dialogo)
        input_nombre = QLineEdit(); input_coste = QDoubleSpinBox(); input_coste.setDecimals(2); input_coste.setMaximum(999.99); input_coste.setSuffix(" €/hora")
        layout.addRow("Nombre:", input_nombre); layout.addRow("Coste/Hora:", input_coste)
        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel); botones.accepted.connect(dialogo.accept); botones.rejected.connect(dialogo.reject); layout.addRow(botones)
        if dialogo.exec():
            nombre, coste = input_nombre.text(), input_coste.value()
            if not nombre: QMessageBox.warning(self, "Campo Vacío", "El nombre no puede estar vacío."); return
            conn = sqlite3.connect("troquelgest.db"); cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO Maquinaria (nombre_maquina, coste_por_hora) VALUES (?, ?)", (nombre, coste))
                conn.commit(); self.modelo_maquinaria.select()
            except sqlite3.Error as e: QMessageBox.critical(self, "Error", f"{e}")
            finally: conn.close()

    def abrir_dialogo_personal(self):
        dialogo = QDialog(self); dialogo.setWindowTitle("Añadir Rol Personal"); layout = QFormLayout(dialogo)
        input_rol = QLineEdit(); input_coste = QDoubleSpinBox(); input_coste.setDecimals(2); input_coste.setMaximum(999.99); input_coste.setSuffix(" €/hora")
        layout.addRow("Rol:", input_rol); layout.addRow("Coste/Hora:", input_coste)
        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel); botones.accepted.connect(dialogo.accept); botones.rejected.connect(dialogo.reject); layout.addRow(botones)
        if dialogo.exec():
            rol, coste = input_rol.text(), input_coste.value()
            if not rol: QMessageBox.warning(self, "Campo Vacío", "El nombre del rol no puede estar vacío."); return
            conn = sqlite3.connect("troquelgest.db"); cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO RolesPersonal (nombre_rol, coste_por_hora) VALUES (?, ?)", (rol, coste))
                conn.commit(); self.modelo_personal.select()
            except sqlite3.Error as e: QMessageBox.critical(self, "Error", f"{e}")
            finally: conn.close()
=======
        self.setWindowTitle("Configuración de Costes")
        self.setMinimumSize(800, 600)

        # AHORA MÁS SENCILLO: Obtenemos la conexión que ya está abierta
        self.db = QSqlDatabase.database()
        if not self.db.isOpen():
            QMessageBox.critical(self, "Error", "La conexión a la base de datos no está disponible.")
            return

        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # El resto del código no cambia...
        # Pestaña de Materiales
        self.tab_materiales = QWidget()
        self.modelo_materiales = self.crear_modelo_tabla("Materiales", ["ID", "Tipo", "Subtipo", "Precio Coste", "Unidad"])
        self.vista_materiales = self.crear_pestana(self.tab_materiales, self.modelo_materiales, self.abrir_dialogo_material)

        # Pestaña de Maquinaria
        self.tab_maquinaria = QWidget()
        self.modelo_maquinaria = self.crear_modelo_tabla("Maquinaria", ["ID", "Nombre Máquina", "Coste por Hora"])
        self.vista_maquinaria = self.crear_pestana(self.tab_maquinaria, self.modelo_maquinaria, self.abrir_dialogo_maquinaria)

        # Pestaña de Personal
        self.tab_personal = QWidget()
        self.modelo_personal = self.crear_modelo_tabla("RolesPersonal", ["ID", "Nombre del Rol", "Coste por Hora"])
        self.vista_personal = self.crear_pestana(self.tab_personal, self.modelo_personal, self.abrir_dialogo_personal)

        self.tabs.addTab(self.tab_materiales, "Materiales")
        self.tabs.addTab(self.tab_maquinaria, "Maquinaria")
        self.tabs.addTab(self.tab_personal, "Personal")

    def crear_modelo_tabla(self, nombre_tabla, cabeceras):
        modelo = QSqlTableModel(self, self.db)
        modelo.setTable(nombre_tabla)
        modelo.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        modelo.select()
        for i, cabecera in enumerate(cabeceras):
            modelo.setHeaderData(i, Qt.Orientation.Horizontal, cabecera)
        return modelo

    def crear_pestana(self, tab_widget, modelo, funcion_anadir):
        layout = QVBoxLayout(tab_widget)
        tabla = QTableView()
        tabla.setModel(modelo)
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tabla.hideColumn(0)
        layout.addWidget(tabla)

        botones_layout = QHBoxLayout()
        botones_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        btn_anadir = QPushButton("Añadir Nuevo")
        btn_editar = QPushButton("Editar Seleccionado")
        btn_eliminar = QPushButton("Eliminar Seleccionado")
        botones_layout.addWidget(btn_anadir)
        botones_layout.addWidget(btn_editar)
        botones_layout.addWidget(btn_eliminar)
        layout.addLayout(botones_layout)

        btn_anadir.clicked.connect(funcion_anadir)
        btn_editar.clicked.connect(self.placeholder_add)
        btn_eliminar.clicked.connect(self.placeholder_add)

        return tabla

    def abrir_dialogo_material(self):
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Añadir Nuevo Material")
        layout = QFormLayout(dialogo)

        combo_tipo = QComboBox(); combo_tipo.addItems(["fleje", "madera", "goma"])
        input_subtipo = QLineEdit()
        input_precio = QDoubleSpinBox(); input_precio.setDecimals(2); input_precio.setMaximum(9999.99); input_precio.setSuffix(" €")
        combo_unidad = QComboBox(); combo_unidad.addItems(["m", "m2"])

        layout.addRow("Tipo de Material:", combo_tipo)
        layout.addRow("Descripción (Subtipo):", input_subtipo)
        layout.addRow("Precio de Coste:", input_precio)
        layout.addRow("Unidad:", combo_unidad)

        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botones.accepted.connect(dialogo.accept)
        botones.rejected.connect(dialogo.reject)
        layout.addRow(botones)

        if dialogo.exec():
            tipo = combo_tipo.currentText()
            subtipo = input_subtipo.text()
            precio = input_precio.value()
            unidad = combo_unidad.currentText()
            if not subtipo:
                QMessageBox.warning(self, "Campo Vacío", "La descripción no puede estar vacía.")
                return

            conn = sqlite3.connect("troquelgest.db")
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO Materiales (tipo_material, subtipo, precio_coste, unidad) VALUES (?, ?, ?, ?)", (tipo, subtipo, precio, unidad))
                conn.commit()
                QMessageBox.information(self, "Éxito", "Material añadido correctamente.")
                self.modelo_materiales.select()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error de Base de Datos", f"No se pudo guardar: {e}")
            finally:
                conn.close()

    def abrir_dialogo_maquinaria(self):
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Añadir Nueva Máquina")
        layout = QFormLayout(dialogo)

        input_nombre = QLineEdit()
        input_coste = QDoubleSpinBox(); input_coste.setDecimals(2); input_coste.setMaximum(999.99); input_coste.setSuffix(" €/hora")

        layout.addRow("Nombre de la Máquina:", input_nombre)
        layout.addRow("Coste por Hora:", input_coste)

        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botones.accepted.connect(dialogo.accept)
        botones.rejected.connect(dialogo.reject)
        layout.addRow(botones)

        if dialogo.exec():
            nombre = input_nombre.text()
            coste = input_coste.value()
            if not nombre:
                QMessageBox.warning(self, "Campo Vacío", "El nombre no puede estar vacío.")
                return

            conn = sqlite3.connect("troquelgest.db")
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO Maquinaria (nombre_maquina, coste_por_hora) VALUES (?, ?)", (nombre, coste))
                conn.commit()
                QMessageBox.information(self, "Éxito", "Máquina añadida correctamente.")
                self.modelo_maquinaria.select()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error de Base de Datos", f"No se pudo guardar la máquina. ¿Quizás el nombre ya existe?\n\n{e}")
            finally:
                conn.close()

    def abrir_dialogo_personal(self):
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Añadir Nuevo Rol de Personal")
        layout = QFormLayout(dialogo)

        input_rol = QLineEdit()
        input_coste = QDoubleSpinBox(); input_coste.setDecimals(2); input_coste.setMaximum(999.99); input_coste.setSuffix(" €/hora")

        layout.addRow("Nombre del Rol:", input_rol)
        layout.addRow("Coste por Hora:", input_coste)

        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botones.accepted.connect(dialogo.accept)
        botones.rejected.connect(dialogo.reject)
        layout.addRow(botones)

        if dialogo.exec():
            rol = input_rol.text()
            coste = input_coste.value()
            if not rol:
                QMessageBox.warning(self, "Campo Vacío", "El nombre del rol no puede estar vacío.")
                return

            conn = sqlite3.connect("troquelgest.db")
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO RolesPersonal (nombre_rol, coste_por_hora) VALUES (?, ?)", (rol, coste))
                conn.commit()
                QMessageBox.information(self, "Éxito", "Rol añadido correctamente.")
                self.modelo_personal.select()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error de Base de Datos", f"No se pudo guardar el rol. ¿Quizás el nombre ya existe?\n\n{e}")
            finally:
                conn.close()

    def placeholder_add(self):
        QMessageBox.information(self, "En construcción", "Esta funcionalidad se añadirá próximamente.")
>>>>>>> 0196544f8e5655a970364ed0b9eed3d8ba9459cb
