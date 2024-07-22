from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QMessageBox
from qgis.PyQt import uic
from qgis._core import QgsFeatureRequest
from qgis._gui import QgsMapCanvas, QgsMapToolPan, QgsMapToolZoom
from qgis.core import QgsDataSourceUri, QgsProject, QgsMapLayer, QgsSettings, Qgis, QgsVectorLayer
from qgis.PyQt.QtWidgets import QDialog, QTableWidgetItem, QHeaderView, QAction
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface
import os
from .bbdd import BBDDMapHurricane

#Se indica la ruta a la interfaz de usuario del Formulario construcción
uiFilePath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Formulario_construccion.ui'))
DIALOG_UI = uic.loadUiType(uiFilePath)[0]


def setCanvasColor(white):
    pass

class FormularioConstruccion(QDialog, DIALOG_UI):

    def __init__(self, parent): #Aquí se definen las herramientas del formulario construcción
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.parent = parent

        # Hay datos que no están en la tabla de consulta sino en otras relacionadas. De la línea 29 a la 31 se establecen dichas relaciones para obtener el dato.
        self.idx_tipo_construccion = self.cargarDatosTipo(self.comboBox_tipo_construccion, 'tc_construcciontipo')
        self.idx_dominio_tipocons = self.cargarDatosTipo(self.comboBox_dominio_tipocons, 'tc_dominioconstrucciontipo')
        self.idx_rel_superficie = self.cargarDatosTipo(self.comboBox_rel_superficie, 'tc_relacionsuperficietipo')

        self.pushButton_cerrar.clicked.connect(self.cerrar)
        self.pushButton_cerrar.setToolTip("Cerrar")

        # Desde aquí hasta la línea 81 es código para que dentro del formulario aparezca un mapa de la zona consultada, aparezca seleccionada y se pueda hacer zoom.
        # En este caso las capas de terreno y construcción son las que van a formar parte de ese mapa apareciendo encima la de construcción.
        self.layerTerreno = QgsProject.instance().mapLayersByName('ue_terreno')[0]
        self.layerConstruccion = QgsProject.instance().mapLayersByName('ue_construccion')[0]
        self.wdt_mapa_cons.setCanvasColor(Qt.white)
        self.wdt_mapa_cons.setExtent(self.layerTerreno.extent())
        self.wdt_mapa_cons.setLayers([self.layerConstruccion, self.layerTerreno])

        self.actionZoomIn = QAction("Zoom in", self)
        self.actionZoomOut = QAction("Zoom out", self)
        self.actionPan = QAction("Pan", self)

        self.actionZoomIn.setCheckable(True)
        self.actionZoomOut.setCheckable(True)
        self.actionPan.setCheckable(True)

        self.actionZoomIn.triggered.connect(self.zoomIn)
        self.actionZoomOut.triggered.connect(self.zoomOut)
        self.actionPan.triggered.connect(self.pan)

        self.toolPan = QgsMapToolPan(self.wdt_mapa_cons)
        self.toolPan.setAction(self.actionPan)
        self.toolZoomIn = QgsMapToolZoom(self.wdt_mapa_cons, False)
        self.toolZoomIn.setAction(self.actionZoomIn)
        self.toolZoomOut = QgsMapToolZoom(self.wdt_mapa_cons, True)
        self.toolZoomOut.setAction(self.actionZoomOut)

        self.pan()

    def zoomIn(self):
        self.wdt_mapa_cons.setMapTool(self.toolZoomIn)

    def zoomOut(self):
        self.wdt_mapa_cons.setMapTool(self.toolZoomOut)

    def pan(self):
        self.wdt_mapa_cons.setMapTool(self.toolPan)

    def cargarDatosTipo(self, combo, tabla): #Función para cargar los datos del campo descripción en el combobox y los datos de t_id en la variable idx
        idx = [0]
        combo.addItem("--Vacio--")
        rows = BBDDMapHurricane.instance().tc_obtenervalores(tabla)
        for row in rows:
            combo.addItem(row["descripcion"])
            idx.append(row["t_id"])
        return idx

    def agregar_detalle_construccion(self, t_id): #Con esta función se añaden los detalles de la construcción en el formulario
        row = BBDDMapHurricane.instance().ueconstruccion_buscarporid(t_id) # Consulta para obtener las construcciones según su id

        self.lineEdit_t_id.setText(str(row['t_id']))
        self.lineEdit_identificador.setText(str(row['identificador']))
        self.lineEdit_num_pisos.setText(str(row['numero_pisos']))
        self.lineEdit_num_sotanos.setText(str(row['numero_sotanos']))
        self.lineEdit_num_semisotanos.setText(str(row['numero_semisotanos']))
        self.lineEdit_num_mezanines.setText(str(row['numero_mezanines']))
        self.lineEdit_area_construccion.setText(str(row['area_construccion']))
        self.lineEdit_anio_construccion.setText(str(row['anio_construccion']))
        self.lineEdit_altura.setText(str(row['altura']))
        self.lineEdit_Avaluo_Catastral_cons.setText(str(row['avaluo_construccion']))
        self.lineEdit_Avaluo_Comercial_cons.setText(str(row['avaluo_comercial_construccion']))
        self.comboBox_tipo_construccion.setCurrentIndex(self.idx_tipo_construccion.index(self.ObtenerID(row['id_tipoconstruccion'])))
        self.comboBox_dominio_tipocons.setCurrentIndex(self.idx_dominio_tipocons.index(self.ObtenerID(row['id_dominioconstrucciontipo'])))
        self.comboBox_rel_superficie.setCurrentIndex(self.idx_rel_superficie.index(self.ObtenerID(row['id_relacionsuperficie'])))
        self.agregar_contenido_unidadesconstruccion(row['t_id'])

        # De la línea 103 a la 107 es para que se haga zoom a lo que se seleccione de la capa construccion
        expr = '"t_id" = {}'.format('idt')
        req = QgsFeatureRequest().setSubsetOfAttributes([]).setFilterExpression(expr)
        features = self.layerConstruccion.getFeatures(req)
        self.layerConstruccion.selectByIds([f.id() for f in features])
        self.wdt_mapa_cons.zoomToSelected(self.layerConstruccion)

    def ObtenerID(self, valor): # función para que devuelva un 0 si le viene un nulo
        if valor is None:
            return 0
        return valor

    def agregar_contenido_unidadesconstruccion(self, id_construccion): # Con esta función se añade la info de unidades de construcciones dentro de la tabla "unidades de construcciones" del formulario
        rows = BBDDMapHurricane.instance().ueUnidadconstruccion_BuscarIdUnidadconstruccion(id_construccion)
        fila = 0
        #QMessageBox.information(iface.mainWindow(), 'MapHurricane plugin', 'Ha seleccionado la fila: ' + str(id_construccion))
        self.tableWidget_unidades_construccion.setRowCount(len(rows))
        self.tableWidget_unidades_construccion.setColumnCount(2)
        header = self.tableWidget_unidades_construccion.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row in rows:
            self.tableWidget_unidades_construccion.setItem(fila, 0, QTableWidgetItem(str(row["t_id"])))
            self.tableWidget_unidades_construccion.setItem(fila, 1, QTableWidgetItem(row["identificador"]))
            fila += 1

    def cerrar(self):
        self.close()