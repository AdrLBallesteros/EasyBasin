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
 ***************************************************************************

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


import os.path
import processing
import csv
import math
import os
import webbrowser
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from EasyBasin_v3.gui.generated.ui_results import Ui_window

# from EasyBasin_v3 import BaseDialog

from qgis.core import QgsProject, QgsVectorLayer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QMessageBox, QMainWindow, QApplication, QFileDialog, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSize

class Results(QDialog, Ui_window):

    def __init__(self, iface):
        QDialog.__init__(self)

        self.setupUi(self)
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))

        # Capturar ruta del proyecto desde otra ventana (BaseDialog)
        self.folder2 = self.pushButton_labelPath2
        self.folder = None

        #Añadir area de la cuenca y perimetro a resultados
        layer = QgsProject.instance().mapLayersByName("Cuenca Hidrográfica")[0]
        value1 = layer.getFeature(0).attribute(1)
        value2 = layer.getFeature(0).attribute(2)
        self.lineEditAreaCuenca.setText(str(round(value1/1000000,2)))
        self.lineEditPerimetroCuenca.setText(str(value2))

        #Añadir altitud maxima y minima del cauce a resultados    
        layer = QgsProject.instance().mapLayersByName("LongestFlowPath_Altitud")[0]
        # field_index = layer.fields().indexFromName('ALT')
        value1 = layer.getFeature(0).attribute(7)
        value2 = layer.getFeature(1).attribute(7)
        self.lineEditAltMax.setText(str(round(value1,2)))
        self.lineEditAltMin.setText(str(round(value2,2)))    

        #Añadir longitud cauce principal a resultados
        layer = QgsProject.instance().mapLayersByName("Cauce Principal")[0]
        value = layer.getFeature(0).attribute(0)
        self.lineEditLongitudCauce.setText(str(value))

        #Añadir REGION a resultados
        layer = QgsProject.instance().mapLayersByName("Cuenca Hidrográfica")[0]
        value = layer.getFeature(0).attribute(5)
        self.lineEditRegion.setText(str(int(value)))

        #Bloqueo boton Calcular Intensidad
        self.pushButton_Intensidad.setEnabled(False)
        #Bloqueo boton Calcular Escorrentia
        self.pushButton_escorrentia.setEnabled(False) 
        #Bloqueo boton Calcular Caudal Maximo
        self.pushButton_QT.setEnabled(False)  
        #Bloqueo boton GENERAR INFORME
        self.pushButton_Informe.setEnabled(False)  
        #Bloqueo boton GENERAR MAPA
        self.pushButton_Mapa.setEnabled(False)
        #Bloqueo boton GENERAR HIETOGRAMA
        self.pushButton_Tormenta.setEnabled(False)
        #Bloqueo boton GENERAR INPUTS HMS
        self.pushButton_HMS.setEnabled(False)
        self.pushButton_HMS_2.setEnabled(False)
        self.pushButton_labelbarHMS.setEnabled(False)
        self.pushButton_labelbarMR.setEnabled(False)

        self.pushButton_PCPmax.setEnabled(False)          
        self.pushButton_setup.setEnabled(False)

        self.lineEditPmax.setEnabled(False)
        self.lineEditPmax_2.setEnabled(False) 
        self.lineEditPmax_3.setEnabled(False)                      

    def tiempo(self): 
        #Obtener ruta de trabajo
        self.folder = str(self.pushButton_labelPath2.text())

        #Añadir pendiente cauce principal a resultados
        AltMax = self.lineEditAltMax.text()
        AltMin = self.lineEditAltMin.text()
        Long = self.lineEditLongitudCauce.text()
        Alt = float(AltMax) - float(AltMin)
        slope = Alt / float(Long)
        value = slope * 100
        self.lineEditPendienteCauce.setText(str(round(value,3)))

        #Añadir tiempo de concentracion (IC-5.2) a resultados
        long2 = float(Long)/1000
        tc = 0.3*(long2**(0.76))*(slope**(-0.19))
        self.lineEditTiempo.setText(str(round(tc,2)))

        self.pushButton_PCPmax.setEnabled(True)          
        self.pushButton_setup.setEnabled(True)

        self.lineEdit_Duracion.setText(str(round(tc*60)))

        if tc > 3:
            self.lineEdit_Intervalo.setText(str(30))
        else:
            self.lineEdit_Intervalo.setText(str(round(tc*60*0.2)))

    def PCPmax(self): 
        #Obtener ruta de trabajo
        self.folder = str(self.pushButton_labelPath2.text())

        #Añadir ventana con mapa pcp georeferenciado               
        #Dimensiones marco exterior
        new_dialog = QDialog(self)
        new_dialog.resize(800, 620)

        #Dimensiones marco interior
        map_canvas = QgsMapCanvas(new_dialog) 
        map_canvas.setMinimumSize(800, 550) 

        vlayer = QgsVectorLayer(self.folder + '/EasyBasin/Capas_SIG/Cuenca_Hidrografica/cuenca_hidrografica_atr.shp',"Cuenca","ogr")
        rlayer = QgsRasterLayer('C:/EasyBasin/Rasters/PCP_Max_Spain.tif',"Mapa")
        QgsProject.instance().addMapLayer(rlayer,False)
        QgsProject.instance().addMapLayer(vlayer,False)
        symbol = QgsFillSymbol.createSimple({'color':'red','color_border':'black','width_border':'1','style':'no'})
        vlayer.renderer().setSymbol(symbol)
        vlayer.triggerRepaint()
        self.iface.layerTreeView().refreshLayerSymbology( vlayer.id() )
        map_canvas.setLayers([vlayer,rlayer])
        map_canvas.setExtent(vlayer.extent())

        label = QLabel(new_dialog)
        label.setText("Líneas color rojo: Coeficiente de variación (Cv) \nLíneas color morado: Valor medio de la máxima precipitación diaria anual (P) \n\nMÁXIMAS LLUVIAS DIARIAS EN LA ESPAÑA PENINSULAR. Dirección General de Carreteras, Ministerio de Fomento (1999).")
        label.adjustSize()
        label.move(10, 555)

        new_dialog.show()

        self.lineEditPmax.setEnabled(True)
        self.lineEditPmax_2.setEnabled(True) 
        self.lineEditPmax_3.setEnabled(True) 

    def setup(self): 
        T = self.comboBoxPeriodo.currentText()
        if T == "---":
            QMessageBox.warning(None, "Aviso", "Seleccionar PERÍODO DE RETORNO.")
            return

        # elif not self.lineEditPmax.isModified():
        #     QMessageBox.warning(None, "Aviso", "Indicar P.")

        # elif not self.lineEditPmax_2.isModified():
        #     QMessageBox.warning(None, "Aviso", "Indicar Cv.")

        elif not self.lineEditPmax.isModified() and not self.lineEditPmax_2.isModified():

            self.lineEditPmax.setEnabled(False)
            self.lineEditPmax_2.setEnabled(False)
            self.lineEditPmax_3.setEnabled(False)     

            input_pcp = 'C:/EasyBasin/Rasters/PCP/' + str(self.comboBoxPeriodo.currentText()) + '.tif'

            #Proceso calcular pcp media de la cuenca - ZONAL_STATISTICS
            params1 ={
                        'INPUT': self.folder + '/EasyBasin/Capas_SIG/Cuenca_Hidrografica/cuenca_hidrografica_atr.shp',
                        'INPUT_RASTER':input_pcp,
                        'RASTER_BAND':1,
                        'COLUMN_PREFIX':'PCP_',
                        'STATISTICS':[2],
                        'OUTPUT': 'TEMPORARY_OUTPUT'}
            processing.runAndLoadResults("native:zonalstatisticsfb", params1)

            #Si la capa existe, la seleccionamos:
            if QgsProject.instance().mapLayersByName('Estadistica zonal'):
                pcp = QgsProject.instance().mapLayersByName("Estadistica zonal")[0]
            else:
                pcp = QgsProject.instance().mapLayersByName("Zonal Statistics")[0]

            #Seleccionar capa temporal por nombre
            # pcp = QgsProject.instance().mapLayersByName("Zonal Statistics")[0]

            #Seleccionar campo tabla por nombre y obtener valor
            features = pcp.getFeatures()
            for feature in features:
                field_name = 'PCP_mean'
                if pcp.fields().indexFromName(field_name) != -1:
                    Pd = feature[field_name]

            self.lineEditPd.setText(str(round(Pd,2)))

            #Eliminar capas sobrantes
            QgsProject.instance().removeMapLayer(pcp.id()) 

        else :
            if not self.lineEditPmax.isModified():
                QMessageBox.warning(None, "Aviso", "Indicar P.")
                return

            elif not self.lineEditPmax_2.isModified():
                QMessageBox.warning(None, "Aviso", "Indicar Cv.")
                return

            #Obtener valores para calculo KT desde tabla CSV       
            CV = self.lineEditPmax_2.text()
            #T = self.comboBoxPeriodo.currentText()
            with open('C:/EasyBasin/Tablas/Tabla_Factores_Kt.csv') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['CV'] == CV:
                        KT = row[T]                    
                        self.lineEditPmax_3.setText(KT)

            KT1 = float(self.lineEditPmax_3.text())
            P1 = float(self.lineEditPmax.text())
            Pd1 = P1*KT1
            self.lineEditPd.setText(str(round(Pd1,2)))

        self.pushButton_Intensidad.setEnabled(True)                                                          

    def intensidad(self):
        #Aviso por si no se ha especificado el valor de Pd
        try:            
            Pd = float(self.lineEditPd.text())
        except:
            QMessageBox.warning(None, "Aviso", "Indicar PRECIPITACIÓN MÁXIMA DIARIA (Pd).")
            return

        #Aviso por si no se ha especificado el periodo de retorno
        T = self.comboBoxPeriodo.currentText()
        if T == "---":
            QMessageBox.warning(None, "Aviso", "Seleccionar PERIODO DE RETORNO.")
            return        

        #Calcular factor KA
        A = float(self.lineEditAreaCuenca.text())
        if A < 1:
            self.lineEdit_KA.setText(str(1))
        else :
            self.lineEdit_KA.setText(str(round(1-(math.log10(A)/15),3)))

        #Calcular intensidad media diaria Id  
        Pd = float(self.lineEditPd.text())
        KA = float(self.lineEdit_KA.text())
        Id = Pd*KA/24
        self.lineEdit_Id.setText(str(round(Id,3)))  

        #Añadir indice torrencialidad I1/Id a resultados
        layer = QgsProject.instance().mapLayersByName("Cuenca Hidrográfica")[0]
        value = layer.getFeature(0).attribute(6)
        self.lineEdit_Torrencialidad.setText(str(int(value)))         

        #Calcular factor de torrencialidad Fa
        I1 = float(self.lineEdit_Torrencialidad.text())
        tc = float(self.lineEditTiempo.text())
        Fa = I1**(3.5287-2.5287*tc**0.1)
        self.lineEdit_Fa.setText(str(round(Fa,3))) 

        #Calcular Intensidad Precipitacion I        
        Id = float(self.lineEdit_Id.text())
        Fa = float(self.lineEdit_Fa.text())
        I = Id*Fa
        self.lineEdit_I.setText(str(round(I,3)))

        #Desactivar Bloqueo boton Calcular Escorrentia
        self.pushButton_escorrentia.setEnabled(True)
        self.pushButton_Tormenta.setEnabled(True)

    def escorrentia(self):  
        #Aviso por si no se ha especificado el raster P0
        P0 = self.comboBoxP0.currentText()
        if P0 == "---":
            QMessageBox.warning(None, "Aviso", "Seleccionar CAPA SIG PARA EL UMBRAL DE ESCORRENTÍA")
            return  
        
        if P0 == "Raster P0 500m (MITECO)":
            #Añadir POi  a resultados
            layer = QgsProject.instance().mapLayersByName("Cuenca Hidrográfica")[0]
            value = layer.getFeature(0).attribute(8)
            self.lineEdit_Poi.setText(str(round(value,3)))

        if P0 == "Raster P0 100m (CLC2000)":
            #Añadir POi  a resultados
            layer = QgsProject.instance().mapLayersByName("Cuenca Hidrográfica")[0]
            value = layer.getFeature(0).attribute(9)
            self.lineEdit_Poi.setText(str(round(value,3))) 

        if P0 == "Raster P0 100m (CLC2018)":
            #Añadir POi  a resultados
            layer = QgsProject.instance().mapLayersByName("Cuenca Hidrográfica")[0]
            value = layer.getFeature(0).attribute(10)
            self.lineEdit_Poi.setText(str(round(value,3))) 

        #Obtener valores para calculo coeficiente corrector b desde tabla CSV       
        reg = self.lineEditRegion.text()
        T = self.comboBoxPeriodo.currentText()
        with open('C:/EasyBasin/Tablas/Tabla_Corrector_Umbral.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Region'] == reg:
                    Bm = row['Bm']                                                            
                    D50 = row['D50']
                    FT = row[T]                    
                    self.lineEdit_Bm.setText(Bm)
                    self.lineEdit_D50.setText(D50)
                    self.lineEdit_FT.setText(FT)

        #Calcular coeficiente corrector umbral en funcion del tipo de obra b
        obra = self.comboBoxObra.currentText()
        vBm = float(self.lineEdit_Bm.text())
        vD50 = float(self.lineEdit_D50.text())

        #Calculo Q10 Levante y Sureste - Regiones 72/821/822
        try:
            vFT = float(self.lineEdit_FT.text())
            self.lineEdit_Y.setText("---")
            self.lineEdit_X.setText("---")
        except:
            self.lineEdit_FT.setText("1")
            vFT = float(self.lineEdit_FT.text())
            # QMessageBox.information(None, "ATENCIÓN", "Cuenca del Levante o Sureste Peninsular (Regiones 72/821/822) con T>25 años.\nCálculo QT= Ψ*Q10^λ")
            reply = QMessageBox.question(None, "ATENCIÓN", "Cuenca del Levante o Sureste Peninsular (Regiones 72/821/822) con T>25 años. Cálculo QT= Ψ*Q10^λ\n¿Quieres continuar con este método de cálculo para las cuencas pequeñas del Levante y Sureste peninsular?", QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                #Seleccion parametro Y e X TABLA 2.6. PARÁMETROS PARA EL CÁLCULO EN CUENCAS PEQUEÑAS DEL LEVANTE Y SURESTE PENINSULAR (T > 25 años)
                reg = self.lineEditRegion.text()
                T = self.comboBoxPeriodo.currentText()
                if reg ==  '72': 
                    with open('C:/EasyBasin/Tablas/Reg72.csv') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            if row['Parametro'] == 'y':
                                Y = row[T]                    
                                self.lineEdit_Y.setText(Y)
                            elif row['Parametro'] == 'x':
                                X = row[T]                    
                                self.lineEdit_X.setText(X)                                                    
                else:
                    with open('C:/EasyBasin/Tablas/Reg821-822.csv') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            if row['Parametro'] == 'y':
                                Y = row[T]                    
                                self.lineEdit_Y.setText(Y)
                            elif row['Parametro'] == 'x':
                                X = row[T]                    
                                self.lineEdit_X.setText(X)
                #Calcular Q10 para caudal en zonas del levante                 
                self.comboBoxPeriodo.setCurrentIndex(3)
                self.setup()
                self.intensidad()
            else:
                self.lineEdit_Y.setText("---")
                self.lineEdit_X.setText("---")                            

        #Calcular coeficiente corrector umbral en funcion del tipo de obra b       
        if obra == 'De la carretera (puentes y ODTs)':
            bDT = (vBm-vD50)*vFT
            self.lineEdit_b.setText(str(round(bDT,3)))
        elif obra == 'De vías de servicio, ramales, caminos, accesos y drenaje de plataforma y márgenes':
            bPM = vBm*vFT
            self.lineEdit_b.setText(str(round(bPM,3)))
        else:
            QMessageBox.warning(None, "AVISO", "Seleccionar OBRAS DE DRENAJE TRANSVERSAL.")
            return 

        #Calcular umbral de escorrentia corregido Po
        Poi = float(self.lineEdit_Poi.text())
        b = float(self.lineEdit_b.text())
        Po = Poi*b
        self.lineEdit_Po.setText(str(round(Po,3)))

        #Calcular el coeficiente de escorrentia C
        Pd = float(self.lineEditPd.text())
        KA = float(self.lineEdit_KA.text())
        Po = float(self.lineEdit_Po.text())        
        if Pd*KA > Po:
            C = ((Pd*KA - Po)*(Pd*KA + 23*Po))/((Pd*KA+11*Po)**2)
            self.lineEdit_C.setText(str(round(C,3))) 
        else:
            C = 0
            self.lineEdit_C.setText(str(round(C,3)))             

        #Calcular coeficiente de uniformidad distribucion temporal Kt                
        tc = float(self.lineEditTiempo.text())
        Kt = 1 + (tc**1.25)/((tc**1.25)+14)
        self.lineEdit_Kt.setText(str(round(Kt,3)))

        #Desactivar Bloqueo boton Calcular Caudal Maximo
        self.pushButton_QT.setEnabled(True)  
        self.pushButton_HMS.setEnabled(True)

    def caudal(self):
        #Mensaje informativo
        A = float(self.lineEditAreaCuenca.text())
        if A > 50:
            QMessageBox.warning(None, "AVISO", "Cuenca hidrográfica superior a 50 km2.\nMétodo Racional no recomendable según Norma 5.2-IC.\nSe recomienda utilizar otro método hidrológico para el calculo del caudal máximo.")                

        #Calcular caudal maximo anual QT
        Y = self.lineEdit_Y.text()       
        if Y == '---':
            I = float(self.lineEdit_I.text())
            C = float(self.lineEdit_C.text())
            A = float(self.lineEditAreaCuenca.text())      
            Kt = float(self.lineEdit_Kt.text())
            QT = (I*C*A*Kt)/3.6
            self.lineEdit_QT.setText(str(round(QT,3)))   
        else:            
            I = float(self.lineEdit_I.text())
            C = float(self.lineEdit_C.text())
            A = float(self.lineEditAreaCuenca.text())      
            Kt = float(self.lineEdit_Kt.text())  
            Ymod = float(self.lineEdit_Y.text())  
            Xmod = float(self.lineEdit_X.text())
            QT = (I*C*A*Kt)/3.6
            QTmod = Ymod*(QT**Xmod)
            self.lineEdit_QT.setText(str(round(QTmod,3)))

        #Bloqueo boton GENERAR INFORME
        self.pushButton_Informe.setEnabled(True)  
        #Bloqueo boton GENERAR MAPA
        self.pushButton_Mapa.setEnabled(True) 

    def informe(self):
        self.folder = str(self.pushButton_labelPath2.text()) 

        A = self.lineEditAreaCuenca.text()
        PER = self.lineEditPerimetroCuenca.text()
        Hmax = self.lineEditAltMax.text()
        Hmin = self.lineEditAltMin.text()
        Lc = self.lineEditLongitudCauce.text()
        Jc = self.lineEditPendienteCauce.text()
        tc = self.lineEditTiempo.text()
        T = self.comboBoxPeriodo.currentText()
        Pd = self.lineEditPd.text()
        KA = self.lineEdit_KA.text()
        Id = self.lineEdit_Id.text()
        I1 = self.lineEdit_Torrencialidad.text()
        Fa = self.lineEdit_Fa.text()
        I = self.lineEdit_I.text()       
        REGION = self.lineEditRegion.text()
        Obra = self.comboBoxObra.currentText()
        Bm = self.lineEdit_Bm.text() 
        D50 = self.lineEdit_D50.text() 
        FT = self.lineEdit_FT.text() 
        b = self.lineEdit_b.text() 
        Poi = self.lineEdit_Poi.text() 
        Po = self.lineEdit_Po.text() 
        C = self.lineEdit_C.text() 
        Kt = self.lineEdit_Kt.text()
        Y = self.lineEdit_Y.text()
        X = self.lineEdit_X.text()
        QT = self.lineEdit_QT.text()

        informe_path = self.folder + '/EasyBasin/Informes'
        informe_MR = informe_path + '/Informe_METODO_RACIONAL_Easybasin.txt'
        #Generar archivo txt con resultados
        with open(informe_MR, "w") as file:
            file.write("------------------------------------INFORME DE RESULTADOS MÉTODO RACIONAL NORMA 5.2-IC DE EASYBASIN------------------------------------ \n \n")            
            file.write("CARACTERÍSTICAS DE LA CUENCA HIDROGRÁFICA:  \n----------------------------- \n\n")
            file.write("-Área: " + A + " km2 \n")
            file.write("-Perímetro: " + PER + " m \n")
            file.write("-Altitud Máxima del cauce: " + Hmax + " msnm \n")
            file.write("-Altitud Mínima del cauce: " + Hmin + " msnm \n")
            file.write("-Longitud del cauce (Lc): " + Lc + " m \n")
            file.write("-Pendiente media del cauce (Jc): " + Jc + " % \n")
            file.write("-Tiempo de concentración (tc): " + tc + " horas \n")
            file.write("------------------------------------------------------------------------------------------------------- \n \n") 
            file.write("INTENSIDAD DE PRECIPITACIÓN:  \n---------------------------- \n\n")
            file.write("-Período de retorno: " + T + " años \n")
            file.write("-Precipitación diaria correspondiente a " + T + " (Pd): " + Pd + " mm \n")
            file.write("-Factor reductor de la precipitación por área de la cuenca (KA): " + KA + "\n")
            file.write("-Intensidad media diaria de precipitación corregida correspondiente a " + T + " (Id): " + Id + " mm/h \n")
            file.write("-Índice de torrencialidad (I1/Id): " + I1 + "\n")
            file.write("-Factor obtenido del índice de torrencialidad (Fa): " + Fa + "\n")
            file.write("-Intensidad de precipitación (I): " + I + " mm/h \n")
            file.write("------------------------------------------------------------------------------------------------------- \n \n")
            file.write("COEFICIENTE DE ESCORRENTÍA:  \n--------------------------- \n\n")
            file.write("-Región: " + REGION + "\n")
            file.write("-Obra de drenaje transversal: " + Obra + "\n")
            file.write("-Coeficiente corrector del umbral de escorrentía (b): " + b + "\n")
            file.write("      -Valor medio en la región del coeficiente corrector del umbral de escorrentía (Bm): " + Bm + "\n")
            file.write("      -Desviación respecto al valor medio para el intervalo de confianza del 50% (D50): " + D50 + "\n")
            file.write("      -Factor función del período de retorno (FT): " + FT + "\n")
            file.write("-Umbral de escorrentía inicial (Poi): " + Poi + " mm \n")
            file.write("-Umbral de escorrentía (Po): " + Po + " mm \n")
            file.write("-Coeficiente de escorrentía (C): " + C + "\n")            
            file.write("------------------------------------------------------------------------------------------------------- \n \n") 
            file.write("CAUDAL MÁXIMO ANUAL:  \n-------------------- \n\n")
            file.write("-Coeficiente de uniformidad en la distribución temporal de la precipitación (Kt): " + Kt + "\n")
            file.write("-Ψ: " + Y + "\n")
            file.write("-λ: " + X + "\n")            
            file.write("-Caudal máximo anual correspondiente a " + T + " (QT): " + QT + " m3/s \n")            
            file.write("------------------------------------------------------------------------------------------------------- \n \n")  

        reply2 = QMessageBox.question(None, "ATENCIÓN", "¿Te gustaría generar también un informe de datos de entrada de la cuenca completa para el modelo hidrológico HEC-HMS?", QMessageBox.Yes, QMessageBox.No)
        if reply2 == QMessageBox.Yes:
            lagTime = str(round(float(tc)*60*0.6,2))
            CN = str(round(25400/((float(Poi)/0.2)+254),2))
            Mus_K = str(round(0.18*((float(Lc)/1000)*(float(Jc)/100)**-0.25)**0.76,2))

            #Obtener area impermeable 
            basin = QgsProject.instance().mapLayersByName("Cuenca Hidrográfica")[0]
            for feature in basin.getFeatures():
                area_impermeable = feature.attribute("Area_Imp_s")
            imp = str(round(float(area_impermeable)/(float(A)*1000000)*100,2))

            informe_HMS = informe_path + '/Informe_INPUTS_HMS_Easybasin.txt'
            with open(informe_HMS, "w") as file2:
                file2.write("------------------------------------INFORME DE DATOS DE ENTRADA PARA HEC-HMS GENERADO POR EASYBASIN------------------------------------ \n \n")  
                file2.write("CUENCA HIDROGRÁFICA COMPLETA:  \n----------------------------- \n\n") 
                file2.write("-Área: " + A + " km2 \n")  
                file2.write("-Longitud del cauce (Lc): " + Lc + " m \n")
                file2.write("-Altitud Máxima del cauce: " + Hmax + " msnm \n")
                file2.write("-Altitud Mínima del cauce: " + Hmin + " msnm \n")
                file2.write("-Pendiente media del cauce (Jc): " + Jc + " % \n")
                file2.write("-Tiempo de concentración (tc): " + tc + " horas \n")
                file2.write("-Lag time (Lag): " + lagTime + " min \n")
                file2.write("-Abstracción inicial o umbral de escorrentía inicial (Poi): " + Poi + " mm \n")
                file2.write("-Número de curva (CN): " + CN + "\n")
                file2.write("-Área impermeable (Impervious): " + imp + " % \n")
                file2.write("-Muskingum K (K): " + Mus_K + " horas \n")
                file2.write("-Muskingum X (X): 0(Caudaloso, poca pendiente) - 0.5(Poco caudaloso, gran pendiente) \n")
                file2.write("------------------------------------------------------------------------------------------------------- \n \n") 
            os.startfile(informe_HMS)
        else:
            pass
        os.startfile(informe_MR)

    def mapa(self): 
        self.folder = str(self.pushButton_labelPath2.text()) 
        informe_path = self.folder + '/EasyBasin/Informes'
        map_file = informe_path + '/Mapa_EasyBasin.png'

        #Acceder al proyecto QGIS actual
        project = QgsProject.instance()
        #Crear layout 
        layout_manager = project.layoutManager()
        layout_name = "Mapa EasyBasin"
        #Comprobar si existe el layout y eliminar en su caso
        layouts_list = layout_manager.printLayouts()
        for layout in layouts_list:
            if layout.name() == layout_name:
                layout_manager.removeLayout(layout)
        #Crear un layout nuevo
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        layout.setName(layout_name)
        layout_manager.addLayout(layout)

        #Hacer referencia al canvas para definir extension
        canvas = self.iface.mapCanvas()

        #Generar frame del layout
        map = QgsLayoutItemMap(layout)
        map.setRect(0, 0, 297, 170)
        map.setFrameEnabled(True)
        #Definir extension               
        map.setExtent(canvas.extent())       
        crs = QgsCoordinateReferenceSystem('EPSG:25830')
        map.setCrs(crs) 
        layout.addLayoutItem(map)
        layout.refresh()

        #Añadir titulo al layout
        title = QgsLayoutItemLabel(layout)
        title.setText("Cuenca hidrográfica generada por el plugin de QGIS 'EasyBasin'")
        font = QFont("Arial", 12)
        font.setBold(True)  # Make the font bold
        title.setFont(font)
        layout.addLayoutItem(title)
        title.attemptMove(QgsLayoutPoint(80, 205, QgsUnitTypes.LayoutMillimeters))

        #Exportar mapa como imagen
        exporter = QgsLayoutExporter(layout)
        export_settings = QgsLayoutExporter.ImageExportSettings()
        export_settings.dpi = 300  
        exporter.exportToImage(map_file, export_settings)
        os.startfile(map_file)

    def BloquesAlternos(self):
        #Tiempo de duracion de la tormenta (min)
        tor = float(self.lineEdit_Duracion.text())
        #Intervalo de tiempo a dividir la tormenta (min)
        inter = float(self.lineEdit_Intervalo.text())

        #Calcular Intensidad Precipitacion I(mm/h)
        I1 = float(self.lineEdit_Torrencialidad.text())  #Indice torrencialidad
        Id = float(self.lineEdit_Id.text())  #Intensidad media diaria

        #Calcular numero de Intervalos
        Num_int = round(tor/inter)  
        Int_central =round(Num_int/2 + 0.0001)

        #Reajuste para evitar errores por redondeo
        reajuste = tor/Num_int
        inter = reajuste

        self.lineEdit_Intervalo.setText(str(int(reajuste)))

        eje = []
        pcp = []
        #Obtener PCP a partir de la intensidad
        for i in range(1,Num_int+1):
            t = inter/60 * i 
            Fa = I1**(3.5287-2.5287*t**0.1)
            I = Id*Fa 
            P = I * t
            pcp.append(P)
            eje.append(round(inter*i))

        #Obtener incremento de la PCP
        pcp2 = [] 
        for i, value in enumerate(pcp):
            if i == 0:
                pcp2.append(value)
            if i > 0:
                value = pcp[i] -pcp[i-1]
                pcp2.append(value)

        #Generar lista de numeros +-
        numbers = [0]
        for i in range(1,Num_int+1):
            numbers.append(i)
            numbers.append(-i)

        #Reajustar tamaño de la lista de numeros
        zipped_list = list(zip(pcp2,numbers))

        #Crear una copia de los datos para autorellenar
        pcp3 = pcp2.copy()
        Int_central = Int_central - 1
        #Poner formato de bloques alternos (funcion principal)
        for i, n in enumerate(zipped_list):
            for a, value in enumerate(pcp2):
                if a == Int_central + n[1]:
                    pcp3[a] = pcp2[i]

        T = self.comboBoxPeriodo.currentText()

        #Generar archivo txt con hietograma
        pcp4 = [round(value, 2) for value in pcp3]
        data = list(zip(eje,pcp4))
        output_txt = self.folder + f'/EasyBasin/Hietogramas/hietograma_{T}.txt'
        with open(output_txt, 'w') as file:
            file.write(f'Hietograma de diseño generado por el plugin de QGIS *EasyBasin* para {T}.\n\n')
            file.write("Duración de la precipitación: " + str(int(tor)) + ' minutos\n')
            file.write("Intervalo de tiempo: " + str(int(inter)) + ' minutos\n\n')
            file.write("Tiempo\tPrecipitación\n")
            file.write(" (min)\t    (mm)\n")
            file.write("------\t-------------\n")
            for row in data:
                file.write(f"{row[0]}\t{row[1]}\n")
        os.startfile(output_txt)

        #Generar grafico del hietograma
        plt.clf()
        plt.bar(eje, pcp3, width=inter, color='blue', edgecolor='black', linewidth=1)
        plt.xlabel('Tiempo (min)')
        plt.ylabel('Precipitación (mm)')
        plt.title(f'Hietograma de Diseño {T} - EasyBasin', fontweight='bold', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        #Guardar grafico
        plt.savefig(self.folder + f'/EasyBasin/Hietogramas/hietograma_{T}')
        os.startfile(self.folder + f'/EasyBasin/Hietogramas/hietograma_{T}.png')

    def hms(self):
        self.folder = str(self.pushButton_labelPath2.text())
        #Dividir la subcuencas en shapefiles individuales
        params ={
                    'INPUT': self.folder + '/EasyBasin/HMS/Subcuencas/subcuencas_atr.shp',
                    'FIELD':'cat',
                    'PREFIX_FIELD':False,
                    'FILE_TYPE':1,
                    'OUTPUT':self.folder + '/EasyBasin/HMS/Subcuencas/Separadas'}
        processing.run("native:splitvectorlayer", params)

        #Pasar subcuencas a polilinea
        params01 = {
                    'INPUT': self.folder + '/EasyBasin/HMS/Subcuencas/subcuencas_atr.shp',
                    'OUTPUT':'TEMPORARY_OUTPUT'}
        processing.runAndLoadResults("native:polygonstolines", params01)

        #Si la capa existe, la seleccionamos:
        if QgsProject.instance().mapLayersByName('Líneas'):
            subbasin_border = QgsProject.instance().mapLayersByName('Líneas')[0]
        else:
            subbasin_border = QgsProject.instance().mapLayersByName('Lines')[0]

        #Seleccionar capa temporal y conseguir ruta
        # subbasin_border = QgsProject.instance().mapLayersByName('Lines')[0]
        subbasin_border_path = subbasin_border.source()

        #Interseccion entre cuenca y cauce
        params02 = {
                    'INPUT': self.folder + '/EasyBasin/HMS/Red_Drenaje/Red_drenaje_LFP.shp',
                    'INTERSECT': subbasin_border_path,
                    'INPUT_FIELDS':['cat'],
                    'INTERSECT_FIELDS':['AREA'],
                    'INTERSECT_FIELDS_PREFIX':'',
                    'OUTPUT':'TEMPORARY_OUTPUT'}
        processing.runAndLoadResults("native:lineintersections", params02)

        #Si la capa existe, la seleccionamos:
        if QgsProject.instance().mapLayersByName('Intersecciones'):
            intersect = QgsProject.instance().mapLayersByName("Intersecciones")[0]
        else:
            intersect = QgsProject.instance().mapLayersByName("Intersections")[0]

        # intersect = QgsProject.instance().mapLayersByName("Intersections")[0]
        intersectPath = intersect.source()

        #Extraer vertices del cauce LFP
        params3 = {
                    'INPUT': self.folder + '/EasyBasin/HMS/Red_Drenaje/Red_drenaje_LFP.shp',
                    'VERTICES':'0,-1',
                    'OUTPUT':'TEMPORARY_OUTPUT'}
        processing.runAndLoadResults("qgis:extractspecificvertices", params3)

        #Si la capa existe, la seleccionamos:
        if QgsProject.instance().mapLayersByName('Vértices'):
            vertex = QgsProject.instance().mapLayersByName("Vértices")[0]
        else:
            vertex = QgsProject.instance().mapLayersByName("Vertices")[0]

        # vertex = QgsProject.instance().mapLayersByName("Vertices")[0]
        vertexPath = vertex.source()
        vertex.setName('Vertices Cauce')

        # layer1 = QgsProject.instance().mapLayersByName('Lines')[0]
        QgsProject.instance().removeMapLayer(subbasin_border.id()) 

        #Iterar a traves de todos los archivos shapefiles de la carpeta
        folder_path = self.folder + '/EasyBasin/HMS/Subcuencas/Separadas'
        files = os.listdir(folder_path)

        #Definir lista para añadir resultados de HMS
        HMS_data = []
        HMS_data2 = []
        HMS_data3 = []
        HMS_data4 = []

        for file_name in files:
            if file_name.lower().endswith('.shp'):
                subbasin_path = os.path.join(folder_path, file_name)

                basin_name = os.path.splitext(file_name)[0]
                #Añadir capa vectorial cauce principal
                main_subbasin = QgsVectorLayer(subbasin_path, str(basin_name), "ogr")
                crs = main_subbasin.crs()
                crs.createFromId(25830) 
                main_subbasin.setCrs(crs)
                QgsProject.instance().addMapLayer(main_subbasin)

                #Recortar cauce mas largo con subcuencas
                params2 ={
                            'INPUT': self.folder + '/EasyBasin/HMS/Red_Drenaje/Red_drenaje_LFP.shp',
                            'OVERLAY': subbasin_path,
                            'OUTPUT': 'TEMPORARY_OUTPUT'}
                processing.runAndLoadResults("native:clip", params2)

                #Si la capa existe, la seleccionamos:
                if QgsProject.instance().mapLayersByName('Cortado'):
                    subbasin_stream = QgsProject.instance().mapLayersByName('Cortado')[0]
                else:
                    subbasin_stream = QgsProject.instance().mapLayersByName('Clipped')[0]

                #Seleccionar capa temporal y conseguir ruta
                # subbasin_stream = QgsProject.instance().mapLayersByName('Clipped')[0]
                subbasin_stream_path = subbasin_stream.source()

                #Extraer puntos de interseccion de cauce - cuenca
                inlet_folder = self.folder + '/EasyBasin/HMS/Subcuencas/Separadas/inlets'
                inlet_path = os.path.join(inlet_folder, file_name)
                params4 = {'INPUT': vertexPath,
                            'PREDICATE':[0],
                            'INTERSECT':subbasin_path,
                            'OUTPUT': inlet_path}
                processing.run("native:extractbylocation", params4)

                #Extraer puntos del cauce dentro de cuenca
                outlet_folder = self.folder + '/EasyBasin/HMS/Subcuencas/Separadas/outlets'
                outlet_path = os.path.join(outlet_folder, file_name)
                params5 = {'INPUT': intersectPath,
                            'PREDICATE':[0,4],
                            'INTERSECT': subbasin_path,
                            'OUTPUT': outlet_path}
                processing.run("native:extractbylocation", params5)

                #Crear shapefile con distancia entre puntos extremos y oulet  ####Comprobar si puedo elegir la selectionada o si no extraer y guardar en un nuevo archivo
                params5 = {
                            'INPUT': outlet_path,
                            'INPUT_FIELD':'cat',
                            'TARGET': inlet_path,
                            'TARGET_FIELD':'cat',
                            'MATRIX_TYPE':0,
                            'NEAREST_POINTS':0,
                            'OUTPUT':'TEMPORARY_OUTPUT'}
                processing.runAndLoadResults("qgis:distancematrix",params5)

                #Si la capa existe, la seleccionamos:
                if QgsProject.instance().mapLayersByName('Matriz de distancia'):
                    streamsD = QgsProject.instance().mapLayersByName('Matriz de distancia')[0]
                else:
                    streamsD = QgsProject.instance().mapLayersByName("Distance matrix")[0]

                # streamsD = QgsProject.instance().mapLayersByName("Distance matrix")[0]
                streamsDPath = streamsD.source()

                #Corregir shape de matriz de distancia a formato point        
                params6 = {
                            'INPUT':streamsDPath,
                            'OUTPUT':'TEMPORARY_OUTPUT'}
                processing.runAndLoadResults("native:multiparttosingleparts", params6)

                #Si la capa existe, la seleccionamos:
                if QgsProject.instance().mapLayersByName('Monoparte'):
                    streamsDcorr = QgsProject.instance().mapLayersByName("Monoparte")[0]
                else:
                    streamsDcorr = QgsProject.instance().mapLayersByName("Single parts")[0]

                # streamsDcorr = QgsProject.instance().mapLayersByName("Single parts")[0]
                streamsDcorrPath = streamsDcorr.source()

                #Eliminar punto duplicados        
                params7 = {
                            'INPUT':streamsDcorrPath,
                            'OUTPUT':'TEMPORARY_OUTPUT'}
                processing.runAndLoadResults("native:deleteduplicategeometries", params7)

                #Si la capa existe, la seleccionamos:
                if QgsProject.instance().mapLayersByName('Limpiada'):
                    streamsDcorr1 = QgsProject.instance().mapLayersByName("Limpiada")[0]
                else:
                    streamsDcorr1 = QgsProject.instance().mapLayersByName("Cleaned")[0]

                # streamsDcorr1 = QgsProject.instance().mapLayersByName("Cleaned")[0]
                streamsDcorr1.setName('Puntos Cauces')

                try: 
                    #Activar capa a editar        
                    layer = QgsProject.instance().mapLayersByName("Puntos Cauces")[0]

                    #Seleccionar punto de mayor longitud en el cauce
                    fieldname='Distance'
                    idx=layer.fields().indexFromName(fieldname)
                    layer.selectByExpression( fieldname + '=' + str(layer.maximumValue(idx)) )

                    try:
                        #Conseguir coordenadas del punto seleccionado INLET
                        selected = layer.selectedFeatures()
                        geo= QgsGeometry.asPoint(selected[0].geometry()) 
                        pxy=QgsPointXY(geo)
                        inlet = str(pxy.x()) + "," + str(pxy.y())
                    except:
                        #Conseguir coordenadas del punto seleccionado INLET
                        selected = layer.selectedFeatures()
                        geo= QgsGeometry.asPoint(selected[1].geometry()) 
                        pxy=QgsPointXY(geo)
                        inlet = str(pxy.x()) + "," + str(pxy.y())

                    #Conseguir coordenadas del punto de salida OUTLET
                    point_layer = QgsVectorLayer(outlet_path, 'Point Layer', 'ogr')
                    # Leer tabla de atributos
                    features = point_layer.getFeatures()
                    # Iterar a traves de los atributos
                    for feature in features:
                        # Conseguir la geometria del atributo
                        geometry = feature.geometry()
                        # Extraer coordenadas X e Y
                        Xcoordinate = str(geometry.asPoint().x())
                        Ycoordinate = str(geometry.asPoint().y())
                    outlet = Xcoordinate + "," + Ycoordinate

                    #Calcular el recorrido mas rapido desde el punto mas lejano al punto de salida
                    lfpSub_folder = self.folder + '/EasyBasin/HMS/Red_Drenaje/LFP_Subcuencas'
                    lfpSub_path = os.path.join(lfpSub_folder, file_name)
                    params8 = {
                                'INPUT':subbasin_stream_path,
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
                                'OUTPUT':lfpSub_path}
                    processing.run("native:shortestpathpointtopoint", params8)

                except: 
                    #Activar capa a editar        
                    layer = QgsProject.instance().mapLayersByName("Puntos Cauces")[0]

                    #Seleccionar punto de mayor longitud en el cauce
                    fieldname='Distance'
                    idx=layer.fields().indexFromName(fieldname)
                    layer.selectByExpression( fieldname + '=' + str(layer.maximumValue(idx)) )

                    try:
                        #Conseguir coordenadas del punto seleccionado INLET
                        selected = layer.selectedFeatures()
                        geo= QgsGeometry.asPoint(selected[0].geometry()) 
                        pxy=QgsPointXY(geo)
                        inlet = str(pxy.x()) + "," + str(pxy.y())
                    except:
                        #Conseguir coordenadas del punto seleccionado INLET
                        selected = layer.selectedFeatures()
                        geo= QgsGeometry.asPoint(selected[1].geometry()) 
                        pxy=QgsPointXY(geo)
                        inlet = str(pxy.x()) + "," + str(pxy.y())

                    #Conseguir coordenadas del punto de salida OUTLET
                    point_layer = QgsVectorLayer(outlet_path, 'Point Layer', 'ogr')
                    # Leer tabla de atributos
                    features = point_layer.getFeatures()

                    # #Saltar la primera iteracion
                    # next(features, None)
                    # Iterar a traves de los atributos
                    for feature in features:
                        # Conseguir la geometria del atributo
                        geometry = feature.geometry()
                        # Extraer coordenadas X e Y
                        Xcoordinate = str(geometry.asPoint().x())
                        Ycoordinate = str(geometry.asPoint().y())
                        break
                    outlet = Xcoordinate + "," + Ycoordinate

                    #Calcular el recorrido mas rapido desde el punto mas lejano al punto de salida
                    lfpSub_folder = self.folder + '/EasyBasin/HMS/Red_Drenaje/LFP_Subcuencas'
                    lfpSub_path = os.path.join(lfpSub_folder, file_name)
                    params8 = {
                                'INPUT':subbasin_stream_path,
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
                                'OUTPUT':lfpSub_path}
                    processing.run("native:shortestpathpointtopoint", params8)

                # layer1 = QgsProject.instance().mapLayersByName('Clipped')[0]
                QgsProject.instance().removeMapLayer(subbasin_stream.id()) 
                # layer2 = QgsProject.instance().mapLayersByName('Distance matrix')[0]
                QgsProject.instance().removeMapLayer(streamsD.id()) 
                # layer3 = QgsProject.instance().mapLayersByName('Single parts')[0]
                QgsProject.instance().removeMapLayer(streamsDcorr.id()) 
                layer4 = QgsProject.instance().mapLayersByName('Puntos Cauces')[0]
                QgsProject.instance().removeMapLayer(layer4.id()) 

                stream_name = os.path.splitext(file_name)[0] + '_stream'
                #Añadir capa vectorial cauce principal
                main_stream = QgsVectorLayer(lfpSub_path, str(stream_name), "ogr")
                crs = main_stream.crs()
                crs.createFromId(25830) 
                main_stream.setCrs(crs)
                QgsProject.instance().addMapLayer(main_stream)

                #Activar capa a editar        
                layer = QgsProject.instance().mapLayersByName(str(stream_name))[0]
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
                            'INPUT':lfpSub_path,
                            'VERTICES':'0,-1',
                            'OUTPUT':'TEMPORARY_OUTPUT'}
                processing.runAndLoadResults("qgis:extractspecificvertices", params8)

                #Si la capa existe, la seleccionamos:
                if QgsProject.instance().mapLayersByName('Vértices'):
                    vertex = QgsProject.instance().mapLayersByName("Vértices")[0]
                else:
                    vertex = QgsProject.instance().mapLayersByName("Vertices")[0]

                # vertex = QgsProject.instance().mapLayersByName("Vertices")[0]
                vertexPath2 = vertex.source()

                elevation_folder = self.folder + '/EasyBasin/HMS/Red_Drenaje/ALT_Subcuencas'
                elevation_path = os.path.join(elevation_folder, file_name)

                #Copiar valor celda raster (MDT) en vertices del cauce principal
                params9 = {
                            'INPUT':vertexPath2,
                            'RASTERCOPY':self.folder + '/EasyBasin/Capas_SIG/MDT/MDT_corregido.tif',
                            'COLUMN_PREFIX':'ALT',
                            'OUTPUT':elevation_path}
                processing.run("qgis:rastersampling",params9 )

                # vertex = QgsProject.instance().mapLayersByName("Vertices")[0]
                QgsProject.instance().removeMapLayer(vertex.id()) 

                points_name = os.path.splitext(file_name)[0]+'_points'
                #Añadir capa vectorial cauce principal
                main_elevation = QgsVectorLayer(elevation_path, str(points_name), "ogr")
                crs = main_elevation.crs()
                crs.createFromId(25830) 
                main_elevation.setCrs(crs)
                QgsProject.instance().addMapLayer(main_elevation)

                #Extraer longitud cauces de la red de drenaje
                #Disolver todos los atributos en una unica red de drenaje
                params10 = {
                            'INPUT':self.folder + '/EasyBasin/Capas_SIG/Red_Drenaje/Red_drenaje_cuenca.shp',
                            'FIELD':[],
                            'SEPARATE_DISJOINT':False,
                            'OUTPUT':'TEMPORARY_OUTPUT'}
                processing.runAndLoadResults("native:dissolve", params10)

                #Si la capa existe, la seleccionamos:
                if QgsProject.instance().mapLayersByName('Disuelto'):
                    dissolve = QgsProject.instance().mapLayersByName("Disuelto")[0]
                else:
                    dissolve = QgsProject.instance().mapLayersByName("Dissolved")[0]

                # dissolve = QgsProject.instance().mapLayersByName("Dissolved")[0]
                dissolvePath = dissolve.source()

                #Recortar red de drenaje por subcuenca
                params11 = {'INPUT':dissolvePath,
                            'OVERLAY':subbasin_path,
                            'OUTPUT':'TEMPORARY_OUTPUT'}
                processing.runAndLoadResults("native:clip", params11)

                #Si la capa existe, la seleccionamos:
                if QgsProject.instance().mapLayersByName('Cortado'):
                    clip = QgsProject.instance().mapLayersByName("Cortado")[0]
                else:
                    clip = QgsProject.instance().mapLayersByName("Clipped")[0]

                # clip = QgsProject.instance().mapLayersByName("Clipped")[0]
                clipPath = clip.source()

                #Actualizar valores del campo "LONGITUD"
                clip.startEditing()
                #Expresiones utilizadas en la calculador de campos
                e3 = QgsExpression('$length')
                #Clases necesarias para utilizar calculadora de campos
                context = QgsExpressionContext()
                scope = QgsExpressionContextScope()
                context.appendScope(scope)
                #Añadir los resultados a la tabla de atributos
                for f in clip.getFeatures():
                    context.setFeature(f)
                    f['LONGITUD'] = e3.evaluate(context)
                    clip.updateFeature(f)
                #Cerrar editor
                clip.commitChanges()

                #Unir longitud red de drenaje a subcuenca
                params12 = {'INPUT':subbasin_path,
                            'PREDICATE':[0],
                            'JOIN':clipPath,
                            'JOIN_FIELDS':['LONGITUD'],
                            'METHOD':0,
                            'DISCARD_NONMATCHING':False,
                            'PREFIX':'',
                            'OUTPUT':'TEMPORARY_OUTPUT'}
                processing.runAndLoadResults("native:joinattributesbylocation", params12)

                #Si la capa existe, la seleccionamos:
                if QgsProject.instance().mapLayersByName('Capa unida'):
                    join_subbasin = QgsProject.instance().mapLayersByName("Capa unida")[0]
                else:
                    join_subbasin = QgsProject.instance().mapLayersByName("Joined layer")[0]

                # join_subbasin = QgsProject.instance().mapLayersByName("Joined layer")[0]
                # join_subbasinPath = join_subbasin.source()

                #Extraer altitud maxima de la red de drenaje
                #Extraer vertices del cauce de la red de drenaje
                params13 = {
                            'INPUT':clipPath,
                            'OUTPUT':'TEMPORARY_OUTPUT'}
                processing.runAndLoadResults("native:extractvertices", params13)

                #Si la capa existe, la seleccionamos:
                if QgsProject.instance().mapLayersByName('Vértices'):
                    vertex3 = QgsProject.instance().mapLayersByName("Vértices")[0]
                else:
                    vertex3 = QgsProject.instance().mapLayersByName("Vertices")[0]

                # vertex3 = QgsProject.instance().mapLayersByName("Vertices")[0]
                vertexPath3 = vertex3.source()

                #Copiar valor celda raster (MDT) en vertices del cauce red drenaje
                params14 = {
                            'INPUT':vertexPath3,
                            'RASTERCOPY':self.folder + '/EasyBasin/Capas_SIG/MDT/MDT_corregido.tif',
                            'COLUMN_PREFIX':'ALT_red',
                            'OUTPUT':'TEMPORARY_OUTPUT'}
                processing.runAndLoadResults("qgis:rastersampling",params14 )

                #Si la capa existe, la seleccionamos:
                if QgsProject.instance().mapLayersByName('Muestreado'):
                    sample = QgsProject.instance().mapLayersByName("Muestreado")[0]
                else:
                    sample = QgsProject.instance().mapLayersByName("Sampled")[0]

                # sample = QgsProject.instance().mapLayersByName("Sampled")[0]
                # samplePath = sample.source()

                #Generar dataframe con Pandas para agrupar inputs para HMS
                main_elevation = QgsVectorLayer(elevation_path, str(points_name), "ogr")
                main_stream = QgsVectorLayer(lfpSub_path, str(stream_name), "ogr")
                # main_subbasin = QgsVectorLayer(subbasin_path, str(basin_name), "ogr")
                main_subbasin = join_subbasin
                #Extraer informacion de la capa de subcuenca
                for feature in main_subbasin.getFeatures():
                    sub = feature.attribute("cat")
                    area = feature.attribute("AREA")
                    alt_min_basin = feature.attribute("ALT_min")
                    alt_max_basin = feature.attribute("ALT_max")
                    area_impermeable = feature.attribute("Area_Imp_s")
                    po_miteco = feature.attribute("p0_500m_me")
                    po_CLC2000 = feature.attribute("p0_CLC2000")
                    po_CLC2018 = feature.attribute("p0_CLC2018")
                    CN_miteco = 25400/((float(po_miteco)/0.2)+254)
                    CN_CLC2000 = 25400/((float(po_CLC2000)/0.2)+254)
                    CN_CLC2018 = 25400/((float(po_CLC2018)/0.2)+254)
                    longitud_red = feature.attribute("LONGITUD")

                    # pendiente = (float(alt_max_basin)-float(alt_min_basin))/float(Long)*100
                    HMS_data.append({'SUB': sub, 'AREA': area, 'ALT_max_basin': alt_max_basin, 'ALT_min_basin': alt_min_basin, 'Area_Impermeable': area_impermeable,
                                        'p0_500m_MITECO': po_miteco, 'p0_100m_CLC2000': po_CLC2000, 'p0_100m_CLC2018': po_CLC2018, 'CN_500m_MITECO': CN_miteco, 'CN_100m_CLC2000': CN_CLC2000, 'CN_100m_CLC2018': CN_CLC2018, 'LONGITUD_Cauce': longitud_red})

                #Extraer informacion de la capa de cauce
                for feature in main_stream.getFeatures():
                    longitud = feature.attribute("LONGITUD")
                    HMS_data2.append({'LONGITUD_Cauce_Principal': longitud})

                #Extraer informacion de la capa de puntos de altitud cauce principal
                max_altitude = None
                min_altitude = None
                for feature in main_elevation.getFeatures():
                    altitud = feature.attribute("ALT1")
                    if max_altitude is None or altitud > max_altitude:
                        max_altitude = altitud
                    if min_altitude is None or altitud < min_altitude:
                        min_altitude = altitud
                HMS_data3.append({'ALT_max_Cauce_Principal': max_altitude, 'ALT_min_Cauce_Principal': min_altitude})

                #Extraer informacion de la capa de puntos de altitud red principal
                max_alt = None
                for feature in sample.getFeatures():
                    altitud = feature.attribute("ALT_red1")
                    if max_alt is None or altitud > max_alt:
                        max_alt = altitud
                HMS_data4.append({'ALT_max_Cauce': max_alt})

                #Eliminar capas sobrantes
                # layer5 = QgsProject.instance().mapLayersByName('Dissolved')[0]
                QgsProject.instance().removeMapLayer(dissolve.id()) 
                # layer6 = QgsProject.instance().mapLayersByName('Clipped')[0]
                QgsProject.instance().removeMapLayer(clip.id()) 
                # layer7 = QgsProject.instance().mapLayersByName('Joined layer')[0]
                QgsProject.instance().removeMapLayer(join_subbasin.id()) 
                # layer8 = QgsProject.instance().mapLayersByName('Vertices')[0]
                QgsProject.instance().removeMapLayer(vertex3.id()) 
                # layer9 = QgsProject.instance().mapLayersByName('Sampled')[0]
                QgsProject.instance().removeMapLayer(sample.id())

                layer10 = QgsProject.instance().mapLayersByName(basin_name)[0]
                QgsProject.instance().removeMapLayer(layer10.id())
                layer11 = QgsProject.instance().mapLayersByName(stream_name)[0]
                QgsProject.instance().removeMapLayer(layer11.id())
                layer12 = QgsProject.instance().mapLayersByName(points_name)[0]
                QgsProject.instance().removeMapLayer(layer12.id())

        #Generar columnas del dataframe
        df_HMS1 = pd.DataFrame(HMS_data, columns=['SUB', 'AREA', 'ALT_max_basin', 'ALT_min_basin','Area_Impermeable','p0_500m_MITECO','p0_100m_CLC2000','p0_100m_CLC2018','CN_500m_MITECO','CN_100m_CLC2000','CN_100m_CLC2018','LONGITUD_Cauce'])
        df_HMS2 = pd.DataFrame(HMS_data2,columns=['LONGITUD_Cauce_Principal'])
        df_HMS3 = pd.DataFrame(HMS_data3,columns=['ALT_max_Cauce_Principal', 'ALT_min_Cauce_Principal'])
        df_HMS4 = pd.DataFrame(HMS_data4,columns=['ALT_max_Cauce'])
        #Unir varios dataframes por columna
        df = pd.concat([df_HMS1, df_HMS2, df_HMS3, df_HMS4], axis=1)

        #Generar formato final del archivo de inputs_HMS
        df['PENDIENTE (%)'] = np.where(
                                        df['LONGITUD_Cauce_Principal'] > df['LONGITUD_Cauce'],
                                        (df['ALT_max_Cauce_Principal'] - df['ALT_min_Cauce_Principal']) / df['LONGITUD_Cauce_Principal'] * 100,
                                        (df['ALT_max_Cauce'] - df['ALT_min_basin']) / df['LONGITUD_Cauce'] * 100)
        df['TIEMPO DE CONCENTRACION (HR)'] = np.where(
                                                        df['LONGITUD_Cauce_Principal'] > df['LONGITUD_Cauce'],
                                                        0.3*((df['LONGITUD_Cauce_Principal']/1000)**(0.76))*((df['PENDIENTE (%)']/100)**(-0.19)),
                                                        0.3*((df['LONGITUD_Cauce']/1000)**(0.76))*((df['PENDIENTE (%)']/100)**(-0.19)))
        df['Lag Time (MIN)'] = df['TIEMPO DE CONCENTRACION (HR)']*60*0.6
        df['Muskingum K (HR)'] = np.where(
                                            df['LONGITUD_Cauce_Principal'] > df['LONGITUD_Cauce'],
                                            0.18*((df['LONGITUD_Cauce_Principal']/1000)*(df['PENDIENTE (%)']/100)**-0.25)**0.76,
                                            0.18*((df['LONGITUD_Cauce']/1000)*(df['PENDIENTE (%)']/100)**-0.25)**0.76)
        df['Muskingum X'] = '0(Caudaloso, poca pendiente) - 0.5(Poco caudaloso, gran pendiente)'
        df['AREA (KM2)'] = df['AREA']/1000000
        df['LONGITUD CAUCE (KM)'] = np.where(
                                                df['LONGITUD_Cauce_Principal'] > df['LONGITUD_Cauce'],
                                                df['LONGITUD_Cauce_Principal']/1000,
                                                df['LONGITUD_Cauce']/1000)
        df['COTA MAX CAUCE (msnm)'] = np.where(
                                                df['LONGITUD_Cauce_Principal'] > df['LONGITUD_Cauce'],
                                                df['ALT_max_Cauce_Principal'],
                                                df['ALT_max_Cauce'])
        df['COTA MIN CAUCE (msnm)'] = np.where(
                                                df['LONGITUD_Cauce_Principal'] > df['LONGITUD_Cauce'],
                                                df['ALT_min_Cauce_Principal'],
                                                df['ALT_min_basin'])
        P0 = self.comboBoxP0.currentText()
        if P0 == "Raster P0 500m (MITECO)":
            df['UMBRAL DE ESCORRENTIA (mm)'] = df['p0_500m_MITECO']
            df['NUMERO DE CURVA (CN)'] = df['CN_500m_MITECO']
        if P0 == "Raster P0 100m (CLC2000)":
            df['UMBRAL DE ESCORRENTIA (mm)'] = df['p0_100m_CLC2000']
            df['NUMERO DE CURVA (CN)'] = df['CN_100m_CLC2000']
        if P0 == "Raster P0 100m (CLC2018)":
            df['UMBRAL DE ESCORRENTIA (mm)'] = df['p0_100m_CLC2018']
            df['NUMERO DE CURVA (CN)'] = df['CN_100m_CLC2018']
        df['AREA IMPERMEABLE (%)'] = df['Area_Impermeable']/df['AREA']*100
        df['SUBCUENCA'] = df['SUB'] 
        df_HMS = df[['SUBCUENCA','AREA (KM2)', 'LONGITUD CAUCE (KM)', 'COTA MAX CAUCE (msnm)','COTA MIN CAUCE (msnm)','PENDIENTE (%)','TIEMPO DE CONCENTRACION (HR)','Lag Time (MIN)', 'UMBRAL DE ESCORRENTIA (mm)', 'NUMERO DE CURVA (CN)', 'AREA IMPERMEABLE (%)', 'Muskingum K (HR)', 'Muskingum X']].copy()
        df_HMS = df_HMS.sort_values(by='SUBCUENCA')

        #Pasar dataframe a CSV
        csv_HMS_path = self.folder + '/EasyBasin/HMS/inputs_HEC-HMS.csv'
        df_HMS.to_csv(csv_HMS_path, index=False)

        #Eliminar capas sobrantes
        layer1 = QgsProject.instance().mapLayersByName('Vertices Cauce')[0]
        QgsProject.instance().removeMapLayer(layer1.id()) 
        # layer2 = QgsProject.instance().mapLayersByName('Intersections')[0]
        QgsProject.instance().removeMapLayer(intersect.id()) 

        #Aplicar metodo racional por subcuenca 
        df_MR = df_HMS[['SUBCUENCA','AREA (KM2)', 'LONGITUD CAUCE (KM)', 'COTA MAX CAUCE (msnm)','COTA MIN CAUCE (msnm)','PENDIENTE (%)','TIEMPO DE CONCENTRACION (HR)', 'UMBRAL DE ESCORRENTIA (mm)']].copy()

        #Coger valores fijos de la interfaz de EasyBasin
        T = self.comboBoxPeriodo.currentText() #Período de retorno
        Pd = float(self.lineEditPd.text()) #PCP max diaria
        I1 = float(self.lineEdit_Torrencialidad.text()) #Índice de torrencialidad
        b = float(self.lineEdit_b.text()) #Coeficiente corrector del umbral de escorrentía

        #Generar variables del Metodo Racional
        df_MR['Pd (MM)'] = Pd
        df_MR['KA'] = np.where( df_MR['AREA (KM2)'] > 1, 1 - np.log10(df_MR['AREA (KM2)'])/15, 1)
        df_MR['Id (MM/HR)'] = df_MR['Pd (MM)']*df_MR['KA']/24
        df_MR['I1/Id'] = I1
        df_MR['Fa'] = df_MR['I1/Id']**(3.5287 - 2.5287*(df_MR['TIEMPO DE CONCENTRACION (HR)']**0.1))
        df_MR['I (MM/HR)'] = df_MR['Id (MM/HR)']*df_MR['Fa']
        df_MR['b'] = b
        df_MR['Po (MM)'] =  df_MR['UMBRAL DE ESCORRENTIA (mm)']*df_MR['b']
        df_MR['C'] = np.where( df_MR['Pd (MM)']*df_MR['KA'] > df_MR['Po (MM)'], 
        ((df_MR['Pd (MM)']*df_MR['KA']/df_MR['Po (MM)']-1)*(df_MR['Pd (MM)']*df_MR['KA']/df_MR['Po (MM)']+23))/ ((df_MR['Pd (MM)']*df_MR['KA']/df_MR['Po (MM)']+11)**2), 0)
        df_MR['Kt'] = 1 + (df_MR['TIEMPO DE CONCENTRACION (HR)']**1.25)/(df_MR['TIEMPO DE CONCENTRACION (HR)']**1.25 + 14)
        df_MR['PERIODO RETORNO (AÑOS)'] = T
        df_MR['QT (M3/S)'] = df_MR['Kt']*df_MR['I (MM/HR)']*df_MR['C']*df_MR['AREA (KM2)']/3.6

        #Pasar dataframe a CSV
        csv_MR_path = self.folder + '/EasyBasin/Metodo_Racional_Subcuencas.csv'
        df_MR.to_csv(csv_MR_path, index=False)

        self.pushButton_HMS_2.setEnabled(True)   
        self.pushButton_labelbarHMS.setEnabled(True)
        self.pushButton_labelbarMR.setEnabled(True)

    def info(self):
        text = "<b>EasyBasin</b> es un complemento de QGIS para la delimitación de cuencas hidrográficas y la obtención del caudal máximo anual mediante el método racional descrito en la norma 5.2-IC DRENAJE SUPERFICIAL.<br><br><b>Manual</b>: https://adrlballesteros.github.io/EasyBasin/ <br><br><b>Referencia</b>: https://doi.org/10.1016/j.ejrh.2022.101308 <br><br>Para cualquier duda o sugerencia contactar con <b>alopez6@ucam.edu</b>. <br><br>Si encuentras útil este plugin, o si te ha ahorrado tiempo en tu trabajo, considera apoyarlo invitándome a un café. Gracias 😊"
        msgINFO = QMessageBox()
        msgINFO.setWindowIcon(QIcon(":/images/icon.png"))
        msgINFO.setWindowTitle("Help & About")
        msgINFO.setText(text)
        msgINFO.setTextFormat(Qt.RichText)
        msgINFO.setStandardButtons(QMessageBox.Ok)
        msgINFO.exec_()

    def open(self):
        FolderPath = self.pushButton_labelPath2.text()
        webbrowser.open(FolderPath)

        self.pushButton_labelPath2.setStyleSheet("QPushButton { color: rgb(85, 0, 127); }")

    def openCSV(self):
        self.folder = str(self.pushButton_labelPath2.text())
        csv_HMS_path = self.folder + '/EasyBasin/HMS/inputs_HEC-HMS.csv'
        webbrowser.open(csv_HMS_path)

    def openCSVMR(self):
        self.folder = str(self.pushButton_labelPath2.text())
        csv_MR_path = self.folder + '/EasyBasin/Metodo_Racional_Subcuencas.csv'
        webbrowser.open(csv_MR_path)

    def coffee(self):
            self.labelCheck_coffee.setText("😊 GRACIAS!")
            url = "https://www.buymeacoffee.com/alopez6"
            webbrowser.open(url)

