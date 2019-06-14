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
        """initialize 'IVCURVE_GUI' class"""
        super(IVCURVE_GUI,self).__init__()
        self.bias_widgets = {}
        self.sisbias = SISBias()
        self.lk = Lakeshore()
        self.sweep_data = {}
        self.devsel_cb = {}
        self.devices = [None, None]
        self.sweep_time = [None, None]
        self.skiprows = 2
        self.initUI()
        
    def initUI(self):
        """initialize GUI window"""

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

        #self.setGeometry(10, 10, 650, 475)
        self.setWindowTitle('OMAYA Bias GUI')

        wid = QWidget(self)
        self.setCentralWidget(wid)

        master_groupbox = QGroupBox()
        vlayout = QVBoxLayout()
        master_groupbox.setLayout(vlayout)
        bias_groupbox = QGroupBox()
        hlayout = QHBoxLayout()
        bias_groupbox.setLayout(hlayout)
        temp_groupbox = QGroupBox("Temperature Monitor")
        channels = ['1', '2', '3', '4', '5', '6', '7', '8']
        temp_groupbox.setLayout(self.add_temp_monitor_grid(channels))
        
        vlayout.addWidget(bias_groupbox)
        vlayout.addWidget(temp_groupbox)
    
        chan0_groupbox = QGroupBox("Channel 0")
        chan1_groupbox = QGroupBox("Channel 1")
        hlayout.addWidget(chan0_groupbox)
        hlayout.addWidget(chan1_groupbox)
        
        vlayout0 = QVBoxLayout()
        vlayout1 = QVBoxLayout()
        chan0_seldev_box = QGroupBox("Select Device")
        chan1_seldev_box = QGroupBox("Select Device")
        chan0_setbox = QGroupBox("Set Bias")
        chan0_sweepbox = QGroupBox("Sweep")
        chan1_setbox = QGroupBox("Set Bias")
        chan1_sweepbox = QGroupBox("Sweep")

        chan0_seldev_box.setLayout(self.add_select_device_grid(0))
        chan1_seldev_box.setLayout(self.add_select_device_grid(1))
        vlayout0.addWidget(chan0_seldev_box)
        vlayout0.addWidget(chan0_setbox)
        vlayout0.addWidget(chan0_sweepbox)
        chan0_setbox.setLayout(self.add_bias_grid(0))
        chan0_sweepbox.setLayout(self.add_bias_sweep_grid(0))

        vlayout1.addWidget(chan1_seldev_box)        
        vlayout1.addWidget(chan1_setbox)
        vlayout1.addWidget(chan1_sweepbox)
        chan1_setbox.setLayout(self.add_bias_grid(1))
        chan1_sweepbox.setLayout(self.add_bias_sweep_grid(1))        
        
        chan0_groupbox.setLayout(vlayout0)
        chan1_groupbox.setLayout(vlayout1)
        
        self.grid = QGridLayout()
        self.grid.addWidget(master_groupbox, 0, 0, 5, 1)      

        canvas_groupbox = QGroupBox("IV Curve Plot")
        self.canvas = PlotCanvas(self, width=5, height=4)
        clearB = QPushButton('Clear Plot', self)
        clearB.setToolTip('clear plot')
        clearB.clicked.connect(self.canvas.clear)
        vlayout2 = QVBoxLayout()
        vlayout2.addWidget(self.canvas)
        vlayout2.addWidget(clearB)
        self.addToolBar(QtCore.Qt.BottomToolBarArea,
                        NavigationToolbar2QT(self.canvas, self))
        #vlayout2.addWidget(self.addToolBar(QtCore.Qt.BottomToolBarArea,
        #                                   NavigationToolbar2QT(self.canvas, self)))
        #vlayout2.addWidget(self.addToolBar(NavigationToolbar2QT(self.canvas, self)))
        canvas_groupbox.setLayout(vlayout2)
        
        self.grid.addWidget(canvas_groupbox, 0, 1, 7, 4)

        wid.setLayout(self.grid)        

        self.show()

    def add_menu(self, mainMenu):
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
        exitAct = QAction(QIcon.fromTheme('exit'), 'Exit', self)
        #exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(self.close)
        toolbar.addAction(exitAct)

    def add_temp_monitor_grid(self, channels):
        grid = QGridLayout()
        bf = QFont("Times", 12, QFont.Bold)
        self.temp_labels = {}
        self.temp_widgets = {}
        i = 0
        for chan in channels:
            self.temp_labels[chan] = QLabel()
            self.temp_labels[chan].setText("%s" %chan)
            self.temp_widgets[chan] = QLabel()
            self.temp_widgets[chan].setText("")
            self.temp_widgets[chan].setFont(bf)
            grid.addWidget(self.temp_labels[chan], 0, i+1)
            grid.addWidget(self.temp_widgets[chan], 0, i+2)
            i += 2
        self.add_temp_monitor_hooks()
        return grid

            
    def add_select_device_grid(self, channel):
        grid = QGridLayout()
        dset = QLabel('Select Device: ')
        self.devsel_cb[channel] = QComboBox()
        self.devsel_cb[channel].setEditable(True)
        lis = []
        for sisd in SISDimensions.select().order_by(SISDimensions.id):
            lis.append("GP# %s: %s %s %s" % (sisd.gelpack.description, sisd.sis2letter, sisd.sisrowcol, sisd.gelpack_label))
        self.devsel_cb[channel].addItems(lis)
        if channel == 0:
            self.devsel_cb[channel].currentIndexChanged.connect(self.dev_selection_change0)
        else:
            self.devsel_cb[channel].currentIndexChanged.connect(self.dev_selection_change1)
        grid.addWidget(dset, 0, 0)
        grid.addWidget(self.devsel_cb[channel], 0, 1)
        #print self.devsel_cb.keys()
        return grid

    def dev_selection_change0(self, i):
        #print i, self.devsel_cb.currentText()
        self.devices[0] = self.devsel_cb[0].currentText()
        
    def dev_selection_change1(self, i):
        #print i, self.devsel_cb.currentText()
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

class AdvComboBox(QComboBox):
    
    def __init__(self, parent=None):
        super(AdvComboBox, self).__init__(parent)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setEditable(True)

        # add a filter model to filter matching items
        self.pFilterModel = QtGui.QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # add a completer, which uses the filter model
        self.completer = QtGui.QCompleter(self.pFilterModel, self)
        # always show all (filtered) completions
        self.completer.setCompletionMode(QtGui.QCompleter.UnfilteredPopupCompletion)

        self.setCompleter(self.completer)

        # connect signals

        def filter(text):
            print "Edited: ", text, "type: ", type(text)
            self.pFilterModel.setFilterFixedString(str(text))

        self.lineEdit().textEdited[unicode].connect(filter)
        self.completer.activated.connect(self.on_completer_activated)

    # on selection of an item from the completer, select the corresponding item from combobox
    def on_completer_activated(self, text):
        if text:
            index = self.findText(str(text))
            self.setCurrentIndex(index)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ivcurve_gui = IVCURVE_GUI()
    
    sys.exit(app.exec_())
        
