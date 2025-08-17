# new_presupuesto_dialog.py
import math, sqlite3, ezdxf
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton,
    QFileDialog, QMessageBox, QFormLayout, QComboBox, QDoubleSpinBox,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsView,
    QGraphicsScene, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsPathItem
)
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtGui import QPainterPath, QPen, QColor, QPainter
from ezdxf.document import Drawing
from ezdxf.math import Vec3, BoundingBox

# --- Utilidades DXF ---
XDATA_APP_NAME = "TroquelGest"

def get_entity_length(entity):
    if entity is None: return 0.0
    if hasattr(entity, 'length') and callable(getattr(entity, 'length')):
        try: return entity.length()
        except: pass
    t = entity.dxftype()
    if t == 'LINE': return entity.dxf.start.distance(entity.dxf.end)
    if t == 'CIRCLE': return 2 * math.pi * float(entity.dxf.radius)
    if t == 'ARC':
        ang = abs(math.radians(entity.dxf.end_angle - entity.dxf.start_angle))
        return float(entity.dxf.radius) * ang
    if t in {'LWPOLYLINE', 'POLYLINE'}:
        length = 0.0; points = list(entity.points())
        if len(points) > 1:
            for i in range(len(points) - 1): length += Vec3(points[i]).distance(Vec3(points[i+1]))
            if entity.is_closed: length += Vec3(points[-1]).distance(Vec3(points[0]))
        return length
    return 0.0

