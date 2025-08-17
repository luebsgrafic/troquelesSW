# select_client_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QListView, QDialogButtonBox, QMessageBox)
from PySide6.QtSql import QSqlDatabase, QSqlTableModel
class SelectClientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar Cliente"); self.setMinimumSize(400, 500)
        self.selected_client_id = None; self.selected_client_name = None
        self.db = QSqlDatabase.database(); layout = QVBoxLayout(self)
        self.model = QSqlTableModel(self, self.db); self.model.setTable("Clientes"); self.model.select()
        self.list_view = QListView(); self.list_view.setModel(self.model); self.list_view.setModelColumn(1)
        layout.addWidget(self.list_view)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        indexes = self.list_view.selectedIndexes()
        if not indexes: QMessageBox.warning(self, "Selección Requerida", "Por favor, selecciona un cliente."); return
        selected_row = indexes[0].row()
        self.selected_client_id = self.model.record(selected_row).value("id")
        self.selected_client_name = self.model.record(selected_row).value("nombre")
        super().accept()