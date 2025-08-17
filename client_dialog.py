# client_dialog.py
import sqlite3
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableView, QPushButton, QHBoxLayout,
    QHeaderView, QMessageBox, QDialogButtonBox, QFormLayout,
    QLineEdit, QDoubleSpinBox
)
from PySide6.QtSql import QSqlDatabase, QSqlTableModel
from PySide6.QtCore import Qt

# Importamos la nueva ventana de presupuestos
from presupuesto_dialog import PresupuestoDialog

class ClientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Clientes")
        self.setMinimumSize(900, 600)

        self.db = QSqlDatabase.database()
        if not self.db.isOpen():
            QMessageBox.critical(self, "Error", "La conexión a la base de datos no está disponible.")
            return

        layout = QVBoxLayout(self)
        self.modelo_clientes = self.crear_modelo_tabla()

        self.tabla_clientes = QTableView()  # Hacemos la tabla un atributo de la clase
        self.tabla_clientes.setModel(self.modelo_clientes)
        self.tabla_clientes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_clientes.hideColumn(0)
        # Permitir seleccionar solo una fila a la vez
        self.tabla_clientes.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.tabla_clientes.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        layout.addWidget(self.tabla_clientes)

        botones_layout = QHBoxLayout()
        botones_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        btn_anadir = QPushButton("Añadir Cliente")
        self.btn_ver_presupuestos = QPushButton("Ver Presupuestos")
        self.btn_ver_presupuestos.setEnabled(False)  # Deshabilitado por defecto

        botones_layout.addWidget(btn_anadir)
        botones_layout.addWidget(self.btn_ver_presupuestos)
        layout.addLayout(botones_layout)

        # Conexiones de los botones
        btn_anadir.clicked.connect(self.abrir_dialogo_anadir_cliente)
        self.btn_ver_presupuestos.clicked.connect(self.abrir_dialogo_presupuestos)

        # Conectar la selección de la tabla a una función
        self.tabla_clientes.selectionModel().selectionChanged.connect(self.actualizar_estado_botones)

    def crear_modelo_tabla(self):
        modelo = QSqlTableModel(self, self.db)
        modelo.setTable("Clientes")
        modelo.select()
        cabeceras = ["ID", "Nombre", "Empresa", "CIF", "Dirección", "Teléfono", "Email", "% Beneficio"]
        for i, cabecera in enumerate(cabeceras):
            modelo.setHeaderData(i, Qt.Orientation.Horizontal, cabecera)
        return modelo

    def abrir_dialogo_anadir_cliente(self):
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Añadir Nuevo Cliente")
        layout = QFormLayout(dialogo)

        input_nombre = QLineEdit()
        input_empresa = QLineEdit()
        input_cif = QLineEdit()
        input_direccion = QLineEdit()
        input_telefono = QLineEdit()
        input_email = QLineEdit()
        input_beneficio = QDoubleSpinBox()
        input_beneficio.setDecimals(2)
        input_beneficio.setSuffix(" %")
        input_beneficio.setValue(25.0)

        layout.addRow("Nombre:", input_nombre)
        layout.addRow("Empresa:", input_empresa)
        layout.addRow("CIF:", input_cif)
        layout.addRow("Dirección:", input_direccion)
        layout.addRow("Teléfono:", input_telefono)
        layout.addRow("Email:", input_email)
        layout.addRow("Beneficio por defecto:", input_beneficio)

        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botones.accepted.connect(dialogo.accept)
        botones.rejected.connect(dialogo.reject)
        layout.addRow(botones)

        if dialogo.exec():
            nombre = input_nombre.text()
            if not nombre:
                QMessageBox.warning(self, "Campo Obligatorio", "El nombre del cliente no puede estar vacío.")
                return

            conn = sqlite3.connect("troquelgest.db")
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO Clientes (nombre, empresa, cif, direccion, telefono, email, porcentaje_beneficio_defecto)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    nombre,
                    input_empresa.text(),
                    input_cif.text(),
                    input_direccion.text(),
                    input_telefono.text(),
                    input_email.text(),
                    input_beneficio.value()
                ))
                conn.commit()
                QMessageBox.information(self, "Éxito", "Cliente añadido correctamente.")
                self.modelo_clientes.select()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error de Base de Datos",
                                   f"No se pudo guardar el cliente. ¿Quizás el CIF ya existe?\n\n{e}")
            finally:
                conn.close()

    def actualizar_estado_botones(self):
        """Habilita o deshabilita botones según si hay una fila seleccionada."""
        tiene_seleccion = self.tabla_clientes.selectionModel().hasSelection()
        self.btn_ver_presupuestos.setEnabled(tiene_seleccion)

    def abrir_dialogo_presupuestos(self):
        """Abre la ventana de presupuestos para el cliente seleccionado."""
        indices_seleccionados = self.tabla_clientes.selectionModel().selectedRows()
        if not indices_seleccionados:
            return  # No debería pasar porque el botón está deshabilitado

        # Obtenemos el ID y el nombre del cliente de la fila seleccionada
        fila_seleccionada = indices_seleccionados[0].row()
        id_cliente = self.modelo_clientes.record(fila_seleccionada).value("id")
        nombre_cliente = self.modelo_clientes.record(fila_seleccionada).value("nombre")

        # Creamos y mostramos el diálogo de presupuestos
        dialogo = PresupuestoDialog(id_cliente, nombre_cliente, self)
        dialogo.exec()