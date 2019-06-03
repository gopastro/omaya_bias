import sys, datetime
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QPushButton, QAction, QDesktopWidget, QToolTip, QPushButton, QLineEdit, QTextEdit, QComboBox, qApp, QLabel, QGridLayout, QGroupBox, QHBoxLayout, QVBoxLayout, QFileDialog, QRadioButton)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QTimer

from omayabias.sisbias.sisbias import SISBias
from omayabias.logging import logger
import numpy
import time
import pandas as pd

logger.name = __name__
QIcon.setThemeSearchPaths(['/usr/share/icons'])
QIcon.setThemeName('Humanity')

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

        self.mainMenu = self.menuBar()
        self.add_menu(self.mainMenu)
        
        #Create a toolbar
        self.toolbar = self.addToolBar('Exit')
        self.add_toolbar(self.toolbar)

        
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
        vlayout1 = QVBoxLayout()
        chan0_setbox = QGroupBox("Set Bias")
        chan0_sweepbox = QGroupBox("Sweep")
        chan1_setbox = QGroupBox("Set Bias")
        chan1_sweepbox = QGroupBox("Sweep")
        
        vlayout0.addWidget(chan0_setbox)
        vlayout0.addWidget(chan0_sweepbox)
        chan0_setbox.setLayout(self.add_bias_grid(0))
        chan0_sweepbox.setLayout(self.add_bias_sweep_grid(0))

        vlayout1.addWidget(chan1_setbox)
        vlayout1.addWidget(chan1_sweepbox)
        chan1_setbox.setLayout(self.add_bias_grid(1))
        chan1_sweepbox.setLayout(self.add_bias_sweep_grid(1))        

        
        chan0_groupbox.setLayout(vlayout0)
        chan1_groupbox.setLayout(vlayout1)
        
        #wid.addWidget(bias_groupbox)
        
        self.grid = QGridLayout()
        self.grid.addWidget(bias_groupbox, 0, 0, 5, 1)
        
        
        self.canvas = PlotCanvas(self, width=5, height=4)

        # button = QPushButton('Plot', self)
        # button.setToolTip('plot')
        # button.clicked.connect(m.plot)

        # clearB = QPushButton('Clear', self)
        # clearB.setToolTip('clear plot')
        # clearB.clicked.connect(m.clear)

        # saveB = QPushButton('Save', self)
        # saveB.setToolTip('save plot')
        # saveB.clicked.connect(m.save)

        #self.counter = QLabel('counter', self)
        
        self.grid.addWidget(self.canvas, 0, 1, 7, 4)
        #self.grid.addWidget(button, 5, 1, 1, 4)
        #self.grid.addWidget(clearB, 6, 1, 1, 4)
        #self.grid.addWidget(saveB, 7, 1, 1, 4)
        #self.grid.addWidget(self.counter, 8, 1)        
        
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
        self.bias_timer.start(3000)
        
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
            
    def plot_ivcurve(self, channel):
        self.canvas.plot(self.sweep_data[channel], channel)
        
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
        self.plot_test()

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
        self.draw()
        
    def clear(self):
        self.axes.cla()

    def save(self):
        self.fig.savefig('test.png')


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ivcurve_gui = IVCURVE_GUI()
    


    sys.exit(app.exec_())
        
