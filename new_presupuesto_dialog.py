# new_presupuesto_dialog.py
import math
import sqlite3
import ezdxf
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton,
    QFileDialog, QMessageBox, QFormLayout, QComboBox, QDoubleSpinBox,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsView,
    QGraphicsScene, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsPathItem
)
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtGui import QPainterPath, QPen, QColor, QPainter
from ezdxf.math import Vec3

# --- Utilidades DXF ---
XDATA_APP_NAME = "TroquelGest"

def get_entity_length(entity):
    """Calcula la longitud de una entidad DXF en milímetros."""
    if entity is None:
        return 0.0

    # Intentar usar el método length() si existe
    if hasattr(entity, 'length') and callable(getattr(entity, 'length')):
        try:
            return entity.length()
        except:
            pass

    # Cálculo manual según el tipo de entidad
    entity_type = entity.dxftype()

    if entity_type == 'LINE':
        return entity.dxf.start.distance(entity.dxf.end)

    elif entity_type == 'CIRCLE':
        return 2 * math.pi * float(entity.dxf.radius)

    elif entity_type == 'ARC':
        start_angle = math.radians(entity.dxf.start_angle)
        end_angle = math.radians(entity.dxf.end_angle)
        angle_diff = abs(end_angle - start_angle)
        return float(entity.dxf.radius) * angle_diff

    elif entity_type in {'LWPOLYLINE', 'POLYLINE'}:
        length = 0.0
        points = list(entity.points())

        if len(points) > 1:
            for i in range(len(points) - 1):
                p1 = Vec3(points[i])
                p2 = Vec3(points[i + 1])
                length += p1.distance(p2)

            # Si está cerrada, añadir distancia del último al primer punto
            if entity.is_closed and len(points) > 2:
                p_last = Vec3(points[-1])
                p_first = Vec3(points[0])
                length += p_last.distance(p_first)

        return length

    return 0.0

# --- Visor CAD Personalizado ---
class InteractiveCADView(QGraphicsView):
    entity_selected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self._doc = None
        self._msp = None
        self._entity2item = {}
        self._item2entity = {}

        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def set_document(self, doc):
        """Establece el documento DXF a visualizar."""
        self._doc = doc
        self._msp = doc.modelspace()
        self._rebuild_scene()

    def redraw(self):
        """Refresca la vista."""
        self.viewport().update()

    def set_overrides(self, mapping: dict):
        """Aplica colores personalizados a entidades específicas."""
        for entity, color_hex in mapping.items():
            item = self._entity2item.get(entity)
            if not item or not hasattr(item, "pen"):
                continue

            pen = item.pen()
            pen.setColor(QColor(color_hex))
            pen.setWidthF(0)
            item.setPen(pen)

        self.redraw()

    def mousePressEvent(self, event):
        """Maneja clics del mouse para seleccionar entidades."""
        super().mousePressEvent(event)

        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            entity = self._item2entity.get(item) if item else None
            self.entity_selected.emit(entity)

    def _rebuild_scene(self):
        """Reconstruye la escena gráfica desde el documento DXF."""
        scene = self.scene()
        scene.clear()
        self._entity2item.clear()
        self._item2entity.clear()

        if not self._msp:
            return

        pen = QPen()
        pen.setWidthF(0)  # Usar ancho 0 para que Qt ajuste automáticamente

        for entity in self._msp:
            entity_type = entity.dxftype()
            item = None

            try:
                if entity_type == "LINE":
                    start = entity.dxf.start
                    end = entity.dxf.end
                    item = QGraphicsLineItem(
                        float(start.x), float(start.y),
                        float(end.x), float(end.y)
                    )

                elif entity_type in {"LWPOLYLINE", "POLYLINE"}:
                    points = [Vec3(p) for p in entity.points()]
                    if len(points) >= 2:
                        path = QPainterPath(QPointF(float(points[0].x), float(points[0].y)))
                        for point in points[1:]:
                            path.lineTo(float(point.x), float(point.y))

                        if entity.is_closed:
                            path.closeSubpath()

                        item = QGraphicsPathItem(path)

                elif entity_type == "CIRCLE":
                    center = entity.dxf.center
                    radius = float(entity.dxf.radius)
                    rect = QRectF(
                        float(center.x - radius), float(center.y - radius),
                        2 * radius, 2 * radius
                    )
                    item = QGraphicsEllipseItem(rect)

                if item:
                    item.setPen(pen)
                    scene.addItem(item)
                    self._entity2item[entity] = item
                    self._item2entity[item] = entity

            except Exception as e:
                print(f"Error procesando entidad {entity_type}: {e}")
                continue

        # Ajustar vista a contenido
        if scene.items():
            scene.setSceneRect(scene.itemsBoundingRect())
            self.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

