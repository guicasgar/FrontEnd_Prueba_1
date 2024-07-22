from PyQt5.QtWidgets import  QMessageBox
from qgis.PyQt import uic
from qgis.core import QgsSettings, Qgis
from qgis.PyQt.QtWidgets import QDialog
from qgis.utils import iface
import os

uiFilePath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'dlg_config.ui'))
DIALOG_UI = uic.loadUiType(uiFilePath)[0]


class ConfigDialog(QDialog, DIALOG_UI):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        s = QgsSettings()
        self.lineEdit_Host.setText(s.value("MapHurricane/host", "localhost:8081"))
        self.lineEdit_Usuario.setText(s.value("MapHurricane/usuario", "prueba"))
        self.lineEdit_Password.setText(s.value("MapHurricane/password", "Seresco_2000"))

        self.parent = parent
        self.botonGuardar.clicked.connect(self.guardar_configuracion)


    def guardar_configuracion(self):
        s = QgsSettings()
        s.setValue("MapHurricane/host", self.lineEdit_Host.text())
        s.setValue("MapHurricane/usuario", self.lineEdit_Usuario.text())
        s.setValue("MapHurricane/password", self.lineEdit_Password.text())

        iface.messageBar().pushMessage("MapHurricane", "Configuración guardada correctamente", level=Qgis.Success)
        self.close()
