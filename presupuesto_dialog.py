# presupuesto_dialog.py
<<<<<<< HEAD
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTableView, QHeaderView, QMessageBox, QLabel)
from PySide6.QtSql import QSqlDatabase, QSqlTableModel
=======
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableView, QPushButton, QHBoxLayout,
                             QHeaderView, QMessageBox, QLabel)
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtCore import Qt
>>>>>>> 0196544f8e5655a970364ed0b9eed3d8ba9459cb

class PresupuestoDialog(QDialog):
    def __init__(self, client_id, client_name, parent=None):
        super().__init__(parent)
<<<<<<< HEAD
        self.client_id, self.client_name = client_id, client_name
=======
        self.client_id = client_id
        self.client_name = client_name

>>>>>>> 0196544f8e5655a970364ed0b9eed3d8ba9459cb
        self.setWindowTitle(f"Presupuestos de: {self.client_name}")
        self.setMinimumSize(900, 600)

        self.db = QSqlDatabase.database()
        if not self.db.isOpen():
            QMessageBox.critical(self, "Error", "La conexión a la base de datos no está disponible.")
            return

<<<<<<< HEAD
        layout = QVBoxLayout(self)

=======
        # Layout principal
        layout = QVBoxLayout(self)

        # Etiqueta con el nombre del cliente
>>>>>>> 0196544f8e5655a970364ed0b9eed3d8ba9459cb
        label_cliente = QLabel(f"Mostrando presupuestos para: {self.client_name}")
        label_cliente.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(label_cliente)

<<<<<<< HEAD
        self.modelo_presupuestos = self.crear_modelo_tabla()
        tabla = QTableView()
        tabla.setModel(self.modelo_presupuestos)
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla.hideColumn(0)  # id
        tabla.hideColumn(1)  # cliente_id
        layout.addWidget(tabla)

=======
        # Tabla de presupuestos
        self.modelo_presupuestos = self.crear_modelo_tabla()

        tabla = QTableView()
        tabla.setModel(self.modelo_presupuestos)
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tabla.hideColumn(0) # Ocultar ID de presupuesto
        tabla.hideColumn(1) # Ocultar ID de cliente
        layout.addWidget(tabla)

        # Botones
        botones_layout = QHBoxLayout()
        botones_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        btn_crear = QPushButton("Crear Nuevo Presupuesto")

        botones_layout.addWidget(btn_crear)
        layout.addLayout(botones_layout)

        # Conexión de botones (por ahora, placeholder)
        btn_crear.clicked.connect(self.crear_nuevo_presupuesto)

>>>>>>> 0196544f8e5655a970364ed0b9eed3d8ba9459cb
    def crear_modelo_tabla(self):
        modelo = QSqlTableModel(self, self.db)
        modelo.setTable("Presupuestos")
        modelo.setFilter(f"cliente_id = {self.client_id}")
        modelo.select()
<<<<<<< HEAD
        cabeceras = ["ID", "Cliente ID", "Fecha Creación", "Proyecto", "Ruta DXF", "Estado", "% Beneficio"]
        for i, cabecera in enumerate(cabeceras):
            modelo.setHeaderData(i, Qt.Orientation.Horizontal, cabecera)
        return modelo
=======

        cabeceras = ["ID", "Cliente ID", "Fecha Creación", "Proyecto", "Ruta DXF", "Estado", "% Beneficio"]
        for i, cabecera in enumerate(cabeceras):
            modelo.setHeaderData(i, Qt.Orientation.Horizontal, cabecera)

        return modelo

    def crear_nuevo_presupuesto(self):
        QMessageBox.information(self, "En construcción", "Aquí empezará el proceso de creación de un nuevo presupuesto.")
>>>>>>> 0196544f8e5655a970364ed0b9eed3d8ba9459cb