# --- Diálogo Principal ---
class NewPresupuestoDialog(QDialog):
    def __init__(self, client_id, client_name, parent=None):
        super().__init__(parent)
        self.client_id = client_id
        self.client_name = client_name
        self.doc = None
        self.msp = None
        self.selected_entity = None
        self.calculo_actual = {}
        self.dxf_path = ""

        self.setWindowTitle(f"Nuevo Presupuesto para: {self.client_name}")
        self.setMinimumSize(1400, 800)

        # Layout principal
        layout = QVBoxLayout(self)

        # Top: Selección de archivo
        top_layout = QHBoxLayout()
        self.input_ruta_fichero = QLineEdit()
        self.input_ruta_fichero.setReadOnly(True)
        btn_cargar = QPushButton("Cargar DXF")

        top_layout.addWidget(QLabel("Archivo DXF:"))
        top_layout.addWidget(self.input_ruta_fichero, 1)
        top_layout.addWidget(btn_cargar)
        layout.addLayout(top_layout)

        # Center: Vista CAD + Panel propiedades
        center_layout = QHBoxLayout()

        # Vista CAD
        self.view = InteractiveCADView()
        center_layout.addWidget(self.view, 3)

        # Panel de propiedades
        self.panel_propiedades = QWidget()
        self.panel_propiedades.setStyleSheet("background-color: #f0f0f0;")
        self._setup_properties_panel()
        center_layout.addWidget(self.panel_propiedades, 2)
        self.panel_propiedades.setVisible(False)

        layout.addLayout(center_layout)

        # Resumen de materiales
        resumen_group = QGroupBox("Resumen de Materiales y Dimensiones")
        resumen_layout = QVBoxLayout(resumen_group)

        self.tabla_resumen = QTableWidget()
        self.tabla_resumen.setColumnCount(2)
        self.tabla_resumen.setHorizontalHeaderLabels(["Concepto", "Valor"])
        self.tabla_resumen.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        resumen_layout.addWidget(self.tabla_resumen)
        layout.addWidget(resumen_group)

        # Bottom: Controles finales
        bottom_layout = QHBoxLayout()
        self.input_nombre_proyecto = QLineEdit()

        self.btn_calcular = QPushButton("📊 Calcular Totales")
        self.btn_calcular.setEnabled(False)

        self.btn_guardar = QPushButton("💾 Guardar Presupuesto")
        self.btn_guardar.setEnabled(False)

        bottom_layout.addWidget(QLabel("Nombre del Proyecto:"))
        bottom_layout.addWidget(self.input_nombre_proyecto)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_calcular)
        bottom_layout.addWidget(self.btn_guardar)
        layout.addLayout(bottom_layout)

        # Conexiones de señales
        btn_cargar.clicked.connect(self.cargar_fichero_dxf)
        self.view.entity_selected.connect(self.on_entity_selected)
        self.combo_tipo_corte.currentTextChanged.connect(self.actualizar_estado_aplastado)
        self.btn_borrar_seleccion.clicked.connect(self.borrar_entidad_seleccionada)
        self.btn_aplicar_cambios.clicked.connect(self.aplicar_cambios_entidad)
        self.btn_calcular.clicked.connect(self.calcular_presupuesto)
        self.btn_guardar.clicked.connect(self.guardar_presupuesto)

    def _setup_properties_panel(self):
        """Configura el panel de propiedades de la entidad seleccionada."""
        side_layout = QVBoxLayout(self.panel_propiedades)
        side_layout.addWidget(QLabel("<b>Panel de Edición</b>"))

        # Formulario de propiedades
        form_layout = QFormLayout()

        self.label_tipo_entidad = QLabel("-")
        self.label_capa_entidad = QLabel("-")
        self.combo_flejes = QComboBox()
        self.combo_tipo_corte = QComboBox()
        self.combo_tipo_corte.addItems(["Corte Total", "Aplastado"])
        self.input_aplastado = QDoubleSpinBox()
        self.input_aplastado.setSuffix(" mm")
        self.input_aplastado.setDecimals(2)

        form_layout.addRow("Tipo:", self.label_tipo_entidad)
        form_layout.addRow("Capa:", self.label_capa_entidad)
        form_layout.addRow("Asignar Fleje:", self.combo_flejes)
        form_layout.addRow("Tipo de Corte:", self.combo_tipo_corte)
        form_layout.addRow("Altura Aplastado:", self.input_aplastado)

        side_layout.addLayout(form_layout)

        # Botones de acción
        self.btn_aplicar_cambios = QPushButton("✔️ Aplicar Cambios")
        self.btn_borrar_seleccion = QPushButton("🗑️ Borrar Línea")

        side_layout.addWidget(self.btn_aplicar_cambios)
        side_layout.addWidget(self.btn_borrar_seleccion)
        side_layout.addStretch()

    def cargar_flejes_al_combo(self):
        """Carga los flejes disponibles desde la base de datos."""
        self.combo_flejes.clear()

        try:
            conn = sqlite3.connect("troquelgest.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, subtipo FROM Materiales WHERE tipo_material = 'fleje'")
            flejes = cursor.fetchall()

            if not flejes:
                QMessageBox.warning(self, "Sin Flejes", "No hay flejes configurados en la base de datos.")
                return

            for fleje_id, subtipo in flejes:
                self.combo_flejes.addItem(subtipo, fleje_id)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de Base de Datos", str(e))
        finally:
            conn.close()

    def cargar_fichero_dxf(self):
        """Carga un archivo DXF seleccionado por el usuario."""
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo DXF", "", "Archivos DXF (*.dxf)"
        )

        if not ruta:
            return

        self.input_ruta_fichero.setText(ruta)

        try:
            self.doc = ezdxf.readfile(ruta)
            self.msp = self.doc.modelspace()
            self.dxf_path = ruta

            self.view.set_document(self.doc)
            self.cargar_flejes_al_combo()
            self.btn_calcular.setEnabled(True)

            QMessageBox.information(self, "Éxito", "Archivo DXF cargado correctamente.")

        except (IOError, ezdxf.DXFStructureError) as e:
            QMessageBox.critical(self, "Error de Archivo", f"No se pudo cargar el archivo DXF:\n{e}")

    def on_entity_selected(self, entity):
        """Maneja la selección de una entidad en la vista CAD."""
        self.selected_entity = entity
        self.panel_propiedades.setVisible(bool(entity))

        if entity:
            self.actualizar_panel_propiedades()

    def actualizar_panel_propiedades(self):
        """Actualiza los controles del panel según la entidad seleccionada."""
        if not self.selected_entity:
            return

        # Mostrar información básica
        self.label_tipo_entidad.setText(self.selected_entity.dxftype())
        self.label_capa_entidad.setText(getattr(self.selected_entity.dxf, "layer", "-"))

        # Intentar cargar datos existentes de XDATA
        try:
            xdata = self.selected_entity.get_xdata(XDATA_APP_NAME)
            fleje_id = int(xdata[1][1])
            tipo_corte = xdata[2][1]
            altura = float(xdata[3][1])

            # Seleccionar el fleje correspondiente
            index = self.combo_flejes.findData(fleje_id)
            if index != -1:
                self.combo_flejes.setCurrentIndex(index)
            else:
                self.combo_flejes.setCurrentIndex(0)

            self.combo_tipo_corte.setCurrentText(tipo_corte)
            self.input_aplastado.setValue(altura)

        except (ezdxf.DXFValueError, IndexError):
            # No hay datos previos, usar valores por defecto
            self.combo_flejes.setCurrentIndex(0)
            self.combo_tipo_corte.setCurrentIndex(0)
            self.input_aplastado.setValue(0.0)

        self.actualizar_estado_aplastado(self.combo_tipo_corte.currentText())

    def actualizar_estado_aplastado(self, tipo_corte):
        """Habilita/deshabilita el campo de altura según el tipo de corte."""
        self.input_aplastado.setEnabled(tipo_corte == "Aplastado")

    def aplicar_cambios_entidad(self):
        """Aplica los cambios de configuración a la entidad seleccionada."""
        if not self.selected_entity:
            return

        fleje_id = self.combo_flejes.currentData()
        tipo_corte = self.combo_tipo_corte.currentText()
        altura = self.input_aplastado.value() if tipo_corte == "Aplastado" else 0.0

        # Guardar datos en XDATA
        self.selected_entity.set_xdata(XDATA_APP_NAME, [
            (1000, "DATOS_TROQUEL"),
            (1071, int(fleje_id)),
            (1000, tipo_corte),
            (1040, float(altura))
        ])

        # Cambiar color para indicar que ha sido configurada
        self.view.set_overrides({self.selected_entity: "#00FF00"})

        QMessageBox.information(self, "Aplicado", "Cambios aplicados a la entidad.")

    def borrar_entidad_seleccionada(self):
        """Borra la entidad seleccionada del dibujo."""
        if not self.selected_entity:
            return

        respuesta = QMessageBox.question(
            self, "Confirmar Borrado",
            "¿Estás seguro de que quieres borrar esta entidad?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                self.msp.delete_entity(self.selected_entity)
                self.selected_entity = None
                self.panel_propiedades.setVisible(False)

                # Refrescar vista
                self.view.set_document(self.doc)

                QMessageBox.information(self, "Borrado", "Entidad eliminada correctamente.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo borrar la entidad:\n{e}")

    def calcular_presupuesto(self):
        """Calcula el resumen de materiales del presupuesto."""
        if not self.msp:
            QMessageBox.warning(self, "Sin DXF", "Primero debes cargar un archivo DXF.")
            return

        resumen = {}
        fleje_defecto_id = self.combo_flejes.itemData(0) if self.combo_flejes.count() > 0 else None
        fleje_defecto_nombre = f"Fleje: {self.combo_flejes.itemText(0)} (por defecto)" if self.combo_flejes.count() > 0 else "Sin flejes configurados"

        # Procesar cada entidad del modelo
        for entity in self.msp:
            longitud_mm = get_entity_length(entity)

            if longitud_mm > 0:
                longitud_m = longitud_mm / 1000.0  # Convertir a metros

                try:
                    # Intentar obtener datos configurados
                    xdata = entity.get_xdata(XDATA_APP_NAME)
                    fleje_id = int(xdata[1][1])

                    # Buscar nombre del fleje
                    index = self.combo_flejes.findData(fleje_id)
                    if index != -1:
                        nombre_fleje = f"Fleje: {self.combo_flejes.itemText(index)}"
                    else:
                        nombre_fleje = fleje_defecto_nombre

                    resumen[nombre_fleje] = resumen.get(nombre_fleje, 0.0) + longitud_m

                except (ezdxf.DXFValueError, IndexError):
                    # Usar fleje por defecto si no está configurado
                    if fleje_defecto_id is not None:
                        resumen[fleje_defecto_nombre] = resumen.get(fleje_defecto_nombre, 0.0) + longitud_m

        # Calcular dimensiones de madera base
        try:
            # Calcular bounding box del dibujo
            bbox = ezdxf.bbox.extents(self.msp, fast=True)
            if bbox.has_data:
                resumen["Madera Base (Ancho)"] = f"{bbox.size.x:.2f} mm"
                resumen["Madera Base (Alto)"] = f"{bbox.size.y:.2f} mm"
        except Exception as e:
            print(f"Error calculando dimensiones: {e}")

        # Actualizar tabla de resumen
        self.tabla_resumen.setRowCount(0)
        self.tabla_resumen.setRowCount(len(resumen))

        for i, (concepto, valor) in enumerate(resumen.items()):
            self.tabla_resumen.setItem(i, 0, QTableWidgetItem(str(concepto)))
            if isinstance(valor, float):
                self.tabla_resumen.setItem(i, 1, QTableWidgetItem(f"{valor:.2f} m"))
            else:
                self.tabla_resumen.setItem(i, 1, QTableWidgetItem(str(valor)))

        self.calculo_actual = resumen
        self.btn_guardar.setEnabled(True)

        QMessageBox.information(self, "Cálculo Completado", "Resumen de materiales calculado correctamente.")

    def guardar_presupuesto(self):
        """Guarda el presupuesto en la base de datos."""
        nombre_proyecto = self.input_nombre_proyecto.text().strip()

        if not nombre_proyecto:
            QMessageBox.warning(self, "Dato Requerido", "Introduce un nombre para el proyecto.")
            return

        if not self.calculo_actual:
            QMessageBox.warning(self, "Sin Cálculo", "Primero debes calcular los totales.")
            return

        try:
            conn = sqlite3.connect("troquelgest.db")
            cursor = conn.cursor()

            fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO Presupuestos (cliente_id, fecha_creacion, nombre_proyecto, ruta_dxf, estado)
                VALUES (?, ?, ?, ?, ?)
            """, (self.client_id, fecha_creacion, nombre_proyecto, self.dxf_path, "Borrador"))

            presupuesto_id = cursor.lastrowid
            conn.commit()

            QMessageBox.information(
                self, "Éxito",
                f"Presupuesto '{nombre_proyecto}' guardado correctamente."
            )

            self.accept()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de Base de Datos", str(e))
        finally:
            conn.close()