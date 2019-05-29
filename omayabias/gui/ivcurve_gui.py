import sys, datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QPushButton, QAction, QDesktopWidget, QToolTip, QPushButton, QLineEdit, QTextEdit, QComboBox, qApp, QLabel, QGridLayout)
from PyQt5.QtGui import QFont
from PyQt5 import QtCore

class IVCURVE_GUI(QMainWindow):

    def __init__(self):
        """initialize 'GUI' class"""
        super(IVCURVE_GUI,self).__init__()
        self.left = 10
        self.top = 10
        self.title = 'Canvas Test'
        self.width = 640
        self.heigth = 400
        self.initUI()

    def initUI(self):
        """initialize GUI window"""

        #Create a status bar
        self.statusBar().showMessage('Ready')

        #Create a menubar
        #menubar = self.menuBar()
        #fileMenu = menubar.addMenu('&File')
        #fileMenu.addAction(exitAct)
        
        #Create a toolbar
        #self.toolbar = self.addToolBar('Exit')
        #self.toolbar.addAction(exitAct)
        
        self.setGeometry(10, 10, 650, 475)
        self.setWindowTitle('SIS Junction IV Curve')

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

        vminL = QLabel('Vmin', self)
        vminTE = QTextEdit()

        vmaxL = QLabel('Vmax', self)
        vmaxTE = QTextEdit()
        
        vstepL = QLabel('Vstep', self)
        vstepTE = QTextEdit()


        #self.chanL = QLabel('Channel')
        #self.chanCombo = QComboBox()
        #self.chanCombo.addItem("0")
        #self.chanCombo.addItem("1")

        self.counter = QLabel('counter', self)

        wid = QWidget(self)
        self.setCentralWidget(wid)

        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(m, 1, 0)
        self.grid.addWidget(button, 2, 0)
        self.grid.addWidget(clearB, 3, 0)
        self.grid.addWidget(saveB, 4, 0)
        self.grid.addWidget(vminL, 5, 0)
        self.grid.addWidget(vminTE, 5, 1)
        self.grid.addWidget(vmaxL, 6, 0)
        self.grid.addWidget(vmaxTE, 6, 1)
        self.grid.addWidget(vstepL, 7, 0)
        self.grid.addWidget(vstepTE, 7, 1)
        self.grid.addWidget(self.counter, 8, 0)

        wid.setLayout(self.grid)        

        self.show()

    def center(self):
        """detects desktop resolution and sets window in center"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

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
        
