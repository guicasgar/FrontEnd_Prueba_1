#-----------------------------------------------------------
# Copyright (C) 2015 Martin Dobias
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

# Se importan todas las librerías que se van a usar. También se importan los formularios y la bbdd necesariasque se ejecuten en el init
import decimal
import os.path

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from qgis.core import *
from qgis.gui import QgsMapToolEmitPoint
from PyQt5.QtWidgets import QAction, QMessageBox, QMenu, QComboBox, QWidgetAction, QProgressBar
from .Formulario_busqueda import FormularioBusqueda
from .Formulario_ficha_predio import FormularioFichaPredial
from qgis._core import QgsMessageLog, QgsProcessingFeedback
from . import resources

from qgis.PyQt.QtGui import QIcon
from .ui.dlg_config import ConfigDialog
from .ui.dlg_ordenes import CargaOrdenesDialog
from qgis.utils import iface

import time
from osgeo import gdal
import locale
import configparser
import os
import sys
from .bbdd import BBDDMapHurricane

try:
    import selenium
except ImportError:
    
    this_dir = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(this_dir, 'resources', 'selenium-4.6.0-py3-none-any.whl')
    sys.path.append(path)

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests.auth import HTTPBasicAuth
import json


def classFactory(iface):
    return MapHurricanePlugin(iface)


