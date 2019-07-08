import sys, datetime
from matplotlib.backends.backend_qt5agg import \
    (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QPushButton, QAction, QDesktopWidget, QToolTip, QPushButton, QLineEdit, QTextEdit, QComboBox, qApp, QLabel, QGridLayout, QGroupBox, QHBoxLayout, QVBoxLayout, QFileDialog, QRadioButton)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QTimer
from PyQt5 import QtGui, QtCore
from omayabias.sisbias.sisbias import SISBias
from omayabias.logging import logger
from omayabias.sisdb.datamodel import GelPack, SISDimensions, Temperature
from omayabias.lakeshore.lakeshore_218 import Lakeshore
from omayabias.lakeshore.myGpib import Gpib
import numpy
import time
import pandas as pd
from omayabias.utils import norm_state_resistance

logger.name = __name__
QIcon.setThemeSearchPaths(['/usr/share/icons'])
QIcon.setThemeName('Humanity')

class IVCURVE_GUI(QMainWindow):

    def __init__(self):
        """Initializes some GUI parameters and calls 'initUI()'"""
        super(IVCURVE_GUI,self).__init__()
        self.bias_widgets = {} #dic for Bias widgets
        self.sisbias = SISBias() #class to control SISBias devices
        self.lk = Lakeshore() #class to control Lakeshore Temp Monitor
        self.sweep_data = {} #dic for storing sweep data
        self.devsel_cb = {} 
        self.devices = [None, None]
        self.sweep_time = [None, None]
        self.skiprows = 2 #size of header for database file
        self.initUI() #this function initializes the widgets and layouts
       
    def initUI(self):
        """Initializes widgets and layout for the IVCURVE_GUI window"""

        #Create a status bar
        self.statusBar().showMessage('Ready')

        #Create a menubar
        #menubar = self.menuBar()
        #fileMenu = menubar.addMenu('&File')
        #fileMenu.addAction(exitAct)
        self.mainMenu = self.menuBar()
        self.add_menu(self.mainMenu)
        
        #Create a toolbar
        self.toolbar = self.addToolBar('Exit')
        self.add_toolbar(self.toolbar)

        #Set title for GUI window
        self.setWindowTitle('OMAYA Bias GUI')

        #Initializes main widget 'wid' that Master and Canvas Groupboxes will lock to
        wid = QWidget(self)
        self.setCentralWidget(wid)

        #Master Groupbox
        master_groupbox = QGroupBox("Master")
        vlayout = QVBoxLayout()
        master_groupbox.setLayout(vlayout)#Sets 'master_groupbox' to a Vertical Layout

        #Bias Groupbox
        res_groupbox = QGroupBox("Res")
        hlayout = QHBoxLayout()
        res_groupbox.setLayout(self.add_res_grid(0))#Sets 'bias_groupbox' to a Hor. Layout
        openB=QPushButton("Open File")
        openB.clicked.connect(self.openFileNameDialog)
        #Master --> Bias (vertically oriented)
        vlayout.addWidget(openB)
        vlayout.addWidget(res_groupbox)

        fileLabel=QLabel("No file selected")
        vlayout.addWidget(fileLabel)
        #Sets Master Groupbox to GUI's central GridLayout 'grid'
        self.grid = QGridLayout()
        self.grid.addWidget(master_groupbox, 0, 0, 5, 1)      

        #Canvas Groupbox
        canvas_groupbox = QGroupBox("IV Curve Plot")
        #Initializes GUI's PlotCanvas class as 'canvas'
        self.canvas = PlotCanvas(self, width=5, height=4)
        #Initializes clear button widget 'clearB' for 'canvas'
        clearB = QPushButton('Clear Plot', self)
        clearB.setToolTip('clear plot')
        #Sets 'clearB' function to canvas.clear()
        clearB.clicked.connect(self.canvas.clear)

        #Adds both widgets to a Vertical Layout 'vlayout2'
        vlayout2 = QVBoxLayout()
        vlayout2.addWidget(self.canvas)
        vlayout2.addWidget(clearB)
        #Adds matplotlib toolbar to control 'canvas'
        self.addToolBar(QtCore.Qt.BottomToolBarArea,
                        NavigationToolbar2QT(self.canvas, self))
        #vlayout2.addWidget(self.addToolBar(QtCore.Qt.BottomToolBarArea,
        #                                   NavigationToolbar2QT(self.canvas, self)))
        #vlayout2.addWidget(self.addToolBar(NavigationToolbar2QT(self.canvas, self)))
        canvas_groupbox.setLayout(vlayout2)

        #Sets Canvas Groupbox to GUI's central GridLayout 'grid'
        self.grid.addWidget(canvas_groupbox, 0, 1, 7, 4)

        #Now wid --> Master Groupbox + Canvas Groupbox

        #Sets 'grid' to the central widget 'wid'
        wid.setLayout(self.grid)        

        #Draw it all!
        self.show()


    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)
            data=pd.read_csv(fileName,skiprows=3)
            print(data)
            self.plot_ivcurve(data)
        return data,fileName


            
    def add_menu(self, mainMenu):
        """Adds a menu feature to the main window"""
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        searchMenu = mainMenu.addMenu('Search')
        toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')

        pcaMenu = QMenu('PCA', self)
        
        exitButton = QAction(QIcon.fromTheme('exit'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)
    
    def add_toolbar(self, toolbar):
        """Adds a toolbar feature to the main window"""
        exitAct = QAction(QIcon.fromTheme('exit'), 'Exit', self)
        #exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(self.close)
        toolbar.addAction(exitAct)

    def center(self):
        """detects desktop resolution and sets window in center"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def add_res_grid(self,df):
        grid = QGridLayout()
        vminL = QLabel('Vmin range (mV)')
        vmaxL = QLabel('Vmax range (mV)')
        vmin=QLineEdit()
        vmax=QLineEdit()
        resB=QPushButton("Get Resistance")
        resB.setToolTip('Calculates resistance of junction')
        resB.clicked.connect(self.fit_wrapper(df,0.015,0.020))
        grid.addWidget(vminL,0,0)
        grid.addWidget(vmaxL,1,0)
        grid.addWidget(vmin,0,1)
        grid.addWidget(vmax,1,1)
        grid.addWidget(resB,2,0,1,2)
        return grid     
            
    def plot_ivcurve(self,df):
        self.canvas.plot(df, clear=False)

    def fit_wrapper(self,df,vmin,vmax):
        try:
           vmin_res = float(self.vmin.text())
           vmax_res = float(self.vmax.text())
        except ValueError:
           vmin_res = 0.015
           vmax_res = 0.020
        try:
            vmin_res,vmax_res = vmin_res * 1e-3, vmax_res * 1e-3
            #print(vmin_res,vmax_res)
            results = norm_state_resistance.norm_state_res(df,vmin,vmax)           
            print("{0:<11} : {1:3.3f} +- {2:3.3e}".format("Resistance",results[0][0],results[2][1]))
            print("{0:<11} : {1:3.3e} +- {2:3.3e}".format("y-intercept",results[1][0],results[1][1]))
            print("{0:<11} : {1:3.3e} +- {2:3.3e}".format("IV Slope",results[2][0],results[2][1]))
        except KeyError:
            print('ERROR:need sweep data')

        except ValueError:
            print('ERROR:sweep at finer resolution')
        
class PlotCanvas(FigureCanvas):
    """Class for functions related to matplotlib plot"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """Initializes matplotlib figure"""
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot(self, df, channel=0, clear=True):
        """plot data onto axes"""
        if clear:
            self.clear()
        self.axes.plot(df.Vj/1e-3, df.Is/1e-6, 'o-', label='Channel %d' % channel)
        self.axes.set_title('SIS Channel %d' % channel)
        self.axes.legend(loc='best')
        self.draw()
        
    def clear(self):
        """clear axes"""
        self.axes.cla()
        self.draw()
        
    def save(self):
        """save figure to file"""
        self.fig.savefig('test.png')
# NEW
# BOOZIN        
# MAIN PROGRAM
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ivcurve_gui = IVCURVE_GUI()
    
    sys.exit(app.exec_())
