from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QMessageBox
from qgis.PyQt import uic
from qgis._core import QgsFeatureRequest
from qgis._gui import QgsMapCanvas, QgsMapToolPan, QgsMapToolZoom
from qgis.core import QgsDataSourceUri, QgsProject, QgsMapLayer, QgsSettings, Qgis, QgsVectorLayer
from qgis.PyQt.QtWidgets import QDialog, QTableWidgetItem, QHeaderView, QAction
from .Formulario_ficha_predio import FormularioFichaPredial
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface
import os
from .bbdd import BBDDMapHurricane

#Se indica la ruta a la interfaz de usuario del Formulario búsqueda
uiFilePath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Formulario_busqueda.ui'))
DIALOG_UI = uic.loadUiType(uiFilePath)[0]


def setCanvasColor(white):
    pass

class FormularioBusqueda(QDialog, DIALOG_UI):

    def __init__(self, parent): #Aquí se definen las herramientas del formulario búsqueda
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.parent = parent

        self.pushButton_Consultar.clicked.connect(self.Consultar)
        self.pushButton_Consultar.setToolTip("Consultar")
        self.pushButton_VerFicha.clicked.connect(self.ver_ficha)
        self.pushButton_VerFicha.setToolTip("Ver Ficha")
        self.pushButton_Cancelar.clicked.connect(self.cancelar)
        self.pushButton_Cancelar.setToolTip("Cancelar")

    def Consultar(self):#Cuando se pulsa el botón "consultar" se ejecuta la consulta a la bbdd de ua_predioBuscarPorNumPredIdPreIdCon y se carga en rows
        rows = BBDDMapHurricane.instance().uapredio_BuscarPorNumPredIdPreIdCon(self.lineEdit_num_predial.text())
        fila = 0
        self.tableWidget_info_predio.setRowCount(len(rows)) #Se indica que haya tantas filas como campos vengan en rows
        self.tableWidget_info_predio.setColumnCount(4) #Se indica que haya 4 columnas
        header = self.tableWidget_info_predio.horizontalHeader() #Se establecen las cabeceras
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) #Se indica que las cabeceras tengan el tamaño ajustado al contenido que le entre.
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        for row in rows:
            self.tableWidget_info_predio.setItem(fila, 0, QTableWidgetItem(str(row["t_id"]))) #Se va distribuyendo la info en filas y columnas según lo que venga del campo t_id
            self.tableWidget_info_predio.setItem(fila, 1, QTableWidgetItem(str(row['predio_tipo'])))
            self.tableWidget_info_predio.setItem(fila, 2, QTableWidgetItem(str(row['condicion_predio'])))
            self.tableWidget_info_predio.setItem(fila, 3, QTableWidgetItem(row["numero_predial"]))
            fila += 1

    def ver_ficha(self): #Esta función permite consultar la ficha predial según el campo que se seleccione de la tabla consulta y pasa el número predial a la ficha predial.
        row = self.tableWidget_info_predio.currentRow() #cómo obtener la fila seleccionada
        num = self.tableWidget_info_predio.item(row, 3).text() # cómo obtener su número predial
        dlg = FormularioFichaPredial(iface.mainWindow())
        dlg.agregar_detalle_predio(num)
        dlg.show()
        self.close()

    def cancelar(self):
        self.close()