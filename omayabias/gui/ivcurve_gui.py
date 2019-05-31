import sys, datetime
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QPushButton, QAction, QDesktopWidget, QToolTip, QPushButton, QLineEdit, QTextEdit, QComboBox, qApp, QLabel, QGridLayout, QGroupBox, QHBoxLayout, QVBoxLayout, QFileDialog)
from PyQt5.QtGui import QFont, QIcon
from PyQt5 import QtCore

from omayabias.sisbias.sisbias import SISBias
from omayabias.logging import logger
import numpy
import time
import pandas as pd

logger.name = __name__

class IVCURVE_GUI(QMainWindow):

    def __init__(self):
        """initialize 'GUI' class"""
        super(IVCURVE_GUI,self).__init__()
        self.left = 10
        self.top = 10
        self.title = 'Canvas Test'
        self.width = 640
        self.heigth = 400
        self.bias_widgets = {}
        self.sisbias = SISBias()
        self.sweep_data = {}
        self.initUI()

    def initUI(self):
        """initialize GUI window"""

        #Create a status bar
        self.statusBar().showMessage('Ready')

        #Create a menubar
        #menubar = self.menuBar()
        #fileMenu = menubar.addMenu('&File')
        #fileMenu.addAction(exitAct)

        mainMenu = self.menuBar()
        self.add_menu(mainMenu)
        
        #Create a toolbar
        #self.toolbar = self.addToolBar('Exit')
        #self.toolbar.addAction(exitAct)
        
        #self.setGeometry(10, 10, 650, 475)
        self.setWindowTitle('OMAYA Bias GUI')

        wid = QWidget(self)
        self.setCentralWidget(wid)
        
        bias_groupbox = QGroupBox("Set Bias")
        hlayout = QHBoxLayout()
        bias_groupbox.setLayout(hlayout)
        chan0_groupbox = QGroupBox("Channel 0")
        chan1_groupbox = QGroupBox("Channel 1")
        hlayout.addWidget(chan0_groupbox)
        hlayout.addWidget(chan1_groupbox)
        vlayout0 = QVBoxLayout()
        
        chan0_groupbox.setLayout(self.add_bias_sweep_grid(0))
        chan1_groupbox.setLayout(self.add_bias_sweep_grid(1))
        
        #wid.addWidget(bias_groupbox)
        
        self.grid = QGridLayout()
        self.grid.addWidget(bias_groupbox, 0, 0, 5, 1)
        
        
        m = PlotCanvas(self, width=5, height=4)

        button = QPushButton('Plot', self)
        button.setToolTip('plot')
        button.clicked.connect(m.plot)

        clearB = QPushButton('Clear', self)
        clearB.setToolTip('clear plot')
        clearB.clicked.connect(m.clear)

        saveB = QPushButton('Save', self)
        saveB.setToolTip('save plot')
        saveB.clicked.connect(m.save)

        self.counter = QLabel('counter', self)
        
        self.grid.addWidget(m, 0, 1, 5, 4)
        self.grid.addWidget(button, 5, 1, 1, 4)
        self.grid.addWidget(clearB, 6, 1, 1, 4)
        self.grid.addWidget(saveB, 7, 1, 1, 4)
        self.grid.addWidget(self.counter, 8, 1)        
        
        # vminL = QLabel('Vmin', self)
        # vminTE = QTextEdit()

        # vmaxL = QLabel('Vmax', self)
        # vmaxTE = QTextEdit()
        
        # vstepL = QLabel('Vstep', self)
        # vstepTE = QTextEdit()


        # #self.chanL = QLabel('Channel')
        # #self.chanCombo = QComboBox()
        # #self.chanCombo.addItem("0")
        # #self.chanCombo.addItem("1")






        # self.grid.setSpacing(10)

        # self.grid.addWidget(m, 1, 0)
        # self.grid.addWidget(button, 2, 0)
        # self.grid.addWidget(clearB, 3, 0)
        # self.grid.addWidget(saveB, 4, 0)
        # self.grid.addWidget(vminL, 5, 0)
        # self.grid.addWidget(vminTE, 5, 1)
        # self.grid.addWidget(vmaxL, 6, 0)
        # self.grid.addWidget(vmaxTE, 6, 1)
        # self.grid.addWidget(vstepL, 7, 0)
        # self.grid.addWidget(vstepTE, 7, 1)
        # self.grid.addWidget(self.counter, 8, 0)

        wid.setLayout(self.grid)        

        self.show()

    def add_menu(self, mainMenu):
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        searchMenu = mainMenu.addMenu('Search')
        toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')
        
        exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)
    
        
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
        
        grid.addWidget(vminL, 0, 0)
        grid.addWidget(self.bias_widgets['Vmin%d' % channel],  0, 1)
        grid.addWidget(vmaxL, 1, 0)
        grid.addWidget(self.bias_widgets['Vmax%d' % channel],  1, 1)
        grid.addWidget(vstep, 2, 0)
        grid.addWidget(self.bias_widgets['Vstep%d' % channel],  2, 1)
        grid.addWidget(self.bias_widgets['sweepbtn%d' % channel], 3, 0, 1, 2)
        grid.addWidget(self.bias_widgets['savebtn%d' % channel], 4, 0, 1, 2)
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

    def save_sweep(self, btn):
        txt = btn.text()
        channel = int(txt.split('Save Channel ')[1])
        print "Saving Channel: %d" % channel
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.csv)", options=options)
        if fileName:
            print "Saving Channel %d data to %s" % (channel, fileName)
            self.sweep_data[channel].to_csv(fileName)
            
        
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
        self.plot()

    def plot(self):
        data = [random.random() for i in range(25)]
        self.axes.plot(data, 'r-')
        
        self.axes.set_title('SIS Channel 0')
        self.draw()
    
    def clear(self):
        self.axes.cla()

    def save(self):
        self.fig.savefig('test.png')


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ivcurve_gui = IVCURVE_GUI()
    
    def update_label():
       current_time = str(datetime.datetime.now().second)
       ivcurve_gui.counter.setText(current_time)

    timer = QtCore.QTimer()
    timer.timeout.connect(update_label)
    timer.start(1000)

    sys.exit(app.exec_())
        
