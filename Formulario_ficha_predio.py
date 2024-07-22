from qgis.PyQt import uic
from qgis._core import QgsFeatureRequest
from qgis._gui import QgsMapToolPan, QgsMapToolZoom
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QDialog, QTableWidgetItem, QHeaderView, QAction
from .Formulario_construccion import FormularioConstruccion
from .Formulario_interesados import FormularioInteresados
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from .bbdd import BBDDMapHurricane

#Se indica la ruta a la interfaz de usuario del Formulario ficha predio
uiFilePath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Formulario_ficha_predio.ui'))
DIALOG_UI = uic.loadUiType(uiFilePath)[0]


def setCanvasColor(white):
    pass

class FormularioFichaPredial(QDialog, DIALOG_UI):

    def __init__(self, parent): #Aquí se definen las herramientas del formulario ficha predio
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.parent = parent
        self.con2 = psycopg2.connect("host='vmmaph' port='5432' dbname='maphurricane' user='maphurricane' password='Seresco_2000' connect_timeout=10 ") #esta conexión a bbdd se ha puesto para la función "def grabar"

        # Hay datos que no están en la tabla de consulta sino en otras relacionadas. De la línea 32 a la 37 se establecen dichas relaciones para obtener el dato.
        self.idxTiposPredio = self.cargarDatosTipo(self.comboBox_tipo_predio, 'tc_prediotipo')
        self.idxCondicionPredio = self.cargarDatosTipo(self.comboBox_cond_predio, 'tc_condicionprediotipo')
        self.idxClaseSuelo = self.cargarDatosTipo(self.comboBox_clase_suelo, 'tc_clasesuelotipo')
        self.idxCategoriaSuelo = self.cargarDatosTipo(self.comboBox_cat_suelo, 'tc_categoriasuelotipo')
        self.idxDestinacionEconomica = self.cargarDatosTipo(self.comboBox_dest_econ, 'tc_destinacioneconomicatipo')
        self.idxEstadoPredio = self.cargarDatosMemoria('tc_estadopredio')

        self.pushButton_VerFichaCons.clicked.connect(self.ver_ficha_construccion)
        self.pushButton_VerFichaCons.setToolTip("Ver Ficha Construcción")
        self.pushButton_VerFichaInt.clicked.connect(self.ver_ficha_interesados)
        self.pushButton_VerFichaInt.setToolTip("Ver Ficha Interesados")
        self.pushButton_Cancelar.clicked.connect(self.cancelar)
        self.pushButton_Cancelar.setToolTip("Cancelar")
        self.pushButton_Grabar.clicked.connect(self.grabar)
        self.pushButton_Grabar.setToolTip("Grabar")

        #Desde aquí hasta la línea 83 es código para que dentro del formulario aparezca un mapa de la zona consultada, aparezca seleccionada y se pueda hacer zoom.
        layers = QgsProject.instance().mapLayersByName('ue_terreno') #Se activa el proyecto y se selecciona la capa por nombre
        self.layerTerreno = layers[0]
        self.wdt_mapa.setCanvasColor(Qt.white) #Hace que el fondo del mapa del formulario sea blanco
        self.wdt_mapa.setExtent(self.layerTerreno.extent()) #La extensión del mapa del formulario será la que tenga la capa del terreno
        self.wdt_mapa.setLayers(layers) #Establece la capa en el mapa

        self.actionZoomIn = QAction("Zoom in", self)
        self.actionZoomOut = QAction("Zoom out", self)
        self.actionPan = QAction("Pan", self)

        self.actionZoomIn.setCheckable(True)
        self.actionZoomOut.setCheckable(True)
        self.actionPan.setCheckable(True)

        self.actionZoomIn.triggered.connect(self.zoomIn)
        self.actionZoomOut.triggered.connect(self.zoomOut)
        self.actionPan.triggered.connect(self.pan)

        self.toolPan = QgsMapToolPan(self.wdt_mapa)
        self.toolPan.setAction(self.actionPan)
        self.toolZoomIn = QgsMapToolZoom(self.wdt_mapa, False)
        self.toolZoomIn.setAction(self.actionZoomIn)
        self.toolZoomOut = QgsMapToolZoom(self.wdt_mapa, True)
        self.toolZoomOut.setAction(self.actionZoomOut)

        self.pan()

    def zoomIn(self):
        self.wdt_mapa.setMapTool(self.toolZoomIn)

    def zoomOut(self):
        self.wdt_mapa.setMapTool(self.toolZoomOut)

    def pan(self):
        self.wdt_mapa.setMapTool(self.toolPan)

    def cargarDatosTipo(self, combo, tabla): #Función para cargar los datos del campo descripción en el combobox y los datos de t_id en la variable idx
        idx = [0]
        combo.addItem("--Vacio--")
        rows = BBDDMapHurricane.instance().tc_obtenervalores(tabla)
        for row in rows:
            combo.addItem(row["descripcion"])
            idx.append(row["t_id"])
        return idx

    def cargarDatosMemoria(self, tabla): #Lo mismo que en la función anterior pero por clave, valor.
        rows = BBDDMapHurricane.instance().tc_obtenervalores(tabla)
        valores = {}
        for row in rows:
            valores[row["t_id"]] = row["descripcion"]
        return valores

    def agregar_detalle_predio(self, numero_predial): #Con esta función se añaden los detalles del predio en el formulario
        row = BBDDMapHurricane.instance().uapredio_buscarpornumeropredial(numero_predial) #Esta consulta a la bbdd extrae los datos de los predios según su número predial

        self.lineEdit_num_predial.setText(str(row['numero_predial']))
        self.lineEdit_Departamento.setText(str(row['departamento']))
        self.lineEdit_Municipio.setText(str(row['municipio']))
        self.lineEdit_Direccion.setText(str(row['id_direccion']))
        self.lineEdit_Id_operacion.setText(str(row['id_operacion']))
        self.lineEdit_num_predial_anterior.setText(row['numero_predial_anterior'])
        self.lineEdit_Estado.setText(self.obtener_valor_indice(self.idxEstadoPredio, row['id_estadopredio']))
        self.lineEdit_Matricula.setText(str(row['matricula_inmobiliaria']))
        self.lineEdit_Nupre.setText(str(row['nupre']))
        self.lineEdit_Avaluo_Catastral.setText(str(row['avaluo_catastral']))
        self.lineEdit_Avaluo_Comercial.setText(str(row['avaluo_comercial']))
        self.comboBox_tipo_predio.setCurrentIndex(self.idxTiposPredio.index(self.ObtenerID(row['id_prediotipo'])))
        self.comboBox_cond_predio.setCurrentIndex(self.idxCondicionPredio.index(self.ObtenerID(row['id_condicionpredio'])))
        self.comboBox_clase_suelo.setCurrentIndex(self.idxClaseSuelo.index(self.ObtenerID(row['id_clasesuelotipo'])))
        self.comboBox_cat_suelo.setCurrentIndex(self.idxCategoriaSuelo.index(self.ObtenerID(row['id_categoriasuelotipo'])))
        self.comboBox_dest_econ.setCurrentIndex(self.idxDestinacionEconomica.index(self.ObtenerID(row['id_destinacioneconomicatipo'])))
        self.agregar_contenido_construccion(row['t_id'])
        self.agregar_contenido_interesados(row['t_id'])

        #De la línea 124 a la 128 es para que se haga zoom a lo que se seleccione de la capa terreno
        expr = '"t_id" = {}'.format(row['idt'])
        req = QgsFeatureRequest().setSubsetOfAttributes([]).setFilterExpression(expr)
        features = self.layerTerreno.getFeatures(req)
        self.layerTerreno.selectByIds([f.id() for f in features])
        self.wdt_mapa.zoomToSelected(self.layerTerreno)

    def obtener_valor_indice(self, idx, valorId): #función para que devuelva un vacío si le llega un registro igual a 0
        idRegistro = self.ObtenerID(valorId)
        if idRegistro == 0:
            return ""
        return idx[idRegistro]

    def ObtenerID(self, valor): #función para que devuelva un 0 si le viene un nulo
        if valor is None:
            return 0
        return valor

    def agregar_contenido_construccion(self, id_predio): # Con esta función se añade la info de construcciones dentro de la tabla "construcciones" del formulario
        rows = BBDDMapHurricane.instance().agregar_contenido_construccion(id_predio)
        fila = 0
        self.tableWidget_construcciones.setRowCount(len(rows))
        self.tableWidget_construcciones.setColumnCount(2)
        for row in rows:
            self.tableWidget_construcciones.setItem(fila, 0, QTableWidgetItem(str(row["t_id"])))
            self.tableWidget_construcciones.setItem(fila, 1, QTableWidgetItem(row["identificador"]))
            fila += 1

    def agregar_contenido_interesados (self, id_predio): # Con esta función se añade la info de interesados dentro de la tabla "interesados" del formulario
        rows = BBDDMapHurricane.instance().agregar_contenido_interesados(id_predio)
        fila = 0
        self.tableWidget_interesados.setRowCount(len(rows))
        self.tableWidget_interesados.setColumnCount(3)
        header = self.tableWidget_interesados.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        for row in rows:
            self.tableWidget_interesados.setItem(fila, 0, QTableWidgetItem(str(row["t_id"])))
            self.tableWidget_interesados.setItem(fila, 1, QTableWidgetItem(row["documento_identidad"]))
            self.tableWidget_interesados.setItem(fila, 2, QTableWidgetItem(row["nombre"]))
            fila += 1

    def ver_ficha_construccion(self): # Con esta función se consulta la info de la construcción en un nuevo formulario llamado Formulario Construcción
        row = self.tableWidget_construcciones.currentRow() #cómo obtener la fila seleccionada
        #QMessageBox.information(iface.mainWindow(), 'MapHurricane plugin', 'Ha seleccionado la fila: ' + str(row()))
        num =self.tableWidget_construcciones.item(row, 0).text() #selecciona el valor de t_id de la tabla de construcciones
        #iface.messageBar().pushMessage("MapHurricane", "el t_id es: " + str(num), level=Qgis.Warning)
        dlg = FormularioConstruccion(iface.mainWindow())
        dlg.agregar_detalle_construccion(num)
        dlg.show()

    def ver_ficha_interesados(self): # Con esta función se consulta la info de los interesados en un nuevo formulario llamado Formulario Interesados
        row = self.tableWidget_interesados.currentRow() #cómo obtener la fila seleccionada
        #QMessageBox.information(iface.mainWindow(), 'MapHurricane plugin', 'Ha seleccionado la fila: ' + str(row()))
        num =self.tableWidget_interesados.item(row, 0).text() #selecciona el valor de t_id de la tabla de interesados
        #iface.messageBar().pushMessage("MapHurricane", "el t_id es: " + str(num), level=Qgis.Warning)
        dlg = FormularioInteresados(iface.mainWindow())
        dlg.agregar_detalle_interesados(num)
        dlg.show()

    def grabar(self):
        cur = self.con2.cursor(cursor_factory=RealDictCursor)
        cur.execute()
        return

    def cancelar(self):
        self.close()