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
import psycopg2
from psycopg2.extras import RealDictCursor
from .bbdd import BBDDMapHurricane

#Se indica la ruta a la interfaz de usuario del Formulario interesados
uiFilePath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Formulario_interesados.ui'))
DIALOG_UI = uic.loadUiType(uiFilePath)[0]


def setCanvasColor(white):
    pass

class FormularioInteresados(QDialog, DIALOG_UI):

    def __init__(self, parent): #Aquí se definen las herramientas del formulario interesados
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.parent = parent

        # Hay datos que no están en la tabla de consulta sino en tablas relacionadas. De la línea 31 a la 35 se establecen dichas relaciones para obtener el dato.
        self.idx_tipo_interesado = self.cargarDatosTipo(self.comboBox_tipo_interesado, 'tc_interesadotipo')
        self.idx_tipodocu_interesado = self.cargarDatosTipo(self.comboBox_tipodocu_interesado, 'tc_interesadodocumentotipo')
        self.idx_grupo_etnico = self.cargarDatosTipo(self.comboBox_grupo_etnico, 'tc_grupoetnicotipo')
        self.idx_sexo = self.cargarDatosTipo(self.comboBox_sexo, 'tc_sexotipo')
        self.idx_direccion = self.cargar_datos_interesados(self.comboBox_direccion, 'tc_direcciontipo')

        self.pushButton_cerrar.clicked.connect(self.cerrar)
        self.pushButton_cerrar.setToolTip("Cerrar")

    def cargarDatosTipo(self, combo, tabla): #Función para cargar los datos del campo descripción en el combobox y los datos de t_id en la variable idx desde la bbdd obtenervalores
        idx = [0]
        combo.addItem("--Vacio--")
        rows = BBDDMapHurricane.instance().tc_obtenervalores(tabla)
        for row in rows:
            combo.addItem(row["descripcion"])
            idx.append(row["t_id"])
        return idx

    def cargar_datos_interesados(self, combo, tabla): #Función para cargar los datos del campo descripción en el combobox y los datos de t_id en la variable idx desde la bbdd obtenervaloresdireccion
        idx = [0]
        combo.addItem("--Vacio--")
        rows = BBDDMapHurricane.instance().tc_obtenervaloresdireccion(tabla)
        for row in rows:
            combo.addItem(row["descripcion"])
            idx.append(row["t_id"])
        return idx

    def agregar_detalle_interesados(self, t_id): #Con esta función se añaden los detalles del interesado en el formulario
        row = BBDDMapHurricane.instance().intInteresados_BuscarPorId(t_id) # Consulta para obtener los interesados según su id

        self.lineEdit_t_id.setText(str(row['t_id']))
        self.lineEdit_primer_nombre.setText(str(row['primer_nombre']))
        self.lineEdit_segundo_nombre.setText(str(row['segundo_nombre']))
        self.lineEdit_primer_apellido.setText(str(row['primer_apellido']))
        self.lineEdit_segundo_apellido.setText(str(row['segundo_apellido']))
        self.lineEdit_razon_social.setText(str(row['razon_social']))
        self.lineEdit_docu_identidad.setText(str(row['documento_identidad']))
        self.lineEdit_nombre.setText(str(row['nombre']))
        self.comboBox_tipo_interesado.setCurrentIndex(self.idx_tipo_interesado.index(self.ObtenerID(row['id_interesadotipo'])))
        self.comboBox_tipodocu_interesado.setCurrentIndex(self.idx_tipodocu_interesado.index(self.ObtenerID(row['id_interesadodocumentotipo'])))
        self.comboBox_grupo_etnico.setCurrentIndex(self.idx_grupo_etnico.index(self.ObtenerID(row['id_grupoetnico'])))
        self.comboBox_sexo.setCurrentIndex(self.idx_sexo.index(self.ObtenerID(row['id_sexotipo'])))
        self.comboBox_direccion.setCurrentIndex(self.idx_direccion.index(self.ObtenerID(row['id_direccion'])))

    def ObtenerID(self, valor):  # función para obtener el valor pero que devuelva un 0 si le viene un nulo
        if valor is None:
            return 0
        return valor

    def cerrar(self):
        self.close()