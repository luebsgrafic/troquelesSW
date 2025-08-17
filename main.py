# main.py
import sys
<<<<<<< HEAD
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox, QPushButton
from PySide6.QtGui import QAction
from PySide6.QtSql import QSqlDatabase
from config_dialog import ConfigDialog
from client_dialog import ClientDialog
from select_client_dialog import SelectClientDialog
from new_presupuesto_dialog import NewPresupuestoDialog

def init_database():
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName("troquelgest.db")
    if not db.open():
        QMessageBox.critical(None, "Error de Base de Datos", f"No se pudo conectar a la base de datos.\nError: {db.lastError().text()}")
        return False
=======
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QMessageBox
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from PyQt6.QtSql import QSqlDatabase # <-- NUEVO

# Importamos nuestras ventanas de diálogo
from config_dialog import ConfigDialog
from client_dialog import ClientDialog

def init_database():
    """NUEVO: Función para crear y abrir la conexión a la base de datos."""
    # addDatabase abre la conexión y la hace disponible para toda la aplicación
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName("troquelgest.db")

    if not db.open():
        QMessageBox.critical(None, "Error de Base de Datos",
                             "No se pudo conectar a la base de datos.\n"
                             f"Error: {db.lastError().text()}")
        return False

    print("Conexión a la base de datos establecida con éxito.")
>>>>>>> 0196544f8e5655a970364ed0b9eed3d8ba9459cb
    return True

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TroquelGest - Sistema de Presupuestos")
        self.setGeometry(100, 100, 800, 600)
<<<<<<< HEAD
        menu = self.menuBar()
        menu_archivo = menu.addMenu("&Archivo"); accion_salir = QAction("Salir", self); accion_salir.triggered.connect(self.close); menu_archivo.addAction(accion_salir)
        menu_clientes = menu.addMenu("&Clientes"); accion_gestionar_clientes = QAction("Gestionar Clientes", self); accion_gestionar_clientes.triggered.connect(self.abrir_dialogo_clientes); menu_clientes.addAction(accion_gestionar_clientes)
        menu_config = menu.addMenu("&Configuración"); accion_costes = QAction("Gestionar Costes", self); accion_costes.triggered.connect(self.abrir_dialogo_configuracion); menu_config.addAction(accion_costes)
        widget_central = QWidget(); self.setCentralWidget(widget_central); layout_principal = QVBoxLayout(widget_central)
        self.btn_nuevo_presupuesto = QPushButton("➕ Crear Nuevo Presupuesto"); font = self.btn_nuevo_presupuesto.font(); font.setPointSize(24); self.btn_nuevo_presupuesto.setFont(font); self.btn_nuevo_presupuesto.setMinimumHeight(100)
        layout_principal.addWidget(self.btn_nuevo_presupuesto)
        self.btn_nuevo_presupuesto.clicked.connect(self.iniciar_proceso_presupuesto)

    def iniciar_proceso_presupuesto(self):
        select_dialog = SelectClientDialog(self)
        if select_dialog.exec():
            presupuesto_dialog = NewPresupuestoDialog(select_dialog.selected_client_id, select_dialog.selected_client_name, self)
            presupuesto_dialog.exec()

    def abrir_dialogo_configuracion(self):
        dialogo = ConfigDialog(self); dialogo.exec()

    def abrir_dialogo_clientes(self):
        dialogo = ClientDialog(self); dialogo.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    if not init_database(): sys.exit(1)
    ventana = MainWindow(); ventana.show()
=======

        menu = self.menuBar()

        menu_archivo = menu.addMenu("&Archivo")
        accion_salir = QAction("Salir", self)
        accion_salir.triggered.connect(self.close)
        menu_archivo.addAction(accion_salir)

        menu_clientes = menu.addMenu("&Clientes")
        accion_gestionar_clientes = QAction("Gestionar Clientes", self)
        accion_gestionar_clientes.triggered.connect(self.abrir_dialogo_clientes)
        menu_clientes.addAction(accion_gestionar_clientes)

        menu_config = menu.addMenu("&Configuración")
        accion_costes = QAction("Gestionar Costes", self)
        accion_costes.triggered.connect(self.abrir_dialogo_configuracion)
        menu_config.addAction(accion_costes)

        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        layout_principal = QVBoxLayout(widget_central)
        etiqueta_bienvenida = QLabel("Bienvenido a TroquelGest\n\nUse el menú para empezar.")
        etiqueta_bienvenida.setStyleSheet("font-size: 24px;")
        etiqueta_bienvenida.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.addWidget(etiqueta_bienvenida)

    def abrir_dialogo_configuracion(self):
        dialogo = ConfigDialog(self)
        dialogo.exec()

    def abrir_dialogo_clientes(self):
        dialogo = ClientDialog(self)
        dialogo.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # NUEVO: Intentamos conectar a la BD antes de mostrar nada
    if not init_database():
        sys.exit(1) # Si no conecta, cerramos la app

    ventana = MainWindow()
    ventana.show()
>>>>>>> 0196544f8e5655a970364ed0b9eed3d8ba9459cb
    sys.exit(app.exec())