class MapHurricanePlugin:

    def __init__(self, iface):
        self.iface = iface
        self.conexion = ""


    def initGui(self): #donde se definen las herramientas y que se inicialicen conectándose a una base de datos.
        self.conexion = ""
        self.driver = None
        self.plugin_path = os.path.dirname(os.path.realpath(__file__))
        self.menu = QMenu(self.iface.mainWindow())
        self.menu.setObjectName("menuMapHurricane")
        self.menu.setTitle("MapHurricane")

        self.toolbar = self.iface.addToolBar('MapHurricane')
        self.toolbar.setObjectName("menuMapHurricane")
        self.toolbar.setToolTip('menuMapHurricane')
        locale.setlocale(locale.LC_ALL, 'es_ES')

        self.actionConfig = QAction(QIcon(":/plugins/MapHurricane/resources/icon/gear-solid.svg"), "Configuración", self.iface.mainWindow())
        self.actionConfig.setObjectName("actionConfig")
        self.actionConfig.setToolTip('Configuración')
        self.actionConfig.triggered.connect(self.mostrar_config)
        self.menu.addAction(self.actionConfig)
        self.toolbar.addAction(self.actionConfig)

        self.submenuWeb = self.menu.addMenu(QIcon("C:/Users/Rudy/.qgis2/python/plugins/arcLensStandard/icons/item_one.png"), "Web")

        self.actionWebOrdenes = QAction(QIcon(":/plugins/MapHurricane/resources/icon/logo-bn.png"), "Ordenes", self.iface.mainWindow())
        self.actionWebOrdenes.setObjectName("actionWebOrdenes")
        self.actionWebOrdenes.setToolTip('Ir a la página de órdenes')
        self.actionWebOrdenes.triggered.connect(self.ir_a_la_web_ordenes)
        self.submenuWeb.addAction(self.actionWebOrdenes)

        self.actionWebPredios = QAction(QIcon(":/plugins/MapHurricane/resources/icon/logo-bn.png"), "Predios", self.iface.mainWindow())
        self.actionWebPredios.setObjectName("actionWebPredios")
        self.actionWebPredios.setToolTip('Ir a la página de predios')
        self.actionWebPredios.triggered.connect(self.ir_a_la_web_predios)
        self.submenuWeb.addAction(self.actionWebPredios)

        self.actionWebInteresados = QAction(QIcon(":/plugins/MapHurricane/resources/icon/logo-bn.png"), "Interesados", self.iface.mainWindow())
        self.actionWebInteresados.setObjectName("actionWebInteresados")
        self.actionWebInteresados.setToolTip('Ir a la página de interesados')
        self.actionWebInteresados.triggered.connect(self.ir_a_la_web_interesados)
        self.submenuWeb.addAction(self.actionWebInteresados)

        self.actionConfig = QAction(QIcon(":/plugins/MapHurricane/resources/icon/map-regular.svg"), "Planificador", self.iface.mainWindow())
        self.actionConfig.setObjectName("actionPlaner")
        self.actionConfig.setToolTip('Planificador')
        self.actionConfig.triggered.connect(self.cargar_proyecto_planificador)
        self.menu.addAction(self.actionConfig)
        self.toolbar.addAction(self.actionConfig)

        self.actionConfig = QAction(QIcon(":/plugins/MapHurricane/resources/icon/book-atlas-solid.svg"), "Orden trabajo", self.iface.mainWindow())
        self.actionConfig.setObjectName("actionCargarOrden")
        self.actionConfig.setToolTip('Cargar orden de trabajo')
        self.actionConfig.triggered.connect(self.cargar_proyecto_orden)
        self.menu.addAction(self.actionConfig)
        self.toolbar.addAction(self.actionConfig)

        #self.actionFichaPredial = QAction(QIcon(":/plugins/MapHurricane/resources/icon/lupa_2.png"), "Consultar Ficha Predial", self.iface.mainWindow())
        #self.actionFichaPredial.setObjectName("actionVerFichaPredial")
        #self.actionFichaPredial.setToolTip('Ficha Predial')
        #self.actionFichaPredial.triggered.connect(self.mostrar_ficha_predial)
        #self.menu.addAction(self.actionFichaPredial)
        #self.toolbar.addAction(self.actionFichaPredial)

        self.actionFormularioBusqueda = QAction(QIcon(":/plugins/MapHurricane/resources/icon/lupa_2.png"), "Formulario busqueda", self.iface.mainWindow())
        self.actionFormularioBusqueda.setObjectName("actionVerFormularioBusqueda")
        self.actionFormularioBusqueda.setToolTip('Realizar Busqueda')
        self.actionFormularioBusqueda.triggered.connect(self.mostrar_formulario_busqueda)
        self.menu.addAction(self.actionFormularioBusqueda)
        self.toolbar.addAction(self.actionFormularioBusqueda)

        self.actionActivarCursor = QAction(QIcon(":/plugins/MapHurricane/resources/icon/format_image_left.svg"), "Consulta de Ficha", self.iface.mainWindow())
        self.actionActivarCursor.setObjectName("actionActivarCursor")
        self.actionActivarCursor.setToolTip('Activa el cursor para hacer selección')
        self.actionActivarCursor.triggered.connect(self.activa_cursor_seleccion)
        self.menu.addAction(self.actionActivarCursor)
        self.toolbar.addAction(self.actionActivarCursor)

        self.bbdd = BBDDMapHurricane.instance()

        self.canvas = iface.mapCanvas()
        self.toolFicha = QgsMapToolEmitPoint(self.canvas) # Permite almacenar el punto x,y que se seleccione en el canvas
        self.toolFicha.setCursor(Qt.CrossCursor) # Aquí se establece que el cursor sea de tipo cruz.
        self.toolFicha.canvasClicked.connect(self.mostrar_ficha_clic) # Aquí se conecta el hacer clic en el canvas con la función que permite mostrar el Formulario Ficha Predial

        self.menuBar = self.iface.mainWindow().menuBar()
        self.menuBar.insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.menu)

    def cargar_proyecto_planificador(self): # Función que carga el proyecto planificador
        if self.hayCapasEnEdicion():
            iface.messageBar().pushMessage("MapHurricane", "Se debe guardar la edición en todas las capas antes de continuar...", level=Qgis.Warning)
            return
        project = QgsProject.instance()
        project.read(self.plugin_path + "/projects/planificador.qgz")

    def activa_cursor_seleccion(self): # Función para activar el cursor sobre el objeto "toolFicha"
        if not 'orden.qgz' in QgsProject.instance().absoluteFilePath():
            iface.messageBar().pushMessage("MapHurricane", "Se debe cargar una orden para consultar fichas prediales...", level=Qgis.Warning)
            return

        self.canvas.setMapTool(self.toolFicha)

    def mostrar_ficha_clic(self, toolFicha):
        num = self.bbdd.saca_numero_predial(toolFicha.x(), toolFicha.y()) #obtengo el número predial en la variable num que viene de la consulta "saca_numero_predial"
        dlg = FormularioFichaPredial(iface.mainWindow()) # Se abre el formulario en QGIS
        dlg.agregar_detalle_predio(num) # Le paso la variable num para que lo meta en el método agregar_detalle_predio
        dlg.show()

    def mostrar_ficha_predial(self): # Se hace un función que permita mostrar la ficha predial.
        if not 'orden.qgz' in QgsProject.instance().absoluteFilePath():
            iface.messageBar().pushMessage("MapHurricane", "Se debe cargar una orden para consultar fichas prediales...", level=Qgis.Warning)
            return

    def mostrar_formulario_busqueda(self): # Se hace un función que permita mostrar el formulario de búsqueda
        if not 'orden.qgz' in QgsProject.instance().absoluteFilePath():
            iface.messageBar().pushMessage("MapHurricane", "Se debe cargar una orden para consultar formulario búsqueda...", level=Qgis.Warning)
            return
        dlg = FormularioBusqueda(self.iface.mainWindow())
        dlg.show()

    def ir_a_la_web_ordenes(self): #Función para ir a la web de órdenes
        self.ir_a_web('/dashboard/ordenestrabajo')

    def ir_a_la_web_interesados(self): #Función para ir a la web de interesados
        self.ir_a_web('/dashboard/interesado')
    
    def ir_a_la_web_predios(self): #Función para ir a la web de predios
        self.ir_a_web('/dashboard/all/predio')
    
    def ir_a_la_web(self): #Función para ir a la web donde se hace login
        self.hacer_login()

    def ir_a_web(self, suburl):
        qgsSettings = QgsSettings()
        url = qgsSettings.value("MapHurricane/host") + suburl
        try:
            self.driver.get(url)
        except:
            self.hacer_login()
            myElem = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'ol-layer')))
            self.driver.get(url)

    def hacer_login(self): #Función con la que se hace login automático
        qgsSettings = QgsSettings()
        url = qgsSettings.value("MapHurricane/host")
        usr = qgsSettings.value("MapHurricane/usuario")
        passw = qgsSettings.value("MapHurricane/password")

        this_dir = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(this_dir, 'resources', 'chromedriver.exe')
        if self.driver == None:
            self.driver = webdriver.Chrome(path)
        self.driver.get(url)
        self.driver.find_element(By.CSS_SELECTOR,"input[formControlName=email]").send_keys(usr)
        self.driver.find_element(By.CSS_SELECTOR,"input[formControlName=password]").send_keys(passw)
        self.driver.find_element(By.CSS_SELECTOR,"button").click()

    def cargar_proyecto_orden(self): # Función que carga la orden en el proyecto
        project = QgsProject.instance() #Se activa el proyecto
        
        if self.hayCapasEnEdicion(): #Comprueba en la función "hayCapasEnEdicion" si la edición está activa
            iface.messageBar().pushMessage("MapHurricane", "Se debe guardar la edición en todas las capas antes de continuar...", level=Qgis.Warning)
            return
        
        rows = self.bbdd.ordenes_obtener() #Aquí llama a la consulta "ordenes_obtener" y la almacena en la variable rows
        dlg = CargaOrdenesDialog(self.iface.mainWindow(), rows) #La varible se almacena en dlg para que se muestre por pantalla
        dlg.exec_() #se ejecuta la varible dlg mostrándose por pantalla
        if dlg.ordenCargar == -1:
            return
        if not 'orden.qgz' in project.absoluteFilePath():
            project.read(self.plugin_path + "/projects/orden.qgz")

        idsPredios = self.bbdd.relordenpredio_obtenerpredios(dlg.ordenCargar)
        idsTerrenos = self.bbdd.reluepredio_obtenerterrenos(idsPredios)
        idsConstrucciones = self.bbdd.reluepredio_obtenercontrucciones(idsPredios)
        idsUnidades = self.bbdd.reluepredio_obtenerunidadadescontruccion(idsPredios)
        idsInteresados = self.bbdd.rrrderecho_obteneridsinteresados(idsPredios)

        self.filtrar_capa('ua_predio', f't_id in ({self.concat_ids(idsPredios)})')
        self.filtrar_capa('rel_uepredio', f'id_predio in ({self.concat_ids(idsPredios)})')
        self.filtrar_capa('rrr_derecho', f'id_predio in ({self.concat_ids(idsPredios)})')
        self.filtrar_capa('int_interesado', f't_id in ({self.concat_ids(idsInteresados)})')
        self.filtrar_capa('ue_terreno', f't_id in ({self.concat_ids(idsTerrenos)})')
        self.filtrar_capa('ue_construccion', f't_id in ({self.concat_ids(idsConstrucciones)})')
        self.filtrar_capa('ue_unidadconstruccion', f't_id in ({self.concat_ids(idsUnidades)})')
        
        extent = QgsProject.instance().mapLayersByName('ue_terreno')[0].extent()
        iface.mapCanvas().setExtent(extent)
        
        iface.messageBar().pushMessage("MapHurricane", "Cargada orden " + str(dlg.ordenCargar), level=Qgis.Success)

    def hayCapasEnEdicion(self) -> bool: # Función que sirve para verificar si existen capas activas en edición.
        project = QgsProject.instance()
        hayCapasEnEdicion = False
        for nombre in project.mapLayers():
            capa = project.mapLayer(nombre)
            QgsMessageLog.logMessage(nombre, 'MapHurricane', level=Qgis.Info)
            if isinstance(capa, QgsVectorLayer) and capa.isModified():
                hayCapasEnEdicion = True
                QgsMessageLog.logMessage("En edicion!!!", 'MapHurricane', level=Qgis.Info)
        return hayCapasEnEdicion

    def concat_ids(self, ids: list[int]) -> str:
        return ",".join(str(id) for id in ids)

    def filtrar_capa(self, capa, condicion):
        for capa in QgsProject.instance().mapLayersByName(capa):
            capa.setSubsetString(condicion)

    def unload(self):
        self.iface.removeToolBarIcon(self.actionConfig)
        del self.actionConfig

        self.menu.deleteLater()

    def mostrar_config(self):
        dlg = ConfigDialog(self.iface.mainWindow())
        dlg.exec_()






