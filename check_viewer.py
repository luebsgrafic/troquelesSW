# check_viewer.py
import sys
from PySide6.QtWidgets import QApplication
from ezdxf.addons.drawing.qtviewer import CADGraphicsView

print("--- Realizando diagnóstico del CADGraphicsView ---")

# Creamos una aplicación mínima para poder instanciar el widget
app = QApplication(sys.argv)

# Creamos una instancia del visualizador
view = CADGraphicsView()

# Imprimimos todos los atributos y métodos disponibles en el objeto
print("\nAtributos y señales disponibles:")
print(dir(view))

print("\n--- Diagnóstico finalizado ---")
sys.exit()