# --- Visor CAD Personalizado ---
class InteractiveCADView(QGraphicsView):
    entity_selected = Signal(object)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self._doc: Drawing | None = None; self._msp = None
        self._entity2item = {}; self._item2entity = {}
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def set_document(self, doc: Drawing):
        self._doc = doc; self._msp = doc.modelspace()
        self._rebuild_scene()

    def redraw(self): self.viewport().update()

    def set_overrides(self, mapping: dict):
        for ent, color_hex in mapping.items():
            item = self._entity2item.get(ent)
            if not item or not hasattr(item, "pen"): continue
            pen = item.pen(); pen.setColor(QColor(color_hex)); pen.setWidthF(0)
            item.setPen(pen)
        self.redraw()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            ent = self._item2entity.get(item) if item else None
            self.entity_selected.emit(ent)

    def _rebuild_scene(self):
        sc = self.scene(); sc.clear()
        self._entity2item.clear(); self._item2entity.clear()
        if not self._msp: return
        pen = QPen(); pen.setWidthF(0)
        for e in self._msp:
            t = e.dxftype(); item = None
            try:
                if t == "LINE":
                    s, p = e.dxf.start, e.dxf.end
                    item = QGraphicsLineItem(float(s.x), float(s.y), float(p.x), float(p.y))
                elif t in {"LWPOLYLINE", "POLYLINE"}:
                    pts = [Vec3(p) for p in e.points()]
                    if len(pts) >= 2:
                        path = QPainterPath(QPointF(float(pts[0].x), float(pts[0].y)))
                        for p in pts[1:]: path.lineTo(float(p.x), float(p.y))
                        if e.is_closed: path.closeSubpath()
                        item = QGraphicsPathItem(path)
                elif t == "CIRCLE":
                    c, r = e.dxf.center, float(e.dxf.radius)
                    item = QGraphicsEllipseItem(QRectF(float(c.x-r), float(c.y-r), 2*r, 2*r))
                if item:
                    item.setPen(pen); sc.addItem(item)
                    self._entity2item[e] = item; self._item2entity[item] = e
            except Exception: continue
        if sc.items():
            sc.setSceneRect(sc.itemsBoundingRect())
            self.fitInView(sc.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

# --- Diálogo Principal ---
class NewPresupuestoDialog(QDialog):
    def __init__(self, client_id, client_name, parent=None):
        super().__init__(parent)
        self.client_id, self.client_name = client_id, client_name
        self.doc: Drawing | None = None; self.msp = None; self.selected_entity = None
        self.calculo_actual = {}; self.dxf_path = ""
        self.setWindowTitle(f"Nuevo Presupuesto para: {self.client_name}"); self.setMinimumSize(1400, 800)
        layout = QVBoxLayout(self)
        top = QHBoxLayout(); self.input_ruta_fichero = QLineEdit(); self.input_ruta_fichero.setReadOnly(True)
        btn_cargar = QPushButton("Cargar DXF"); top.addWidget(QLabel("Archivo DXF:")); top.addWidget(self.input_ruta_fichero, 1); top.addWidget(btn_cargar)
        layout.addLayout(top)
        center = QHBoxLayout(); self.view = InteractiveCADView(); center.addWidget(self.view, 3)
        self.panel_propiedades = QWidget(); self.panel_propiedades.setStyleSheet("background-color: #f0f0f0;")
        side = QVBoxLayout(self.panel_propiedades); side.addWidget(QLabel("<b>Panel de Edición</b>")); form = QFormLayout()
        self.label_tipo_entidad = QLabel("-"); self.label_capa_entidad = QLabel("-")
        self.combo_flejes = QComboBox(); self.combo_tipo_corte = QComboBox(); self.combo_tipo_corte.addItems(["Corte Total", "Aplastado"])
        self.input_aplastado = QDoubleSpinBox(); self.input_aplastado.setSuffix(" mm"); self.input_aplastado.setDecimals(2)
        form.addRow("Tipo:", self.label_tipo_entidad); form.addRow("Capa:", self.label_capa_entidad); form.addRow("Asignar Fleje:", self.combo_flejes)
        form.addRow("Tipo de Corte:", self.combo_tipo_corte); form.addRow("Altura Aplastado:", self.input_aplastado)
        side.addLayout(form)
        self.btn_aplicar_cambios = QPushButton("✔️ Aplicar Cambios"); self.btn_borrar_seleccion = QPushButton("🗑️ Borrar Línea")
        side.addWidget(self.btn_aplicar_cambios); side.addWidget(self.btn_borrar_seleccion); side.addStretch()
        center.addWidget(self.panel_propiedades, 2); self.panel_propiedades.setVisible(False)
        layout.addLayout(center)
        resumen_group = QGroupBox("Resumen de Materiales y Dimensiones"); vres = QVBoxLayout(resumen_group)
        self.tabla_resumen = QTableWidget(); self.tabla_resumen.setColumnCount(2); self.tabla_resumen.setHorizontalHeaderLabels(["Concepto", "Valor"])
        self.tabla_resumen.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        vres.addWidget(self.tabla_resumen); layout.addWidget(resumen_group)
        bottom = QHBoxLayout(); self.input_nombre_proyecto = QLineEdit()
        self.btn_calcular = QPushButton("📊 Calcular Totales"); self.btn_calcular.setEnabled(False)
        self.btn_guardar = QPushButton("💾 Guardar Presupuesto"); self.btn_guardar.setEnabled(False)
        bottom.addWidget(QLabel("Nombre del Proyecto:")); bottom.addWidget(self.input_nombre_proyecto)
        bottom.addStretch(); bottom.addWidget(self.btn_calcular); bottom.addWidget(self.btn_guardar); layout.addLayout(bottom)

        btn_cargar.clicked.connect(self.cargar_fichero_dxf)
        self.combo_tipo_corte.currentTextChanged.connect(self.actualizar_estado_aplastado)
        self.btn_borrar_seleccion.clicked.connect(self.borrar_entidad_seleccionada)
        self.btn_aplicar_cambios.clicked.connect(self.aplicar_cambios_entidad)
        self.btn_calcular.clicked.connect(self.calcular_presupuesto)
        self.btn_guardar.clicked.connect(self.guardar_presupuesto)

    def cargar_flejes_al_combo(self):
        self.combo_flejes.clear()
        try:
            conn = sqlite3.connect("troquelgest.db"); cur = conn.cursor()
            cur.execute("SELECT id, subtipo FROM Materiales WHERE tipo_material = 'fleje'")
            flejes = cur.fetchall()
            if not flejes: QMessageBox.warning(self, "Sin Flejes", "No hay flejes en la base de datos.")
            for fid, subtipo in flejes: self.combo_flejes.addItem(subtipo, fid)
        except sqlite3.Error as e: QMessageBox.critical(self, "Error", str(e))
        finally: conn.close()

    def cargar_fichero_dxf(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo DXF", "", "Archivos DXF (*.dxf)")
        if not ruta: return
        self.input_ruta_fichero.setText(ruta)
        try:
            self.doc = ezdxf.readfile(ruta); self.msp = self.doc.modelspace(); self.dxf_path = ruta
            self.view.set_document(self.doc)
            self.cargar_flejes_al_combo()
            self.btn_calcular.setEnabled(True)
        except (IOError, ezdxf.DXFStructureError) as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo: {e}")

    def on_entity_selected(self, entity):
        self.selected_entity = entity
        self.panel_propiedades.setVisible(bool(entity))
        if entity: self.actualizar_panel_propiedades()

    def actualizar_panel_propiedades(self):
        if not self.selected_entity: return
        self.label_tipo_entidad.setText(self.selected_entity.dxftype())
        self.label_capa_entidad.setText(getattr(self.selected_entity.dxf, "layer", "-"))
        try:
            xdata = self.selected_entity.get_xdata(XDATA_APP_NAME)
            fleje_id, tipo_corte, altura = int(xdata[1][1]), xdata[2][1], float(xdata[3][1])
            idx = self.combo_flejes.findData(fleje_id)
            self.combo_flejes.setCurrentIndex(idx if idx != -1 else 0)
            self.combo_tipo_corte.setCurrentText(tipo_corte); self.input_aplastado.setValue(altura)
        except (ezdxf.DXFValueError, IndexError):
            self.combo_flejes.setCurrentIndex(0); self.combo_tipo_corte.setCurrentIndex(0); self.input_aplastado.setValue(0.0)
        self.actualizar_estado_aplastado(self.combo_tipo_corte.currentText())

    def actualizar_estado_aplastado(self, texto): self.input_aplastado.setEnabled(texto == "Aplastado")

    def aplicar_cambios_entidad(self):
        if not self.selected_entity: return
        fleje_id = self.combo_flejes.currentData()
        tipo_corte = self.combo_tipo_corte.currentText()
        altura = self.input_aplastado.value() if tipo_corte == "Aplastado" else 0.0
        self.selected_entity.set_xdata(XDATA_APP_NAME, [(1000, "DATOS_TROQUEL"), (1071, int(fleje_id)), (1000, tipo_corte), (1040, float(altura))])
        self.view.set_overrides({self.selected_entity: "#00FF00"})

    def borrar_entidad_seleccionada(self):
        if not self.selected_entity: return
        if QMessageBox.question(self, "Confirmar", "¿Seguro que quieres borrar?") == QMessageBox.StandardButton.Yes:
            try:
                self.msp.delete_entity(self.selected_entity); self.selected_entity = None
                self.panel_propiedades.setVisible(False)
                self.view.set_document(self.doc)
            except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def calcular_presupuesto(self):
        if not self.msp: QMessageBox.warning(self, "DXF", "Carga un DXF primero."); return
        resumen = {}
        fleje_defecto_id = self.combo_flejes.itemData(0)
        fleje_defecto_nombre = f"Fleje: {self.combo_flejes.itemText(0)} (defecto)"

        for entity in self.msp:
            longitud_mm = get_entity_length(entity)
            if longitud_mm > 0:
                longitud_m = longitud_mm / 1000.0
                try:
                    xdata = entity.get_xdata(XDATA_APP_NAME)
                    fleje_id = int(xdata[1][1])
                    idx = self.combo_flejes.findData(fleje_id)
                    nombre_fleje = f"Fleje: {self.combo_flejes.itemText(idx)}"
                    resumen[nombre_fleje] = resumen.get(nombre_fleje, 0.0) + longitud_m
                except (ezdxf.DXFValueError, IndexError):
                    if fleje_defecto_id is not None:
                        resumen[fleje_defecto_nombre] = resumen.get(fleje_defecto_nombre, 0.0) + longitud_m
        try:
            bbox = ezdxf.bbox.extents(self.msp, fast=True)
            if bbox.has_data:
                resumen["Madera Base (Ancho)"] = f"{bbox.size.x:.2f} mm"; resumen["Madera Base (Alto)"] = f"{bbox.size.y:.2f} mm"
        except Exception: pass

        self.tabla_resumen.setRowCount(0); self.tabla_resumen.setRowCount(len(resumen))
        for i, (k, v) in enumerate(resumen.items()):
            self.tabla_resumen.setItem(i, 0, QTableWidgetItem(str(k)))
            self.tabla_resumen.setItem(i, 1, QTableWidgetItem(f"{v:.2f} m" if isinstance(v, float) else str(v)))

        self.calculo_actual = resumen
        self.btn_guardar.setEnabled(True)
        QMessageBox.information(self, "OK", "Resumen calculado.")

    def guardar_presupuesto(self):
        nombre = self.input_nombre_proyecto.text().strip()
        if not nombre: QMessageBox.warning(self, "Dato requerido", "Introduce un nombre."); return
        if not self.calculo_actual: QMessageBox.warning(self, "Sin cálculo", "Calcula los totales primero."); return
        conn = sqlite3.connect("troquelgest.db"); cur = conn.cursor()
        try:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("INSERT INTO Presupuestos (cliente_id, fecha_creacion, nombre_proyecto, ruta_dxf, estado) VALUES (?, ?, ?, ?, ?)",
                           (self.client_id, fecha, nombre, self.dxf_path, "Borrador"))
            presupuesto_id = cur.lastrowid; conn.commit()
            QMessageBox.information(self, "Éxito", f"Presupuesto '{nombre}' guardado.")
            self.accept()
        except sqlite3.Error as e: QMessageBox.critical(self, "BD", str(e))
        finally: conn.close()