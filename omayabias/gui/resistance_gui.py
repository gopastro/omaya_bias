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
        self.skiprows = 2 #size of header for database file
        self.filename = ""
        self.idname = ""
        self.resistance = 0.0
        self.vmin=""
        self.vmax=""
        self.data=""
        self.df=[]
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
        self.setWindowTitle('OMAYA RESISTANCE GUI')

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
        res_groupbox.setLayout(self.add_res_grid())#Sets 'bias_groupbox' to a Hor. Layout
        openB=QPushButton("Open File")
        openB.clicked.connect(self.openFileNameDialog)
        #Master --> Bias (vertically oriented)
        vlayout.addWidget(openB)
        vlayout.addWidget(res_groupbox)

        label_groupbox = QGroupBox("")
        label_groupbox.setLayout(self.add_label_grid())
        vlayout.addWidget(label_groupbox)
        #self.fileLabel=QLabel("No file selected")
        #self.fileLabel.setFont(QFont("Arial", 20))
        #vlayout.addWidget(self.fileLabel)
        #self.idLabel=QLabel("")
        #self.idLabel.setFont(QFont("Arial",20))
        #vlayout.addWidget(self.idLabel)
        #Sets Master Groupbox to GUI's central GridLayout 'grid'
        self.grid = QGridLayout()
        self.grid.addWidget(master_groupbox,0, 0,0, 1)      

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
        canvas_groupbox.setLayout(vlayout2)

        #Sets Canvas Groupbox to GUI's central GridLayout 'grid'
        self.grid.addWidget(canvas_groupbox, 0, 1, 7, 4)

        #Now wid --> Master Groupbox + Canvas Groupbox

        #Sets 'grid' to the central widget 'wid'
        wid.setLayout(self.grid)        

        #Draw it all!
        self.show()

    def add_label_grid(self):
        grid = QGridLayout()
        idlabel=QLabel("SIS ID:")
        filelabel=QLabel("File Name:")
        resistancelabel=QLabel("Resistance:")
        slopelabel=QLabel("Slope:")
        intlabel=QLabel("Intercept:")
        self.idLabel=QLabel("SIS ID")
        self.fileLabel=QLabel("File Name")
        self.resistanceLabel=QLabel("Resistance")
        self.slopeLabel=QLabel("Slope")
        self.intLabel=QLabel("Intercept")

        #add them widgets
        grid.addWidget(filelabel,0,0)
        grid.addWidget(idlabel,1,0)
        grid.addWidget(resistancelabel,2,0)
        grid.addWidget(slopelabel,3,0)
        grid.addWidget(intlabel,4,0)
        grid.addWidget(self.idLabel,1,1)
        grid.addWidget(self.fileLabel,0,1)
        grid.addWidget(self.resistanceLabel,2,1)
        grid.addWidget(self.slopeLabel,3,1)
        grid.addWidget(self.intLabel,4,1)
        return grid

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            fileName = str(fileName)
            self.data=pd.read_csv(fileName,skiprows=3)
            print(self.data.keys())
            print(self.data.Vs)
           #self.df = pd.DataFrame({'Vs':data['Vs'],'Is':data['Is']})
            self.plot_ivcurve(self.data)
            name = fileName.split("/")
            setname=str(name[-1])
            self.fileLabel.setText(setname)
            file = open(fileName,"r")
            sisid=file.readline()[13:-3]
            file.close()
            self.idLabel.setText(sisid)

            
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

    def dummy(self):
        print("AHHHHH")
        
    def add_res_grid(self):
        grid = QGridLayout()
        vminL = QLabel('Vmin range (mV)')
        vmaxL = QLabel('Vmax range (mV)')
        self.vmin=QLineEdit("15")
        self.vmax=QLineEdit("20")
        resB=QPushButton("Get Resistance")
        resB.setToolTip('Calculates resistance of junction')
        resB.clicked.connect(self.fit_wrapper)
        grid.addWidget(vminL,0,0)
        grid.addWidget(vmaxL,1,0)
        grid.addWidget(self.vmin,0,1)
        grid.addWidget(self.vmax,1,1)
        grid.addWidget(resB,2,0,1,2)
        return grid     
            
    def plot_ivcurve(self,df):
        self.canvas.plot(df,self.idname, clear=False)

    def fit_wrapper(self):
        df = self.data
        try:
           vmin_res = float(self.vmin.text())
           vmax_res = float(self.vmax.text())
        except ValueError:
           vmin_res = 0.015
           vmax_res = 0.020
        vmin_res,vmax_res = vmin_res * 1e-3, vmax_res * 1e-3
        print(type(df))
        results = norm_state_resistance.norm_state_res(df,vmin_res,vmax_res)
        print(results)
        
    
        
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

    def plot(self, df, name, clear=True):
        """plot data onto axes"""
        if clear:
            self.clear()
        self.axes.plot(df.Vj/1e-3, df.Is/1e-6, 'o-')
        #self.axes.set_title(name)
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
