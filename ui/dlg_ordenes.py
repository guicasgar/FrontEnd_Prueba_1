from PyQt5.QtWidgets import  QMessageBox, QTableWidgetItem, QHeaderView
from qgis.PyQt import uic
from qgis.core import QgsSettings, Qgis
from qgis.PyQt.QtWidgets import QDialog
from qgis.utils import iface
import os

uiFilePath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'dlg_ordenes.ui'))
DIALOG_UI = uic.loadUiType(uiFilePath)[0]


class CargaOrdenesDialog(QDialog, DIALOG_UI):

    def __init__(self, parent, ordenes):
        QDialog.__init__(self, parent)
        self.ordenCargar = -1
        self.setupUi(self)

        self.tableOrdenes.setRowCount(len(ordenes))
        self.tableOrdenes.setColumnCount(4)
        self.tableOrdenes.setHorizontalHeaderLabels(["ID", "Codigo", "Descripcion", "Estado"])
        header = self.tableOrdenes.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.botonCargar.clicked.connect(self.cargar_orden)
        self.botonCancelar.clicked.connect(self.cancelar)

        for idxRow in range(len(ordenes)):
            row = ordenes[idxRow]
            for idxCol in range(len(row)):
                self.tableOrdenes.setItem(idxRow, idxCol, QTableWidgetItem(str(row[idxCol])))

    def cargar_orden(self):
        self.ordenCargar = int(self.tableOrdenes.item(self.tableOrdenes.currentRow(), 0).text())
        self.close()
    
    def cancelar(self):
        self.close()
