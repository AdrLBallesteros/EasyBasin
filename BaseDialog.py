# -*- coding: utf-8 -*-
"""
/***************************************************************************
 **EasyBasin v3
 **A QGIS plugin
 **Descripcion: Plugin para la creación de cuencas hidrográficas.
--------------------------------------------------
        begin                : **Diciembre-2023
        copyright            : **COPYRIGHT
        email                : **alopez6@ucam.edu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software: you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation, either version 3 of the License, or     *
 *   (at your option) any later version.                                    *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *  

from EasyBasin_v3.gui.generated.ui_dialog import Ui_BaseDialog
from EasyBasin_v3.Results import Results

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QApplication
from qgis.gui import QgsMapToolEmitPoint
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsRasterLayer
from PyQt5.QtCore import QFileInfo
from qgis.PyQt.QtCore import QVariant
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtWidgets, QtGui

import os.path
import os
import processing
import webbrowser


class BaseDialog(QDialog, Ui_BaseDialog):
    def __init__(self, iface):

        QDialog.__init__(self)
        self.setupUi(self)
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))

        # Variable global -> Ruta de proyecto
        self.folder = None

        #Activar bloqueo de botones
        # self.pushButtonAvance1.setEnabled(False)
        self.pushButtonAvance2.setEnabled(False)
        self.pushButtonAvance3.setEnabled(False)
        self.pushButtonAvance4.setEnabled(False)
        self.pushButtonStreams.setEnabled(False)
        self.pushButtonBasin.setEnabled(False)
        self.pushButtonResultados.setEnabled(False)
        self.inputRaster.setEnabled(False)
        self.lineEditMDT.setEnabled(False)

        #Activar selector CRS y cambiar info por defecto.
        self.mQgsProjection_PUNTO.setOptionVisible(self.mQgsProjection_PUNTO.CrsNotSet,True)
        self.mQgsProjection_PUNTO.setNotSetText('Sistema de Referencia Coordenadas')

        #Cambia el CRS del proyecto a ETRS89
        ETRS89 = QgsCoordinateReferenceSystem(25830)
        QgsProject.instance().setCrs(ETRS89)  
        self.canvas.refresh()

        #Colocar filtros MDT
        self.inputRaster.setFilter("TIFF files (*.tif);;ERDAS IMAGINE files (*.img)")

        #Aviso de fallo en la instalación
        if not os.path.exists("C:/EasyBasin"):   
            QMessageBox.critical(None, "Error de instalación", "Carpeta C:\EasyBasin no encontrada.\nVuelve a lanzar el instalador o descarga desde el repositorio GitHub la carpeta EasyBasin y copiala en el disco C:\. ")

        self.inputRaster.setFilePath('C:/EasyBasin/Rasters/MDT/MDT25_SPAIN.tif')

    def InitialWindow(self):

        #Crea una ventana para seleccionar la ruta del proyecto
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(':/imgBase/icon.png'))
        msg.setWindowTitle("Seleccionar ruta del proyecto")
        msg.setText("Por favor, indica una ruta para guardar el proyecto.")
        msg.setDetailedText("Pasos: \n1. Pulsa \"OK\" para abrir el explorador de archivos. \n2. Escribe un nombre para la carpeta del proyecto.\n3. Pulsa \"Guardar\".")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.No)

        if msg.exec_() == QMessageBox.Ok:

            self.show()

            try:
                #Crear nueva carpeta en la ruta seleccionada
                filename = QtWidgets.QFileDialog.getSaveFileName(self,"Escribe un nombre para la carpeta del proyecto:","","")
                self.folder = str(filename[0])
                os.makedirs(self.folder)
                self.pushButton_labelPath.setText(self.folder)

                # Añadir mapa base
                self.MapaBase()  

                #Generar carpetas por defecto
                path1 = self.folder + '/EasyBasin'
                os.makedirs(path1, exist_ok=True)
                path2 = self.folder + '/EasyBasin/HMS'
                os.makedirs(path2, exist_ok=True)
                path3 = self.folder + '/EasyBasin/HMS/Subcuencas'
                os.makedirs(path3, exist_ok=True)
                path4 = self.folder + '/EasyBasin/Capas_SIG'
                os.makedirs(path4, exist_ok=True)
                path6 = self.folder + '/EasyBasin/Capas_SIG/Punto_Salida'
                os.makedirs(path6, exist_ok=True)
                path7 = self.folder + '/EasyBasin/Capas_SIG/Red_Drenaje'
                os.makedirs(path7, exist_ok=True)
                path8 = self.folder + '/EasyBasin/Capas_SIG/Cuenca_Hidrografica'
                os.makedirs(path8, exist_ok=True)
                path9 = self.folder + '/EasyBasin/Capas_SIG/MDT'
                os.makedirs(path9, exist_ok=True)
                path10 = self.folder + '/EasyBasin/Hietogramas'
                os.makedirs(path10, exist_ok=True)
                path11 = self.folder + '/EasyBasin/Informes'
                os.makedirs(path11, exist_ok=True)
                path12 = self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos'
                os.makedirs(path12, exist_ok=True) 
                path13 = self.folder + '/EasyBasin/HMS/Red_Drenaje'
                os.makedirs(path13, exist_ok=True)
                path14 = self.folder + '/EasyBasin/HMS/Subcuencas/Separadas'
                os.makedirs(path14, exist_ok=True)
                path15 = self.folder + '/EasyBasin/HMS/Subcuencas/Separadas/inlets'
                os.makedirs(path15, exist_ok=True)
                path16 = self.folder + '/EasyBasin/HMS/Subcuencas/Separadas/outlets'
                os.makedirs(path16, exist_ok=True)
                path17 = self.folder + '/EasyBasin/HMS/Red_Drenaje/LFP_Subcuencas'
                os.makedirs(path17, exist_ok=True)
                path18 = self.folder + '/EasyBasin/HMS/Red_Drenaje/ALT_Subcuencas'
                os.makedirs(path18, exist_ok=True)

            except:
                self.close()      
        else:
            self.close()

    def MapaBase(self):

        #Seleccionar y añadir mapa base
        basemap_url = "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png&zmax=19&zmin=0&crs=EPSG3857"
        basemap = QgsRasterLayer(basemap_url, "Mapa Base", "wms")
        QgsProject.instance().addMapLayer(basemap) 


        layer = QgsVectorLayer('C:/EasyBasin/Rasters/SIG/CH_SPAIN_WGS84.shp', 'Límites de aplicación EasyBasin', 'ogr')
        QgsProject.instance().addMapLayer(layer)

        #Activar capa a editar
        spain = QgsProject.instance().mapLayersByName('Límites de aplicación EasyBasin')[0]
        #Cambiar color y tamaño capa
        symbol = QgsFillSymbol.createSimple({'color':'red','color_border':'black','width_border':'0.5','style':'no'})
        spain.renderer().setSymbol(symbol)
        spain.triggerRepaint()
        self.iface.layerTreeView().refreshLayerSymbology(spain.id())



    def aforo(self):

        try:
            #Capturar CRS del selector de coordenadas
            crs_Outlet = self.mQgsProjection_PUNTO.crs() 

            #Capturar ruta del proyecto
            pointPath =  self.folder + '/EasyBasin/Capas_SIG/Punto_Salida/punto_salida.shp'

            #Crear un nuevo shapefile
            writer = QgsVectorFileWriter(pointPath,
                                            "UTF-8",
                                            QgsFields(),
                                            QgsWkbTypes.Point, 
                                            crs_Outlet, 
                                            "ESRI Shapefile")
            #Añadir la geometria - Dibujar punto
            X = self.lineEditX.text()
            Y = self.lineEditY.text()
            fet = QgsFeature()
            fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(X),float(Y))))
            fet.setAttributes([1, "ID"])
            writer.addFeature(fet)
            del writer

            #Añadir capa vectorial
            layer = QgsVectorLayer(pointPath, 'Punto de Salida', "ogr")
            QgsProject.instance().addMapLayer(layer)

            #Cambia el CRS del proyecto a ETRS89
            ETRS89 = QgsCoordinateReferenceSystem(25830)
            QgsProject.instance().setCrs(ETRS89)  
            self.canvas.setDestinationCrs(ETRS89)
            self.canvas.refresh()

            #Desactivar botones del proceso previo
            self.pushButtonOutlet.setEnabled(False)
            self.pushButtonAvance1.setEnabled(False)
            self.pushButtonAvance2.setEnabled(True)
            self.inputRaster.setEnabled(True)
            self.lineEditMDT.setEnabled(True)

            #Desactivar coordenadas X e Y
            self.lineEditX.setEnabled(False)
            self.lineEditY.setEnabled(False)
            self.mQgsProjection_PUNTO.setEnabled(False)

            #Generar buffer por defecto
            self.buffer()

            if not os.path.exists("C:/EasyBasin/Rasters/MDT/MDT25_SPAIN.tif"):   
                QMessageBox.warning(None, "MDT por defecto", "Archivo MDT25_SPAIN.tif no encontrado.\n\nSi quiere utilizar el MDT25 por defecto de EasyBasin, descarguelo del siguiente enlace (https://doi.org/10.5281/zenodo.10687298) y guardelo en la ruta:\nC:/EasyBasin/Rasters/MDT/ \n\nSi no puede continuar utilizando EasyBasin con cualquier otro MDT propio, pero recuerde cambiar la ruta por defecto.")

        except:
            QMessageBox.critical(None, "ERROR", "Fallo al generar el Punto de Salida, revisa la información insertada.")

    def display_point(self , punto):

        pointPath =  self.folder + '/EasyBasin/Capas_SIG/Punto_Salida/punto_salida.shp'

        #Cambiar a ETRS89 el CRS del selector de CRS
        self.mQgsProjection_PUNTO.setCrs(QgsCoordinateReferenceSystem(25830))

        #Herramienta para seleccionar un punto en el CANVAS y capturar sus coordenadas 
        self.lineEditX.setText(str(round(punto.x(),1)))
        self.lineEditY.setText(str(round(punto.y(),1)))
        self.canvas.unsetMapTool(self.pointTool)

        #Mostrar ventana EasyBasin
        self.show()

        #Bloquear opcion de modificar coordenadas X e Y
        self.lineEditX.setEnabled(False)
        self.lineEditY.setEnabled(False)
        self.mQgsProjection_PUNTO.setEnabled(False)

    def outlet(self):

        #Herramienta para seleccionar un punto en el CANVAS y capturar sus coordenadas    
        self.pointTool = QgsMapToolEmitPoint(self.canvas)
        self.canvas.setMapTool(self.pointTool)
        self.pointTool.canvasClicked.connect(self.display_point)

        #Cambia el CRS del proyecto a ETRS89
        ETRS89 = QgsCoordinateReferenceSystem(25830)
        QgsProject.instance().setCrs(ETRS89)  
        self.canvas.setDestinationCrs(ETRS89)
        self.canvas.refresh()

        #Añadir check
        self.labelCheck.setText("✔")

        #Esconder ventana EasyBasin
        self.hide()

    def buffer(self):

        #Definir amplitud del buffer (km)
        try:
            buffer = float(self.lineEditMDT.text())*1000
        except:
            buffer = 0

        if QgsProject.instance().mapLayersByName('Buffered'):
            #Seleccionar capa por nombre
            Buffered = QgsProject.instance().mapLayersByName('Buffered')[0]
            #Eliminar mapa base del CANVAS
            QgsProject.instance().removeMapLayer(Buffered.id())

        #Crear buffer a partir del punto
        params = {'INPUT':self.folder + '/EasyBasin/Capas_SIG/Punto_Salida/punto_salida.shp',
                    'DISTANCE':buffer,
                    'SEGMENTS':5,
                    'END_CAP_STYLE':2,
                    'JOIN_STYLE':0,
                    'MITER_LIMIT':2,
                    'DISSOLVE':False,
                    'OUTPUT':'TEMPORARY_OUTPUT'}
        processing.runAndLoadResults("native:buffer", params)

        Buffered = QgsProject.instance().mapLayersByName('Buffered')[0]
        #Cambiar color y tamaño capa
        symbol = QgsFillSymbol.createSimple({'color':'red','color_border':'red','width_border':'0.5','style':'no'})
        Buffered.renderer().setSymbol(symbol)
        Buffered.triggerRepaint()
        self.iface.layerTreeView().refreshLayerSymbology(Buffered.id())

        # #Activar capa a editar
        # layer = QgsProject.instance().mapLayersByName('Buffered')[0]
        # self.iface.layerTreeView().refreshLayerSymbology( layer.id() )
        # #Zoom a la capa activa (funciona)
        # zoom = layer.extent()
        # self.canvas.setExtent(zoom)

    def raster(self):   

        self.progressBar.setValue(10)
        self.labelBar.setText("Procesando...")
        # self.iface.mainWindow().blockSignals(True)

        fileName = self.inputRaster.filePath()
        rlayer = QgsRasterLayer(fileName,"MDT")
        crs_MDT = rlayer.crs()

        if not crs_MDT == QgsCoordinateReferenceSystem('EPSG:25830'):

            #Reproyectar MDT a ETRS89                            
            params = {'INPUT':fileName,
                        'SOURCE_CRS':crs_MDT,
                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:25830'),
                        'RESAMPLING':0,
                        'NODATA':None,
                        'TARGET_RESOLUTION':None,
                        'OPTIONS':'',
                        'DATA_TYPE':0,
                        'TARGET_EXTENT':None,
                        'TARGET_EXTENT_CRS':None,
                        'MULTITHREADING':False,
                        'EXTRA':'',
                        'OUTPUT': self.folder + '/EasyBasin/Capas_SIG/MDT/MDT_ETRS89.tif'}
            processing.run("gdal:warpreproject", params)

            self.inputRaster.setFilePath(self.folder + '/EasyBasin/Capas_SIG/MDT/MDT_ETRS89.tif')

        self.progressBar.setValue(30)

        #Definir amplitud del buffer (km)
        buffer = float(self.lineEditMDT.text())*1000

        #Crear buffer a partir del punto
        params = {'INPUT':self.folder + '/EasyBasin/Capas_SIG/Punto_Salida/punto_salida.shp',
                    'DISTANCE':buffer,
                    'SEGMENTS':5,
                    'END_CAP_STYLE':2,
                    'JOIN_STYLE':0,
                    'MITER_LIMIT':2,
                    'DISSOLVE':False,
                    'OUTPUT':self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/buffer.shp'}
        processing.run("native:buffer", params)

        self.progressBar.setValue(40)

        #Recortar MDT con buffer         
        params = {'INPUT':fileName,
                    'MASK':self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/buffer.shp',
                    'NODATA':None,
                    'ALPHA_BAND':False,
                    'CROP_TO_CUTLINE':True,
                    'KEEP_RESOLUTION':False,
                    'OPTIONS':'',
                    'DATA_TYPE':0,
                    'OUTPUT':self.folder + '/EasyBasin/Capas_SIG/MDT/MDT.tif'} 
        processing.run("gdal:cliprasterbymasklayer", params)

        self.progressBar.setValue(50)

        #Añadir MDT a QGIS
        fileName2 = self.folder + '/EasyBasin/Capas_SIG/MDT/MDT.tif'
        fileInfo = QFileInfo(fileName2)
        baseName = fileInfo.baseName()
        MDT = QgsRasterLayer(fileName2, baseName)          
        QgsProject.instance().addMapLayer(MDT)

        #Eliminar mapa base del CANVAS
        BaseMap = QgsProject.instance().mapLayersByName('Mapa Base')[0]
        QgsProject.instance().removeMapLayer(BaseMap.id())
        #Elimiar capa de zona de trabajo
        spain = QgsProject.instance().mapLayersByName('Límites de aplicación EasyBasin')[0]
        QgsProject.instance().removeMapLayer(spain.id())

        #Seleccionar capa por nombre
        layer = QgsProject.instance().mapLayersByName('MDT')[0]

        #Cambiar rampa de colores raster
        provider = layer.dataProvider()
        extent = layer.extent()
        stats = provider.bandStatistics(1, QgsRasterBandStats.All, extent, 0)

        #Valores de los intervalos
        minimum = stats.minimumValue
        maximum = stats.maximumValue
        value_range = maximum - minimum
        intervals = 4  # For example, divide the range into 4 intervals
        interval_values = [minimum + (value_range / intervals) * i for i in range(intervals + 1)]

        #Colores de los intervalos
        colors = ['#66ffcc', '#663300', '#ff9900', '#008000', '#ffffff']  
        ramp_items = [QgsColorRampShader.ColorRampItem(interval_values[i], QColor(colors[i])) for i in range(len(interval_values))]

        #Setup de la rampa de colores
        raster_shader = QgsRasterShader()
        color_ramp = QgsColorRampShader()
        color_ramp.setColorRampItemList(ramp_items)
        color_ramp.setColorRampType(QgsColorRampShader.Interpolated)
        raster_shader.setRasterShaderFunction(color_ramp)

        # Aplicar renderer
        renderer = QgsSingleBandPseudoColorRenderer(provider, 1, raster_shader)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        self.iface.mapCanvas().refreshAllLayers()
        self.iface.layerTreeView().refreshLayerSymbology(layer.id())

        self.progressBar.setValue(90)

        #Añadir mapa de sombras
        fileName = self.folder + '/EasyBasin/Capas_SIG/MDT/MDT.tif'

        params = {'INPUT':fileName,
                    'Z_FACTOR':1,
                    'AZIMUTH':300,
                    'V_ANGLE':40,
                    'OUTPUT':self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/Hillshade.tif'}
        processing.run("qgis:hillshade",params)

        fileName = self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/Hillshade.tif'
        fileInfo = QFileInfo(fileName)
        baseName = fileInfo.baseName()
        rlayer = QgsRasterLayer(fileName,baseName)
        rlayer.setCrs(QgsCoordinateReferenceSystem(25830,QgsCoordinateReferenceSystem.EpsgCrsId))
        rlayer.renderer().setOpacity(0.35)
        QgsProject.instance().addMapLayer(rlayer)

        #Activar capa a editar
        layer = QgsProject.instance().mapLayersByName('Hillshade')[0]
        self.iface.layerTreeView().refreshLayerSymbology( layer.id() )

        #Zoom a la capa activa
        zoom = layer.extent()
        self.canvas.setExtent(zoom)

        #Desactivar boton avance 2
        self.pushButtonAvance2.setEnabled(False)
        self.pushButtonStreams.setEnabled(True)

        #Desactivar cuadro buffer
        self.lineEditMDT.setEnabled(False)

        self.labelBar.setText("")
        self.progressBar.setValue(0)

        self.umbral()

        #Seleccionar capa por nombre
        layer = QgsProject.instance().mapLayersByName('Punto de Salida')[0]

        #Mover capa punto a la primera posicion en el panel de capas
        root = QgsProject.instance().layerTreeRoot()
        point = root.findLayer(layer.id())
        pointClone = point.clone()
        parent = point.parent()
        parent.insertChildNode(0, pointClone)
        parent.removeChildNode(point)

        #Cambiar nombre de la capa buffer
        Buffered = QgsProject.instance().mapLayersByName('Buffered')[0]
        Buffered.setName('Buffer de recorte')

    def umbral(self):

        umbral = self.lineEditStreams_cells.text()

        #Capturar el tamaño X e Y de las celdas de un raster (m)
        mdt = QgsRasterLayer(self.folder + '/EasyBasin/Capas_SIG/MDT/MDT.tif')
        pixelSizeX = mdt.rasterUnitsPerPixelX()
        pixelSizeY = mdt.rasterUnitsPerPixelY()
        
        #Transforma el numero de celdas que drena a un punto para considerarlo cauce a km2
        area = round((float(umbral)*float(pixelSizeX)*float(pixelSizeY))/10**6)

        self.lineEditStreams_area.setText(str(area))
        self.lineEditStreams_cells.setEnabled(False)

    def umbralCeldas(self):

        umbral = self.lineEditStreams_area.text()

        #Capturar el tamaño X e Y de las celdas de un raster (m)
        mdt = QgsRasterLayer(self.folder + '/EasyBasin/Capas_SIG/MDT/MDT.tif')
        pixelSizeX = mdt.rasterUnitsPerPixelX()
        pixelSizeY = mdt.rasterUnitsPerPixelY()

        try:
            #Transforma a km2 (area) el numero de celdas que drena a un punto para considerarlo cauce
            celdas = round((float(umbral)*10**6)/(float(pixelSizeX)*float(pixelSizeY)))
        except:
            celdas = 0

        self.lineEditStreams_cells.setText(str(celdas))

    def stream(self):

        self.progressBar.setValue(10)
        self.labelBar.setText("Calculando red de drenaje...")

        #Si no existe la el MDT corregido, lo genera
        if not os.path.exists(self.folder + '/EasyBasin/Capas_SIG/MDT/MDT_corregido.tif'):

            #Proceso para corregir el MDT
            params ={'input': self.folder + '/EasyBasin/Capas_SIG/MDT/MDT.tif',
                        'format':0,
                        '-f':False,
                        'output': self.folder + '/EasyBasin/Capas_SIG/MDT/MDT_corregido.tif',
                        'direction':"None",
                        'areas':"None",
                        'GRASS_REGION_PARAMETER':None,
                        'GRASS_REGION_CELLSIZE_PARAMETER':0,
                        'GRASS_RASTER_FORMAT_OPT':'',
                        'GRASS_RASTER_FORMAT_META':''}   
            processing.run("grass7:r.fill.dir", params)

        #Si la capa de cauces existe, la eliminamos
        if QgsProject.instance().mapLayersByName('Vectorized'):
            #Seleccionar capa por nombre
            Vectorized = QgsProject.instance().mapLayersByName('Vectorized')[0]
            #Eliminar mapa base del CANVAS
            QgsProject.instance().removeMapLayer(Vectorized.id())    

        self.progressBar.setValue(30)

        #Proceso para  crear los cauces y mapa de direccion de flujo
        umbral = self.lineEditStreams_cells.text()

        params2 ={
                    'elevation': self.folder + '/EasyBasin/Capas_SIG/MDT/MDT_corregido.tif',
                    'depression':None,
                    'flow':None,
                    'disturbed_land':None,
                    'blocking':None,
                    'threshold':float(umbral),
                    'max_slope_length':None,
                    'convergence':5,
                    'memory':300,
                    '-s':True,
                    '-m':False,
                    '-4':False,
                    '-a':False,
                    'b':False,
                    'accumulation':'None',
                    'drainage': 'None',
                    'basin': 'None',
                    'stream': 'TEMPORARY_OUTPUT',
                    'half_basin':'None',
                    'length_slope':'None',
                    'slope_steepness':'None',
                    'tci':'None',
                    'spi':'None',
                    'GRASS_REGION_PARAMETER':None,
                    'GRASS_REGION_CELLSIZE_PARAMETER':0,
                    'GRASS_RASTER_FORMAT_OPT':'',
                    'GRASS_RASTER_FORMAT_META':''}
        processing.runAndLoadResults("grass7:r.watershed", params2)

        self.progressBar.setValue(60) 

        #Seleccionar capa temporal y conseguir ruta
        streams = QgsProject.instance().mapLayersByName("Stream segments")[0]
        streamsPath = streams.source()

        #Proceso para pasar de raster a shape CAUCES
        params3 ={
                    'input': streamsPath,
                    'type':0,
                    'column':'value',
                    '-s':True,
                    '-v':False,
                    '-z':False,
                    '-b':False,
                    '-t':True,
                    'output': 'TEMPORARY_OUTPUT',
                    'GRASS_REGION_PARAMETER':None,
                    'GRASS_REGION_CELLSIZE_PARAMETER':0,
                    'GRASS_OUTPUT_TYPE_PARAMETER':0,
                    'GRASS_VECTOR_DSCO':'',
                    'GRASS_VECTOR_LCO':'',
                    'GRASS_VECTOR_EXPORT_NOCAT':False}
        processing.runAndLoadResults("grass7:r.to.vect", params3)

        self.progressBar.setValue(80)

        #Cambiar color y tamaño capa
        layer = QgsProject.instance().mapLayersByName("Vectorized")[0]
        symbol = QgsLineSymbol.createSimple({'width': '0.5', 'color': 'blue'})
        layer.renderer().setSymbol(symbol)
        layer.triggerRepaint()
        self.iface.layerTreeView().refreshLayerSymbology( layer.id() )

        streams = QgsProject.instance().mapLayersByName("Stream segments")[0]
        #Eliminar stream segments del CANVAS
        QgsProject.instance().removeMapLayer(streams.id())

        #Eliminar capa None si existe en el CANVAS
        project = QgsProject.instance()
        for layer in project.mapLayers().values():
            if layer.name() == "None":
                project.removeMapLayer(layer.id())

        self.progressBar.setValue(100)
        self.progressBar.setValue(0)

        self.labelBar.setText("")

        self.pushButtonAvance3.setEnabled(True)

        #Añadir check
        self.labelCheck2.setText("✔")


    def stream2(self):

        self.labelBar.setText("Calculando red de drenaje...")
        self.progressBar.setValue(10)

        #Si la capa de cauces existe, la eliminamos
        if QgsProject.instance().mapLayersByName('Vectorized'):
            #Seleccionar capa por nombre
            Vectorized = QgsProject.instance().mapLayersByName('Vectorized')[0]
            #Eliminar mapa base del CANVAS
            QgsProject.instance().removeMapLayer(Vectorized.id())   

        self.progressBar.setValue(30)

        #Proceso para  crear los cauces y mapa de direccion de flujo
        umbral = self.lineEditStreams_cells.text()

        params2 ={
                    'elevation': self.folder + '/EasyBasin/Capas_SIG/MDT/MDT_corregido.tif',
                    'depression':None,
                    'flow':None,
                    'disturbed_land':None,
                    'blocking':None,
                    'threshold':float(umbral),
                    'max_slope_length':None,
                    'convergence':5,
                    'memory':300,
                    '-s':True,
                    '-m':False,
                    '-4':False,
                    '-a':False,
                    'b':False,
                    'accumulation':'None',
                    'drainage': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/drainage_direction.tif',
                    'basin': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subcuencas.tif',
                    'stream': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/cauces.tif',
                    'half_basin':'None',
                    'length_slope':'None',
                    'slope_steepness':'None',
                    'tci':'None',
                    'spi':'None',
                    'GRASS_REGION_PARAMETER':None,
                    'GRASS_REGION_CELLSIZE_PARAMETER':0,
                    'GRASS_RASTER_FORMAT_OPT':'',
                    'GRASS_RASTER_FORMAT_META':''}
        processing.run("grass7:r.watershed", params2)

        self.progressBar.setValue(60) 

        #Proceso para pasar de raster a shape CAUCES
        params3 ={
                    'input': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/cauces.tif',
                    'type':0,
                    'column':'value',
                    '-s':True,
                    '-v':False,
                    '-z':False,
                    '-b':False,
                    '-t':True,
                    'output': self.folder + '/EasyBasin/Capas_SIG/Red_Drenaje/Red_drenaje.shp',
                    'GRASS_REGION_PARAMETER':None,
                    'GRASS_REGION_CELLSIZE_PARAMETER':0,
                    'GRASS_OUTPUT_TYPE_PARAMETER':0,
                    'GRASS_VECTOR_DSCO':'',
                    'GRASS_VECTOR_LCO':'',
                    'GRASS_VECTOR_EXPORT_NOCAT':False}
        processing.run("grass7:r.to.vect", params3)

        self.progressBar.setValue(80)

        #Añadir capa vectorial
        layer_streams = QgsVectorLayer(self.folder + '/EasyBasin/Capas_SIG/Red_Drenaje/Red_drenaje.shp', 'Red de Drenaje', "ogr")
        QgsProject.instance().addMapLayer(layer_streams) 

        #Cambiar color y tamaño capa
        layer = QgsProject.instance().mapLayersByName("Red de Drenaje")[0]
        symbol = QgsLineSymbol.createSimple({'width': '0.5', 'color': 'blue'})
        layer.renderer().setSymbol(symbol)
        layer.triggerRepaint()
        self.iface.layerTreeView().refreshLayerSymbology( layer.id() )

        #Snap punto de salida al cauce
        params4 ={
                    'INPUT': self.folder + '/EasyBasin/Capas_SIG/Punto_Salida/punto_salida.shp',
                    'REFERENCE_LAYER': self.folder + '/EasyBasin/Capas_SIG/Red_Drenaje/Red_drenaje.shp',
                    'TOLERANCE':1000,
                    'BEHAVIOR':3,
                    'OUTPUT': self.folder + '/EasyBasin/Capas_SIG/Punto_Salida/punto_salida_corregido.shp'}
        processing.runAndLoadResults("native:snapgeometries", params4)

        #Cambiar nombre de la capa punto
        snappedPoint = QgsProject.instance().mapLayersByName('punto_salida_corregido')[0]
        snappedPoint.setName('Punto de Salida (corregido)')

        #Eliminar punto de salida antiguo
        point = QgsProject.instance().mapLayersByName('Punto de Salida')[0]
        QgsProject.instance().removeMapLayer(point.id()) 

        self.progressBar.setValue(100)
        self.progressBar.setValue(0)

        #Desactivar bloqueo de boton PUNTO DE SALIDA
        self.pushButtonBasin.setEnabled(True)
        self.pushButtonStreams.setEnabled(False)
        self.pushButtonAvance3.setEnabled(False)

        self.labelBar.setText("")

        # info = QMessageBox()
        # info.information(None, "Red de Drenaje", "Proceso Finalizado")
        # info.setIcon(QIcon(":/imgBase/images/icon.png"))
        # info.exec_()

    def basin(self):

        self.labelBar.setText("Creando cuenca hidrográfica...")
        self.progressBar.setValue(10)

        # Seleccionar capa punto
        point_layer = QgsVectorLayer(self.folder + '/EasyBasin/Capas_SIG/Punto_Salida/punto_salida_corregido.shp', 'Point Layer', 'ogr')

        # Leer tabla de atributos
        features = point_layer.getFeatures()

        # Iterar a traves de los atributos
        for feature in features:
            # Conseguir lageometria del atributo
            geometry = feature.geometry()
            # Extraer coordenadas X e Y
            Xcoordinate = str(geometry.asPoint().x())
            Ycoordinate = str(geometry.asPoint().y())

        #Proceso para crear cuenca en formato raster
        params4 ={
                    'input': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/drainage_direction.tif',
                    'coordinates':Xcoordinate + "," + Ycoordinate,
                    'output': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/basin.tif',
                    'GRASS_REGION_PARAMETER':None,
                    'GRASS_REGION_CELLSIZE_PARAMETER':0,
                    'GRASS_RASTER_FORMAT_OPT':'',
                    'GRASS_RASTER_FORMAT_META':''}
        processing.run("grass7:r.water.outlet", params4)

        self.progressBar.setValue(30)

        #Proceso para pasar de raster a shape CUENCA
        params5 ={
                    'input':self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/basin.tif',
                    'type':2,
                    'column':'value',
                    '-s':True,
                    '-v':False,
                    '-z':False,
                    '-b':False,
                    '-t':True,
                    'output':self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/basin.shp',
                    'GRASS_REGION_PARAMETER':None,
                    'GRASS_REGION_CELLSIZE_PARAMETER':0,
                    'GRASS_OUTPUT_TYPE_PARAMETER':0,
                    'GRASS_VECTOR_DSCO':'',
                    'GRASS_VECTOR_LCO':'',
                    'GRASS_VECTOR_EXPORT_NOCAT':False}
        processing.run("grass7:r.to.vect", params5)
        
        #Arreglar problemas geometria 
        params = {
                    'INPUT':self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/basin.shp',
                    'OUTPUT':self.folder + '/EasyBasin/Capas_SIG/Cuenca_Hidrografica/cuenca_hidrografica.shp'}
        processing.run("native:fixgeometries", params)

        self.progressBar.setValue(60)

        #Añadir capa vectorial y definir sistema coordenadas
        layer_basin = QgsVectorLayer(self.folder + '/EasyBasin/Capas_SIG/Cuenca_Hidrografica/cuenca_hidrografica.shp', 'Cuenca Hidrografica', "ogr")
        crs = layer_basin.crs()
        crs.createFromId(25830) 
        layer_basin.setCrs(crs)
        QgsProject.instance().addMapLayer(layer_basin) 

        self.progressBar.setValue(70) 

        #Recortar capas vectoriales
        params6 ={
                    'INPUT': self.folder + '/EasyBasin/Capas_SIG/Red_Drenaje/Red_drenaje.shp',
                    'OVERLAY': self.folder + '/EasyBasin/Capas_SIG/Cuenca_Hidrografica/cuenca_hidrografica.shp',
                    'OUTPUT': self.folder + '/EasyBasin/Capas_SIG/Red_Drenaje/Red_drenaje_cuenca.shp'}
        processing.run("native:clip", params6)

        #Añadir capa vectorial y definir sistema coordenadas
        layer_stream = QgsVectorLayer(self.folder + '/EasyBasin/Capas_SIG/Red_Drenaje/Red_drenaje_cuenca.shp', 'Red de Drenaje (Cuenca)', 'ogr')
        crs = layer_stream.crs()
        crs.createFromId(25830) 
        layer_stream.setCrs(crs)
        QgsProject.instance().addMapLayer(layer_stream) 

        self.progressBar.setValue(80) 

        #Eliminar capa cauces mediante nombre     
        stream = QgsProject.instance().mapLayersByName('Red de Drenaje')[0]
        QgsProject.instance().removeMapLayer(stream.id())

        self.progressBar.setValue(85)        

        #Activar capa a editar
        layer = QgsProject.instance().mapLayersByName("Cuenca Hidrografica")[0]

        #Añadir campo nuevo a la capa seleccionada
        caps = layer.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.AddAttributes:
            layer.dataProvider().addAttributes([QgsField("AREA", QVariant.Int)])
            layer.dataProvider().addAttributes([QgsField("PERIMETRO", QVariant.Int)])  
        layer.updateFields()

        #Activar el editor
        layer.startEditing()
        #Expresiones utilizadas en la calculador de campos
        e1 = QgsExpression('$area')
        e2 = QgsExpression('$perimeter')
        #Clases necesarias para utilizar calculadora de campos
        context = QgsExpressionContext()
        scope = QgsExpressionContextScope()
        context.appendScope(scope)
        #Añadir los resultados a la tabla de atributos
        for f in layer.getFeatures():
            context.setFeature(f)
            f['AREA'] = e1.evaluate(context)
            f['PERIMETRO'] = e2.evaluate(context)
            layer.updateFeature(f)
        #Cerrar editor
        layer.commitChanges()

        #Proceso calcular altitud maxima y minima - ZONAL_STATISTICS
        params1 ={
                    'INPUT': self.folder + '/EasyBasin/Capas_SIG/Cuenca_Hidrografica/cuenca_hidrografica.shp',
                    'INPUT_RASTER': self.folder + '/EasyBasin/Capas_SIG/MDT/MDT_corregido.tif',
                    'RASTER_BAND':1,
                    'COLUMN_PREFIX':'ALT_',
                    'STATISTICS':[5,6],
                    'OUTPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/basin_atr1.shp'}
        processing.run("native:zonalstatisticsfb", params1)

        #Proceso calcular region umbral escorrentia - ZONAL_STATISTICS
        params2 ={
                    'INPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/basin_atr1.shp',
                    'INPUT_RASTER': 'C:/EasyBasin/Rasters/P0/Regiones_p0.tif',
                    'RASTER_BAND':1,
                    'COLUMN_PREFIX':'Reg_p0_',
                    'STATISTICS':[9],
                    'OUTPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/basin_atr2.shp'}
        processing.run("native:zonalstatisticsfb", params2)

        #Proceso calcular indice de torrencialidad I1/Id - ZONAL_STATISTICS
        params3 ={
                    'INPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/basin_atr2.shp',
                    'INPUT_RASTER': 'C:/EasyBasin/Rasters/Indice_Torrencialidad/i1id.tif',
                    'RASTER_BAND':1,
                    'COLUMN_PREFIX':'I1Id_Torr_',
                    'STATISTICS':[9],
                    'OUTPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/basin_atr3.shp'}
        processing.run("native:zonalstatisticsfb", params3)

        #Proceso calcular area impermeable - ZONAL_STATISTICS
        params4 ={
                    'INPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/basin_atr3.shp',
                    'INPUT_RASTER': 'C:/EasyBasin/Rasters/Impermeable/suelo_imp.tif',
                    'RASTER_BAND':1,
                    'COLUMN_PREFIX':'Area_Imp_',
                    'STATISTICS':[1],
                    'OUTPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/basin_atr4.shp'}
        processing.run("native:zonalstatisticsfb", params4)

        #Proceso calcular p0 medio 500m - ZONAL_STATISTICS
        params5 ={
                    'INPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/basin_atr4.shp',
                    'INPUT_RASTER': 'C:/EasyBasin/Rasters/P0/p0_MITECO_500m.tif',
                    'RASTER_BAND':1,
                    'COLUMN_PREFIX':'p0_500m_',
                    'STATISTICS':[2],
                    'OUTPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/basin_atr5.shp'}
        processing.run("native:zonalstatisticsfb", params5)

        #Proceso calcular p0 medio 100m CLC2000 - ZONAL_STATISTICS
        params6 ={
                    'INPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/basin_atr5.shp',
                    'INPUT_RASTER': 'C:/EasyBasin/Rasters/P0/p0_clc2000_100m.tif',
                    'RASTER_BAND':1,
                    'COLUMN_PREFIX':'p0_CLC2000_',
                    'STATISTICS':[2],
                    'OUTPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/basin_atr6.shp'}
        processing.run("native:zonalstatisticsfb", params6)

        #Proceso calcular p0 medio 100m CLC2018 - ZONAL_STATISTICS
        params7 ={
                    'INPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/basin_atr6.shp',
                    'INPUT_RASTER': 'C:/EasyBasin/Rasters/P0/p0_clc2018_100m.tif',
                    'RASTER_BAND':1,
                    'COLUMN_PREFIX':'p0_CLC2018_',
                    'STATISTICS':[2],
                    'OUTPUT': self.folder + '/EasyBasin/Capas_SIG/Cuenca_Hidrografica/cuenca_hidrografica_atr.shp'}
        processing.runAndLoadResults("native:zonalstatisticsfb", params7)

        #Eliminar capa cauces mediante nombre     
        stream = QgsProject.instance().mapLayersByName('Cuenca Hidrografica')[0]
        QgsProject.instance().removeMapLayer(stream.id()) 

        #Cambiar nombre de la capa punto
        snappedPoint = QgsProject.instance().mapLayersByName('cuenca_hidrografica_atr')[0]
        snappedPoint.setName('Cuenca Hidrográfica')

        #Activar capa a editar
        layer = QgsProject.instance().mapLayersByName('Cuenca Hidrográfica')[0]
        #Cambiar color y tamaño capa
        symbol = QgsFillSymbol.createSimple({'color':'red','color_border':'red','width_border':'0.5','style':'no'})
        layer.renderer().setSymbol(symbol)
        layer.triggerRepaint()
        self.iface.layerTreeView().refreshLayerSymbology( layer.id() )

        #Zoom a la capa activa
        zoom = layer.extent()
        self.canvas.setExtent(zoom)

        self.progressBar.setValue(90)  

        #Activar capa a editar        
        layer = QgsProject.instance().mapLayersByName("Red de Drenaje (Cuenca)")[0]

        #Añadir campo nuevo a la capa seleccionada
        caps = layer.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.AddAttributes:
            layer.dataProvider().addAttributes([QgsField("LONGITUD", QVariant.Int)])
        layer.updateFields()
        #Activar el editor
        layer.startEditing()
        #Expresiones utilizadas en la calculador de campos
        e3 = QgsExpression('$length')
        #Clases necesarias para utilizar calculadora de campos
        context = QgsExpressionContext()
        scope = QgsExpressionContextScope()
        context.appendScope(scope)
        #Añadir los resultados a la tabla de atributos
        for f in layer.getFeatures():
            context.setFeature(f)
            f['LONGITUD'] = e3.evaluate(context)
            layer.updateFeature(f)
        #Cerrar editor
        layer.commitChanges()

        #Cambiar color y tamaño capa
        symbol = QgsLineSymbol.createSimple({'width': '0.5', 'color': 'blue'})
        layer.renderer().setSymbol(symbol)
        layer.triggerRepaint()
        self.iface.layerTreeView().refreshLayerSymbology( layer.id() )

        #Condicional para calcular subcuencas
        if os.path.exists(self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subcuencas.tif'):

            self.labelBar.setText("Generando subcuencas...")
            self.progressBar.setValue(10)          

            #Recortar capa raster con capa vectorial
            params7 ={
            'INPUT':self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subcuencas.tif',
            'MASK':self.folder + '/EasyBasin/Capas_SIG/Cuenca_Hidrografica/Cuenca_hidrografica.shp',
            'NODATA':None,
            'ALPHA_BAND':False,
            'CROP_TO_CUTLINE':True,
            'KEEP_RESOLUTION':False,
            'OPTIONS':'',
            'DATA_TYPE':0,
            'OUTPUT':self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subcuencas_recortado.tif'}
            processing.run("gdal:cliprasterbymasklayer", params7)

            self.progressBar.setValue(20)    

            #Proceso para pasar de raster a shape CUENCA
            params8 ={
            'input':self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subcuencas_recortado.tif',
            'type':2,
            'column':'value',
            '-s':True,
            '-v':False,
            '-z':False,
            '-b':False,
            '-t':True,
            'output':self.folder + '/EasyBasin/HMS/Subcuencas/subcuencas.shp',
            'GRASS_REGION_PARAMETER':None,
            'GRASS_REGION_CELLSIZE_PARAMETER':0,
            'GRASS_OUTPUT_TYPE_PARAMETER':0,
            'GRASS_VECTOR_DSCO':'',
            'GRASS_VECTOR_LCO':'',
            'GRASS_VECTOR_EXPORT_NOCAT':False}
            processing.run("grass7:r.to.vect", params8)

            self.progressBar.setValue(30) 

            #Añadir capa vectorial
            layer_subbasins = QgsVectorLayer(self.folder + '/EasyBasin/HMS/Subcuencas/subcuencas.shp', 'Subcuencas', "ogr")
            crs = layer_subbasins.crs()
            crs.createFromId(25830) 
            layer_subbasins.setCrs(crs)
            QgsProject.instance().addMapLayer(layer_subbasins) 

            #Activar capa a editar
            layer = QgsProject.instance().mapLayersByName("Subcuencas")[0]

            #Añadir campo nuevo a la capa activada   
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
                layer.dataProvider().addAttributes([QgsField("AREA", QVariant.Int)])
                layer.dataProvider().addAttributes([QgsField("PERIMETRO", QVariant.Int)])  
            layer.updateFields()

            self.progressBar.setValue(40) 

            #Activar el editor
            layer.startEditing()
            #Expresiones utilizadas en la calculador de campos
            e1 = QgsExpression('$area')
            e2 = QgsExpression('$perimeter')
            #Clases necesarias para utilizar calculadora de campos
            context = QgsExpressionContext()
            scope = QgsExpressionContextScope()
            context.appendScope(scope)
            #Añadir los resultados a la tabla de atributos
            for f in layer.getFeatures():
                context.setFeature(f)
                f['AREA'] = e1.evaluate(context)
                f['PERIMETRO'] = e2.evaluate(context)
                layer.updateFeature(f)
            #Cerrar editor
            layer.commitChanges()

            self.progressBar.setValue(50)

            #Arreglar problemas geometria 
            params = {
                        'INPUT':self.folder + '/EasyBasin/HMS/Subcuencas/subcuencas.shp',
                        'OUTPUT':self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subcuencas_fix.shp'}
            processing.run("native:fixgeometries", params) 

            #Proceso calcular altitud maxima y minima - ZONAL_STATISTICS
            params1 ={
                        'INPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subcuencas_fix.shp',
                        'INPUT_RASTER': self.folder + '/EasyBasin/Capas_SIG/MDT/MDT_corregido.tif',
                        'RASTER_BAND':1,
                        'COLUMN_PREFIX':'ALT_',
                        'STATISTICS':[5,6],
                        'OUTPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subbasin_atr1.shp'}
            processing.run("native:zonalstatisticsfb", params1)

            self.progressBar.setValue(60)

            #Proceso calcular region umbral escorrentia - ZONAL_STATISTICS
            params2 ={
                        'INPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subbasin_atr1.shp',
                        'INPUT_RASTER': 'C:/EasyBasin/Rasters/P0/Regiones_p0.tif',
                        'RASTER_BAND':1,
                        'COLUMN_PREFIX':'Reg_p0_',
                        'STATISTICS':[9],
                        'OUTPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subbasin_atr2.shp'}
            processing.run("native:zonalstatisticsfb", params2)

            self.progressBar.setValue(70)

            #Proceso calcular indice de torrencialidad I1/Id - ZONAL_STATISTICS
            params3 ={
                        'INPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subbasin_atr2.shp',
                        'INPUT_RASTER': 'C:/EasyBasin/Rasters/Indice_Torrencialidad/i1id.tif',
                        'RASTER_BAND':1,
                        'COLUMN_PREFIX':'I1Id_Torr_',
                        'STATISTICS':[9],
                        'OUTPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subbasin_atr3.shp'}
            processing.run("native:zonalstatisticsfb", params3)

            self.progressBar.setValue(80)

            #Proceso calcular area impermeable - ZONAL_STATISTICS
            params4 ={
                        'INPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subbasin_atr3.shp',
                        'INPUT_RASTER': 'C:/EasyBasin/Rasters/Impermeable/suelo_imp.tif',
                        'RASTER_BAND':1,
                        'COLUMN_PREFIX':'Area_Imp_',
                        'STATISTICS':[1],
                        'OUTPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subbasin_atr4.shp'}
            processing.run("native:zonalstatisticsfb", params4)

            #Proceso calcular p0 medio 500m - ZONAL_STATISTICS
            params5 ={
                        'INPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subbasin_atr4.shp',
                        'INPUT_RASTER': 'C:/EasyBasin/Rasters/P0/p0_MITECO_500m.tif',
                        'RASTER_BAND':1,
                        'COLUMN_PREFIX':'p0_500m_',
                        'STATISTICS':[2],
                        'OUTPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subbasin_atr5.shp'}
            processing.run("native:zonalstatisticsfb", params5)

            self.progressBar.setValue(90)

            #Proceso calcular p0 medio 100m CLC2000 - ZONAL_STATISTICS
            params6 ={
                        'INPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subbasin_atr5.shp',
                        'INPUT_RASTER': 'C:/EasyBasin/Rasters/P0/p0_clc2000_100m.tif',
                        'RASTER_BAND':1,
                        'COLUMN_PREFIX':'p0_CLC2000_',
                        'STATISTICS':[2],
                        'OUTPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subbasin_atr6.shp'}
            processing.run("native:zonalstatisticsfb", params6)

            #Proceso calcular p0 medio 100m CLC2018 - ZONAL_STATISTICS
            params7 ={
                        'INPUT': self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/subbasin_atr6.shp',
                        'INPUT_RASTER': 'C:/EasyBasin/Rasters/P0/p0_clc2018_100m.tif',
                        'RASTER_BAND':1,
                        'COLUMN_PREFIX':'p0_CLC2018_',
                        'STATISTICS':[2],
                        'OUTPUT': self.folder + '/EasyBasin/HMS/Subcuencas/subcuencas_atr.shp'}
            processing.runAndLoadResults("native:zonalstatisticsfb", params7)

            #Eliminar capa cauces mediante nombre     
            stream = QgsProject.instance().mapLayersByName('Subcuencas')[0]
            QgsProject.instance().removeMapLayer(stream.id()) 

            #Cambiar nombre de la capa punto
            snappedPoint = QgsProject.instance().mapLayersByName('subcuencas_atr')[0]
            snappedPoint.setName('Subcuencas')

            #Activar capa a editar
            layer = QgsProject.instance().mapLayersByName('Subcuencas')[0]

            #Cambiar color y tamaño capa
            symbol = QgsFillSymbol.createSimple({'color':'red','color_border':'black','width_border':'0.1','style':'no'})
            layer.renderer().setSymbol(symbol)

            #Añadir etiquetas a las subcuencas
            settings = QgsPalLayerSettings()
            settings.fieldName = 'cat'
            labeling = QgsVectorLayerSimpleLabeling(settings)
            layer.setLabeling(labeling)
            layer.setLabelsEnabled(True)
            layer.triggerRepaint()
            self.iface.layerTreeView().refreshLayerSymbology( layer.id() )

            self.progressBar.setValue(100)
        self.progressBar.setValue(0)
        self.labelBar.setText("")

        self.LongestFlowPath()

    def LongestFlowPath(self):

        self.labelBar.setText("Calculando cauce principal...")
        self.progressBar.setValue(0) 

        #Proceso para  recortar raster MDT corregido con shape CUENCA
        params1 ={
                    'INPUT':self.folder + '/EasyBasin/Capas_SIG/MDT/MDT_corregido.tif',
                    'MASK':self.folder + '/EasyBasin/Capas_SIG/Cuenca_Hidrografica/Cuenca_hidrografica.shp',
                    'NODATA':None,
                    'ALPHA_BAND':False,
                    'CROP_TO_CUTLINE':True,
                    'KEEP_RESOLUTION':False,
                    'OPTIONS':'',
                    'DATA_TYPE':0,
                    'OUTPUT':self.folder + '/EasyBasin/Capas_SIG/MDT/MDT_cuenca.tif'}
        processing.run("gdal:cliprasterbymasklayer", params1)

        self.progressBar.setValue(10)

        #Proceso para  crear cauces Cuenca
        limite = float(self.lineEditStreams_cells.text())
        limite2 = limite*0.1
        params2 ={
                    'elevation':self.folder + '/EasyBasin/Capas_SIG/MDT/MDT_cuenca.tif',
                    'depression':None,
                    'flow':None,
                    'disturbed_land':None,
                    'blocking':None,
                    'threshold':limite2,
                    'max_slope_length':None,
                    'convergence':5,
                    'memory':300,
                    '-s':True,
                    '-m':False,
                    '-4':False,
                    '-a':False,
                    'b':False,
                    'accumulation':'None',
                    'drainage':'None',
                    'basin':'None',
                    'stream':'TEMPORARY_OUTPUT',
                    'half_basin':'None',
                    'length_slope':'None',
                    'slope_steepness':'None',
                    'tci':'None',
                    'spi':'None',
                    'GRASS_REGION_PARAMETER':None,
                    'GRASS_REGION_CELLSIZE_PARAMETER':0,
                    'GRASS_RASTER_FORMAT_OPT':'',
                    'GRASS_RASTER_FORMAT_META':''}
        processing.runAndLoadResults("grass7:r.watershed", params2)

        self.progressBar.setValue(20) 

        #Seleccionar capa temporal y conseguir ruta
        streams = QgsProject.instance().mapLayersByName("Stream segments")[0]
        streamsPath = streams.source()

        #Proceso para pasar de raster a shape CAUCES Cuenca
        params3 ={
                    'input':streamsPath,
                    'type':0,
                    'column':'value',
                    '-s':True,
                    '-v':False,
                    '-z':False,
                    '-b':False,
                    '-t':True,
                    'output':self.folder + '/EasyBasin/HMS/Red_Drenaje/Red_drenaje_LFP.shp',
                    'GRASS_REGION_PARAMETER':None,
                    'GRASS_REGION_CELLSIZE_PARAMETER':0,
                    'GRASS_OUTPUT_TYPE_PARAMETER':0,
                    'GRASS_VECTOR_DSCO':'',
                    'GRASS_VECTOR_LCO':'',
                    'GRASS_VECTOR_EXPORT_NOCAT':False}
        processing.run("grass7:r.to.vect", params3)

        self.progressBar.setValue(30)    

        #Obtener puntos en los extremos de los cauces
        params4 ={
                    'input':self.folder + '/EasyBasin/HMS/Red_Drenaje/Red_drenaje_LFP.shp',
                    'type':[1],
                    'use':0,
                    'dmax':100,
                    '-i':False,
                    '-t':True,
                    'output':'TEMPORARY_OUTPUT',
                    'GRASS_REGION_PARAMETER':None,
                    'GRASS_SNAP_TOLERANCE_PARAMETER':-1,
                    'GRASS_MIN_AREA_PARAMETER':0.0001,
                    'GRASS_OUTPUT_TYPE_PARAMETER':0,
                    'GRASS_VECTOR_DSCO':'',
                    'GRASS_VECTOR_LCO':'',
                    'GRASS_VECTOR_EXPORT_NOCAT':False}
        processing.runAndLoadResults("grass7:v.to.points", params4)

        #Seleccionar capa temporal y conseguir ruta
        streamsV = QgsProject.instance().mapLayersByName("Points along lines")[0]
        streamsVPath = streamsV.source()

        self.progressBar.setValue(40)

        #Crear shapefile con distancia entre puntos extremos y oulet
        params5 = {
                    'INPUT':streamsVPath,
                    'INPUT_FIELD':'cat',
                    'TARGET':self.folder + '/EasyBasin/Capas_SIG/Punto_Salida/punto_salida_corregido.shp',
                    'TARGET_FIELD':'FID',
                    'MATRIX_TYPE':0,
                    'NEAREST_POINTS':0,
                    'OUTPUT':'TEMPORARY_OUTPUT'}
        processing.runAndLoadResults("qgis:distancematrix",params5)

        #Seleccionar capa temporal y conseguir ruta
        streamsD = QgsProject.instance().mapLayersByName("Distance matrix")[0]
        streamsDPath = streamsD.source()

        self.progressBar.setValue(50)  

        #Corregir shape de matriz de distancia a formato point        
        params6 = {
                    'INPUT':streamsDPath,
                    'OUTPUT':'TEMPORARY_OUTPUT'}
        processing.runAndLoadResults("native:multiparttosingleparts", params6)

        #Seleccionar capa temporal y cambiar nombre
        streamsDcorr = QgsProject.instance().mapLayersByName("Single parts")[0]
        streamsDcorrPath = streamsDcorr.source()

        #Eliminar punto duplicados        
        params7 = {
                    'INPUT':streamsDcorrPath,
                    'OUTPUT':'TEMPORARY_OUTPUT'}
        processing.runAndLoadResults("native:deleteduplicategeometries", params7)

        #Seleccionar capa temporal y cambiar nombre
        streamsDcorr = QgsProject.instance().mapLayersByName("Cleaned")[0]
        streamsDcorr.setName('Puntos Cauces')

        #Eliminar capas sobrantes
        layer0 = QgsProject.instance().mapLayersByName('Stream segments')[0]
        QgsProject.instance().removeMapLayer(layer0.id()) 
        layer1 = QgsProject.instance().mapLayersByName('Distance matrix')[0]
        QgsProject.instance().removeMapLayer(layer1.id()) 
        layer2 = QgsProject.instance().mapLayersByName('Points along lines')[0]
        QgsProject.instance().removeMapLayer(layer2.id()) 
        layer3 = QgsProject.instance().mapLayersByName('Single parts')[0]
        QgsProject.instance().removeMapLayer(layer3.id()) 

        #Eliminar capa None si existe en el CANVAS
        project = QgsProject.instance()
        for layer in project.mapLayers().values():
            if layer.name() == "None":
                project.removeMapLayer(layer.id())

        #Try/Except para resolver el problema de la seleccion de puntos duplicada
        try:
            #Activar capa a editar        
            layer = QgsProject.instance().mapLayersByName("Puntos Cauces")[0]

            #Seleccionar punto de mayor longitud en el cauce
            fieldname='Distance'
            idx=layer.fields().indexFromName(fieldname)
            layer.selectByExpression( fieldname + '=' + str(layer.maximumValue(idx)) )

            self.progressBar.setValue(60)    

            #Conseguir coordenadas del punto seleccionado INLET
            selected = layer.selectedFeatures()
            geo= QgsGeometry.asPoint(selected[0].geometry()) 
            pxy=QgsPointXY(geo)
            inlet = str(pxy.x()) + "," + str(pxy.y())

            #Conseguir coordenadas del punto de salida OUTLET
            point_layer = QgsVectorLayer(self.folder + '/EasyBasin/Capas_SIG/Punto_Salida/punto_salida_corregido.shp', 'Point Layer', 'ogr')
            # Leer tabla de atributos
            features = point_layer.getFeatures()
            # Iterar a traves de los atributos
            for feature in features:
                # Conseguir lageometria del atributo
                geometry = feature.geometry()
                # Extraer coordenadas X e Y
                Xcoordinate = str(geometry.asPoint().x())
                Ycoordinate = str(geometry.asPoint().y())
            outlet = Xcoordinate + "," + Ycoordinate

            #Calcular el recorrido mas rapido desde el punto mas lejano al punto de salida
            params7 = {
                        'INPUT':self.folder + '/EasyBasin/HMS/Red_Drenaje/Red_drenaje_LFP.shp',
                        'STRATEGY':0,
                        'DIRECTION_FIELD':None,
                        'VALUE_FORWARD':'',
                        'VALUE_BACKWARD':'',
                        'VALUE_BOTH':'',
                        'DEFAULT_DIRECTION':2,
                        'SPEED_FIELD':None,
                        'DEFAULT_SPEED':50,
                        'TOLERANCE':0,
                        'START_POINT':inlet,
                        'END_POINT':outlet,
                        'OUTPUT':self.folder + '/EasyBasin/Capas_SIG/Red_Drenaje/LongestFlowPath.shp'}
            processing.run("native:shortestpathpointtopoint", params7)

        except:

            self.progressBar.setValue(60)   
            
            #Activar capa a editar        
            layer = QgsProject.instance().mapLayersByName("Puntos Cauces")[0]

            #Seleccionar punto de mayor longitud en el cauce
            fieldname='Distance'
            idx=layer.fields().indexFromName(fieldname)
            layer.selectByExpression( fieldname + '=' + str(layer.maximumValue(idx)) )
            #Conseguir coordenadas del punto seleccionado INLET
            selected = layer.selectedFeatures()
            geo= QgsGeometry.asPoint(selected[0].geometry()) 
            pxy=QgsPointXY(geo)
            inlet = str(pxy.x()) + "," + str(pxy.y())

            #Seleccionar punto de menor longitud en el cauce
            fieldname='Distance'
            idx=layer.fields().indexFromName(fieldname)
            layer.selectByExpression( fieldname + '=' + str(layer.minimumValue(idx)) )
            #Conseguir coordenadas del punto seleccionado INLET
            selected = layer.selectedFeatures()
            geo= QgsGeometry.asPoint(selected[0].geometry()) 
            pxy=QgsPointXY(geo)
            outlet = str(pxy.x()) + "," + str(pxy.y())

            #Calcular el recorrido mas rapido desde el punto mas lejano al punto de salida
            params7 = {
                        'INPUT':self.folder + '/EasyBasin/HMS/Red_Drenaje/Red_drenaje_LFP.shp',
                        'STRATEGY':0,
                        'DIRECTION_FIELD':None,
                        'VALUE_FORWARD':'',
                        'VALUE_BACKWARD':'',
                        'VALUE_BOTH':'',
                        'DEFAULT_DIRECTION':2,
                        'SPEED_FIELD':None,
                        'DEFAULT_SPEED':50,
                        'TOLERANCE':0,
                        'START_POINT':outlet,
                        'END_POINT':inlet,
                        'OUTPUT':self.folder + '/EasyBasin/Capas_SIG/Red_Drenaje/LongestFlowPath.shp'}
            processing.run("native:shortestpathpointtopoint", params7)

        self.progressBar.setValue(70)

        #Añadir capa vectorial 
        main_stream = QgsVectorLayer(self.folder + '/EasyBasin/Capas_SIG/Red_Drenaje/LongestFlowPath.shp', 'Cauce Principal', "ogr")
        crs = main_stream.crs()
        crs.createFromId(25830) 
        main_stream.setCrs(crs)
        QgsProject.instance().addMapLayer(main_stream)

        #Eliminar capas sobrantes
        layer3 = QgsProject.instance().mapLayersByName('Puntos Cauces')[0]
        QgsProject.instance().removeMapLayer(layer3.id()) 

        self.progressBar.setValue(80)    

        #Activar capa a editar        
        layer = QgsProject.instance().mapLayersByName("Cauce Principal")[0]

        #Actualizar campos de la capa longest flow path    
        caps = layer.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.AddAttributes:
            layer.dataProvider().addAttributes([QgsField("LONGITUD", QVariant.Int)])
        layer.updateFields()

        #Eliminar los campos sobrantes
        layer.startEditing()
        idx1 = layer.fields().indexFromName('cost')
        idx2 = layer.fields().indexFromName('end')
        idx3 = layer.fields().indexFromName('start')
        layer.deleteAttribute(idx1)
        layer.deleteAttribute(idx2)
        layer.deleteAttribute(idx3)
        layer.commitChanges()

        #Activar el editor
        layer.startEditing()
        #Expresiones utilizadas en la calculador de campos
        e3 = QgsExpression('$length')
        #Clases necesarias para utilizar calculadora de campos
        context = QgsExpressionContext()
        scope = QgsExpressionContextScope()
        context.appendScope(scope)
        #Añadir los resultados a la tabla de atributos
        for f in layer.getFeatures():
            context.setFeature(f)
            f['LONGITUD'] = e3.evaluate(context)
            layer.updateFeature(f)
        #Cerrar editor
        layer.commitChanges()

        #Extraer vertices del cauce principal
        params8 = {
                    'INPUT':self.folder + '/EasyBasin/Capas_SIG/Red_Drenaje/LongestFlowPath.shp',
                    'VERTICES':'0,-1',
                    'OUTPUT':'TEMPORARY_OUTPUT'}
        processing.runAndLoadResults("qgis:extractspecificvertices", params8)

        vertex = QgsProject.instance().mapLayersByName("Vertices")[0]
        vertexPath = vertex.source()

        #Copiar valor celda raster (MDT) en vertices del cauce principal
        params9 = {
                    'INPUT':vertexPath,
                    'RASTERCOPY':self.folder + '/EasyBasin/Capas_SIG/MDT/MDT_corregido.tif',
                    'COLUMN_PREFIX':'ALT',
                    'OUTPUT':self.folder + '/EasyBasin/Capas_SIG/Procesos_Internos/LongestFlowPath_Altitud.shp'}
        processing.runAndLoadResults("qgis:rastersampling",params9 )

        vertex = QgsProject.instance().mapLayersByName("Vertices")[0]
        QgsProject.instance().removeMapLayer(vertex.id()) 

        #Mover capa punto a la ultima posicion en el panel de capas
        layer = QgsProject.instance().mapLayersByName("LongestFlowPath_Altitud")[0]
        root = QgsProject.instance().layerTreeRoot()
        point = root.findLayer(layer.id())
        pointClone = point.clone()
        parent = point.parent()
        parent.insertChildNode(-1, pointClone)
        parent.removeChildNode(point)

        #Cambiar color y tamaño capa
        layer = QgsProject.instance().mapLayersByName("Cauce Principal")[0]
        symbol = QgsLineSymbol.createSimple({'width': '0.5', 'color': 'yellow'})
        layer.renderer().setSymbol(symbol)
        layer.triggerRepaint()
        self.iface.layerTreeView().refreshLayerSymbology( layer.id() )

        self.progressBar.setValue(100)

        self.progressBar.setValue(0)
        self.showMinimized()
        self.labelBar.setText("")

        self.results()

        self.pushButtonBasin.setEnabled(False)
        self.pushButtonAvance4.setEnabled(True)
        self.pushButtonResultados.setEnabled(True)

        # #Mensaje informativo
        # QMessageBox.information(None, "Cuenca Hidrográfica", "Proceso Finalizado")
        # self.results() 

    def results(self):

        #Crear la otra ventana
        self.results = Results(self.iface)
        self.results.setWindowFlags(Qt.WindowSystemMenuHint | Qt.MSWindowsFixedSizeDialogHint | Qt.WindowTitleHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        #Llamar a la funcion getter para pasar la ruta de trabajo de una ventana a otra
        self.passInfo()

        # self.results.show()
        self.results.exec_()  

    def passInfo(self):

        #Colocar ruta de trabajo (variable global) en el objeto (label) de la otra ventana
        self.results.folder2.setText(self.folder)

        #Tambien se puede capturar la ruta desde el objeto de la ventana1 y pegarlo en la ventana2
        # self.results.folder2.setText(self.pushButton_labelPath.text())

    def RESET(self): 

        reply = QMessageBox.question(None, 'AVISO', 'Recuerde que al cerrar EasyBasin, la zona de trabajo (canvas) de QGIS se limpiará y todas las capas serán borradas. Sin embargo, todos los archivos generados se mantendrán en la carpeta del proyecto. \n¿Desea continuar con el cierre?', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            #Cerrar plugin
            self.close()

            #Eliminar capas del CANVAS
            QgsProject.instance().removeAllMapLayers()
            self.canvas.refresh()

        else:
            pass

    def info(self):

        text = "<b>EasyBasin</b> es un complemento de QGIS para la delimitación de cuencas hidrográficas y la obtención del caudal máximo anual mediante el método racional descrito en la norma 5.2-IC DRENAJE SUPERFICIAL.<br><br><b>Manual</b>: (en desarrollo) <br><br><b>Referencia</b>: https://doi.org/10.1016/j.ejrh.2022.101308 <br><br>Para cualquier duda o sugerencia contactar con <b>alopez6@ucam.edu</b>. <br><br>Si encuentras útil este plugin, o si te ha ahorrado tiempo en tu trabajo, considera apoyarlo invitándome a un café. Gracias 😊"
        msgINFO = QMessageBox()
        msgINFO.setWindowIcon(QIcon(":/images/icon.png"))
        msgINFO.setWindowTitle("Help & About")
        msgINFO.setText(text)
        msgINFO.setTextFormat(Qt.RichText)
        msgINFO.setStandardButtons(QMessageBox.Ok)
        msgINFO.exec_()

        # QMessageBox.information(None, "Información sobre EasyBasin", "Complemento de QGIS para la delimitación de cuencas hidrográficas y obtención del caudal máximo anual mediante el método racional descrito en la norma 5.2-IC DRENAJE SUPERFICIAL. \n\nAutores: \n\nAdrián López-Ballesteros (alopez6@ucam.edu)\nJavier Senent-Aparicio (jsenent@ucam.edu) \nPatricia Jimeno-Sáez (pjimeno@ucam.edu) \nJulio Pérez-Sánchez (jperez058@ucam.edu)", QMessageBox.Close)

    def Open(self):

        FolderPath = self.pushButton_labelPath.text()
        webbrowser.open(FolderPath)

    def coffee(self):

            self.labelCheck_coffee.setText("😊 GRACIAS!")
            url = "https://www.buymeacoffee.com/alopez6"
            webbrowser.open(url)


