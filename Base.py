# -*- coding: utf-8 -*-
"""
/***************************************************************************
 **EasyBasin v3
 **A QGIS plugin
 **Descripcion: Plugin para la creación de cuencas hidrográficas.
--------------------------------------------------
        begin                : **Diciembre-2023
        copyright            : **COPYRIGHT
        email                : **alopbal@upv.es
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
import os.path
from qgis.core import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QAction

from .BaseDialog import BaseDialog
import EasyBasin_v3.gui.generated.resources_rc


class Base:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = QAction(
            QIcon(":/imgBase/icon.png"), "EasyBasin v3", self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&EasyBasin v3", self.action)

    def unload(self):
        self.iface.removePluginMenu("&EasyBasin v3", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        self.dlg = BaseDialog(self.iface)
        self.dlg.setWindowFlags(
            Qt.WindowSystemMenuHint
            | Qt.MSWindowsFixedSizeDialogHint
            | Qt.WindowTitleHint
            | Qt.WindowMinimizeButtonHint
        )
        self.dlg.InitialWindow()
        # self.dlg.show()
        # self.dlg.exec_()
