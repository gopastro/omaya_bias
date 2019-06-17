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

        #Initializes widget 'wid' that layouts will lock to
        wid = QWidget(self)
        self.setCentralWidget(wid)

        #Master Groupbox
        master_groupbox = QGroupBox()
        vlayout = QVBoxLayout()
        master_groupbox.setLayout(vlayout)#Sets 'master_groupbox' to a Vertical Layout

        #Bias Groupbox
        bias_groupbox = QGroupBox()
        hlayout = QHBoxLayout()
        bias_groupbox.setLayout(hlayout)#Sets 'bias_groupbox' to a Hor. Layout

        #Temp Monitor Groupbox
        temp_groupbox = QGroupBox("Temperature Monitor")
        channels = ['1', '2', '3', '4', '5', '6', '7', '8']
        #'add_temp_monitor_grid' returns a GridLayout populated w/ temp widgets
        #Temp Monitor Groupbox is then set to this grid
        temp_groupbox.setLayout(self.add_temp_monitor_grid(channels))

        #Master --> Bias + Temp Monitor (vertically oriented)
        vlayout.addWidget(bias_groupbox)
        vlayout.addWidget(temp_groupbox)

        #Bias --> Chan0 + Chan1 Groupboxes (horizontally oriented)
        chan0_groupbox = QGroupBox("Channel 0")
        chan1_groupbox = QGroupBox("Channel 1")
        hlayout.addWidget(chan0_groupbox)
        hlayout.addWidget(chan1_groupbox)

        #Select Device, Set Bias and Sweep Groupboxes (2 per chan)
        chan0_seldev_box = QGroupBox("Select Device")
        chan1_seldev_box = QGroupBox("Select Device")
        chan0_setbox = QGroupBox("Set Bias")
        chan0_sweepbox = QGroupBox("Sweep")
        chan1_setbox = QGroupBox("Set Bias")
        chan1_sweepbox = QGroupBox("Sweep")

        #Initializes two Vertical Layouts for Chan0/1 Grouboxes
        vlayout0 = QVBoxLayout()
        vlayout1 = QVBoxLayout()

        #Sets Select Device to GridLayout populated with widgets
        chan0_seldev_box.setLayout(self.add_select_device_grid(0))
        chan1_seldev_box.setLayout(self.add_select_device_grid(1))
        #Adds Groupboxes to Vertical Layout for Chan0
        vlayout0.addWidget(chan0_seldev_box)
        vlayout0.addWidget(chan0_setbox)
        vlayout0.addWidget(chan0_sweepbox)
        #Sets Set Bias and Sweep to GridLayouts populated with widgets
        chan0_setbox.setLayout(self.add_bias_grid(0))
        chan0_sweepbox.setLayout(self.add_bias_sweep_grid(0))
        #Adds Grouboxes to Vertical Layout for Chan1
        vlayout1.addWidget(chan1_seldev_box)        
        vlayout1.addWidget(chan1_setbox)
        vlayout1.addWidget(chan1_sweepbox)
        #Sets Set Bias and Sweep to GridLayouts populated with widgets
        chan1_setbox.setLayout(self.add_bias_grid(1))
        chan1_sweepbox.setLayout(self.add_bias_sweep_grid(1))        

        #Chan0/1 --> Select Device + Set Bias + Sweep (ver. oriented)
        chan0_groupbox.setLayout(vlayout0)
        chan1_groupbox.setLayout(vlayout1)
        #from before at Line 85:
        #Bias --> Chan0 + Chan1 (horizontally oriented)

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

        #Sets 'grid' to the central widget 'wid'
        wid.setLayout(self.grid)        

        #Draw it all!
        self.show()

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

    def add_temp_monitor_grid(self, channels):
        """Takes a dic of lakeshore 'channels' and populates
        a GridLayout for Temperature Monitor widgets"""
        grid = QGridLayout() #GridLayout we will return
        bf = QFont("Times", 12, QFont.Bold)
        self.temp_labels = {} #Dic for Label widgets
        self.temp_widgets = {} #Dic for Monitor widgets
        i = 0
        for chan in channels:
            #Create a Label widget for 'chan'
            self.temp_labels[chan] = QLabel()
            self.temp_labels[chan].setText("%s" %chan)
            #Create a Monitor widget for 'chan'
            self.temp_widgets[chan] = QLabel()
            self.temp_widgets[chan].setText("")
            self.temp_widgets[chan].setFont(bf)
            #Adds Label widgets to even indices in grid
            grid.addWidget(self.temp_labels[chan], 0, i+1)
            #Adds Monitor widgets to odd indices in grid
            grid.addWidget(self.temp_widgets[chan], 0, i+2)
            i += 2
        #Connects Monitor widgets to lakeshore temperature readings
        self.add_temp_monitor_hooks()
        return grid

            
    def add_select_device_grid(self, channel):
        """Takes a channel number 'channel' and populates
        a GridLayout for Select Device widgets"""
        grid = QGridLayout() #GridLayout we will return
        dset = QLabel('Select Device: ')
        #Create a combobox for listing SIS Device ID's
        self.devsel_cb[channel] = QComboBox()
        #Make combobox autocomplete search
        self.devsel_cb[channel].setEditable(True)
        lis = []
        #Gets SIS Device ID from the database and stores them in 'lis'
        for sisd in SISDimensions.select().order_by(SISDimensions.id):
            lis.append("GP# %s: %s %s %s" % (sisd.gelpack.description, sisd.sis2letter, sisd.sisrowcol, sisd.gelpack_label))
        #Populates the combobox with the list of SIS Device IDs 
        self.devsel_cb[channel].addItems(lis)
        if channel == 0:
            self.devsel_cb[channel].currentIndexChanged.connect(self.dev_selection_change0)
        else:
            self.devsel_cb[channel].currentIndexChanged.connect(self.dev_selection_change1)
        #Sets Label and Combbox widgets to the GridLayout
        grid.addWidget(dset, 0, 0)
        grid.addWidget(self.devsel_cb[channel], 0, 1)
        return grid

    def dev_selection_change0(self, i):
        """Special function"""
        self.devices[0] = self.devsel_cb[0].currentText()
        
    def dev_selection_change1(self, i):
        """Special function"""
        self.devices[1] = self.devsel_cb[1].currentText()
        
    def add_bias_grid(self, channel):
        grid = QGridLayout()
        vset = QLabel('Vj (mV)')
        self.bias_widgets['Vj%d' % channel] = QLineEdit()
        self.bias_widgets['Vj%d' % channel].returnPressed.connect(lambda:self.Vjset(channel))
        pcalab = QLabel('Bias Mode:')
        self.bias_widgets['PCA0%d' % channel] = QRadioButton("Constant V")
        self.bias_widgets['PCA1%d' % channel] = QRadioButton("Constant R")
        self.bias_widgets['PCA0%d' % channel].setChecked(True)
        self.bias_widgets['PCA0%d' % channel].toggled.connect(lambda:self.pcastate(self.bias_widgets['PCA0%d' % channel]))
        self.bias_widgets['PCA1%d' % channel].toggled.connect(lambda:self.pcastate(self.bias_widgets['PCA1%d' % channel]))
        wid = QWidget()
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.bias_widgets['PCA0%d' % channel])
        hlayout.addWidget(self.bias_widgets['PCA1%d' % channel])
        wid.setLayout(hlayout)
        Islab = QLabel('Is (uA):')
        Vslab = QLabel('Vs (mV):')
        self.bias_widgets['IsLabel%d' % channel] = QLabel('Is (uA)')
        self.bias_widgets['VsLabel%d' % channel] = QLabel('Vs (mV)')
        font = QFont("Times", 12, QFont.Bold)
        self.bias_widgets['IsLabel%d' % channel].setFont(font)
        self.bias_widgets['VsLabel%d' % channel].setFont(font)
        self.add_bias_monitor_hooks()
        grid.addWidget(vset, 0, 0, 1, 2)
        grid.addWidget(self.bias_widgets['Vj%d' % channel],  0, 2, 1, 2)
        grid.addWidget(pcalab, 1, 0, 1, 2)
        grid.addWidget(wid, 1, 2, 1, 2)
        grid.addWidget(Islab, 2, 0)
        grid.addWidget(self.bias_widgets['IsLabel%d' % channel], 2, 1)
        grid.addWidget(Vslab, 2, 2)
        grid.addWidget(self.bias_widgets['VsLabel%d' % channel], 2, 3)
        return grid

    def Vjset(self, channel):
        try:
            Vj = float(self.bias_widgets['Vj%d' % channel].text()) * 1e-3
        except ValueError:
            Vj = 0.0 * 1e-3
        self.sisbias.xicor[channel].set_mixer_voltage(Vj)
            
    def pcastate(self, btn):
        txt = btn.text()
        print txt
        #pca_state = int(txt[3])
        #channel = int(txt[4])
        if btn.isChecked():
            if txt == "Constant V":
                self.sisbias.pca.SetMode(0)
            else:
                self.sisbias.pca.SetMode(1)
            
    def add_bias_monitor_hooks(self):
        self.bias_timer = QTimer()
        self.bias_timer.timeout.connect(self.update_bias_labels)
        self.bias_timer.start(3000)
    
    def update_bias_labels(self):
        for channel in (0, 1):
            Vs, Is = self.sisbias.adc.read_Vsense(channel), self.sisbias.adc.read_Isense(channel)
            self.bias_widgets['IsLabel%d' % channel].setText("%.2f" % (Is/1e-6))
            self.bias_widgets['VsLabel%d' % channel].setText("%.2f" % (Vs/1e-3))

    def add_temp_monitor_hooks(self):
        self.temp_timer = QTimer()
        self.temp_timer.timeout.connect(self.update_temp_widgets)
        self.temp_timer.start(3000)

    def update_temp_widgets(self):
        T = self.lk.read_temperature(0)
        tdic = {}
        for chan in range(1, 9):
            if chan not in (4, 8):
                tdic['temp%d' % chan] = T[chan]
        temperature = Temperature(**tdic)
        temperature.save()
        i = 1
        for chan in self.temp_widgets.keys():
            self.temp_widgets[chan].setText("%.2f" % (T[i]))
            i += 1
            
    def add_bias_sweep_grid(self, channel):
        grid = QGridLayout()
        vminL = QLabel('Vmin (mV)')
        vmaxL = QLabel('Vmax (mV)')
        vstep = QLabel('Vstep (mV)')
        self.bias_widgets['Vmin%d' % channel] = QLineEdit()
        self.bias_widgets['Vmax%d' % channel] = QLineEdit()
        self.bias_widgets['Vstep%d' % channel] = QLineEdit()
        self.bias_widgets['sweepbtn%d' % channel] = QPushButton('Sweep Channel %d' % channel, self)
        self.bias_widgets['sweepbtn%d' % channel].setToolTip('Sweep IV Curve')
        self.bias_widgets['sweepbtn%d' % channel].clicked.connect(lambda:self.sweep(self.bias_widgets['sweepbtn%d' % channel]))
        self.bias_widgets['savebtn%d' % channel] = QPushButton('Save Channel %d' % channel, self)
        self.bias_widgets['savebtn%d' % channel].setToolTip('Save IV Curve')
        self.bias_widgets['savebtn%d' % channel].clicked.connect(lambda:self.save_sweep(self.bias_widgets['savebtn%d' % channel]))
        self.bias_widgets['plotbtn%d' % channel] = QPushButton('Plot IV Curve')
        self.bias_widgets['plotbtn%d' % channel].setToolTip('Plot IV Curve')
        self.bias_widgets['plotbtn%d' % channel].clicked.connect(lambda:self.plot_ivcurve(channel))
        
        grid.addWidget(vminL, 0, 0)
        grid.addWidget(self.bias_widgets['Vmin%d' % channel],  0, 1)
        grid.addWidget(vmaxL, 1, 0)
        grid.addWidget(self.bias_widgets['Vmax%d' % channel],  1, 1)
        grid.addWidget(vstep, 2, 0)
        grid.addWidget(self.bias_widgets['Vstep%d' % channel],  2, 1)
        grid.addWidget(self.bias_widgets['sweepbtn%d' % channel], 3, 0, 1, 2)
        grid.addWidget(self.bias_widgets['savebtn%d' % channel], 4, 0, 1, 2)
        grid.addWidget(self.bias_widgets['plotbtn%d' % channel], 5, 0, 1, 2)
        return grid
        
    def center(self):
        """detects desktop resolution and sets window in center"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def sweep(self, btn):
        txt = btn.text()
        channel = int(txt.split('Sweep Channel ')[1])
        print "Sweeping Channel: %d" % channel
        try:
            vmin = float(self.bias_widgets['Vmin%d' % channel].text())
        except ValueError:
            vmin = 0.0
        try:
            vmax = float(self.bias_widgets['Vmax%d' % channel].text())
        except ValueError:
            vmax = 0.0
        try:
            vstep = float(self.bias_widgets['Vstep%d' % channel].text())
        except ValueError: 
            vstep = 0.1
        vmin, vmax, vstep = vmin * 1e-3, vmax * 1e-3, vstep * 1e-3
        self.bias_timer.stop()
        self.sisbias.pca.SetMode(0)
        lisdic = []
        for v in numpy.arange(vmin, vmax+vstep, vstep):
            dic = {}
            self.sisbias.xicor[channel].set_mixer_voltage(v)
            time.sleep(0.010)
            Vs, Is = self.sisbias.adc.read_Vsense(channel), self.sisbias.adc.read_Isense(channel)
            dic['Vj'] = v
            dic['Vs'] = Vs
            dic['Is'] = Is
            print v, Vs, Is
            lisdic.append(dic)
        self.sweep_data[channel] = pd.DataFrame(lisdic)
        #self.sweep_data[channel].to_csv('channel%d.csv' % channel)
        self.sweep_time[channel] = datetime.datetime.now().ctime()
        self.bias_timer.start(3000)
        
    def save_sweep(self, btn):
        txt = btn.text()
        channel = int(txt.split('Save Channel ')[1])
        print "Saving Channel: %d" % channel
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.csv)", options=options)
        metadata = pd.Series([{'device': self.devices[channel]}, {'channel': channel},
                              {'date': self.sweep_time[channel]}])
        if fileName:
            print "Saving Channel %d data to %s" % (channel, fileName)
            with open(fileName, 'w') as fout:
                metadata.to_csv(fout, index=False)
                self.sweep_data[channel].to_csv(fout, index=False)
            
    def plot_ivcurve(self, channel):
        self.canvas.plot(self.sweep_data[channel], channel, clear=False)
        
class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """Initializes matplotlib figure"""
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        #self.plot_test()

    def plot_test(self):
        data = [random.random() for i in range(25)]
        self.axes.plot(data, 'r-')
        
        self.axes.set_title('SIS Channel 0')
        self.draw()

    def plot(self, df, channel=0, clear=True):
        if clear:
            self.clear()
        self.axes.plot(df.Vj/1e-3, df.Is/1e-6, 'o-', label='Channel %d' % channel)
        self.axes.set_title('SIS Channel %d' % channel)
        self.axes.legend(loc='best')
        self.draw()
        
    def clear(self):
        self.axes.cla()
        self.draw()
        
    def save(self):
        self.fig.savefig('test.png')

        

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ivcurve_gui = IVCURVE_GUI()
    
    sys.exit(app.exec_())
        
