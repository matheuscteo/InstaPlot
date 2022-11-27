import sys
import sqlite3
import json
from sqlite3 import Error
from PyQt5 import QtWidgets, QtCore
import matplotlib as mpl
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

mpl.use('Qt5Agg')
app = QtWidgets.QApplication(sys.argv)

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self,*args,**kwargs):
        super(MainWindow, self).__init__(*args,**kwargs)

        #Title
        self.setWindowTitle("InstaPlot")

        layout = QtWidgets.QVBoxLayout()

        UpdateButton = QtWidgets.QPushButton('Plot',self)
        UpdateButton.clicked.connect(self.plot_current)

        self.canvas = MplCanvas(self)
        self.data = Data()
        #self.canvas.dataplot(self.data)
        layout.addWidget(self.canvas)

        self.data.grab_db_info()
        self.set_combobox_id()

        layout_combobox = QtWidgets.QHBoxLayout()

        layout_combobox_id = QtWidgets.QVBoxLayout()
        layout_combobox_id.setAlignment(QtCore.Qt.AlignCenter)
        layout_combobox_id.addWidget(QtWidgets.QLabel('Data ID'))
        layout_combobox_id.addWidget(self.combobox_id)

        self.set_combobox_axes()

        layout_combobox_axes = QtWidgets.QVBoxLayout()
        layout_combobox_axes.addWidget(self.combobox_ax1)
        layout_combobox_axes.addWidget(self.combobox_ax2)

        layout_combobox.addLayout(layout_combobox_id)
        layout_combobox.addLayout(layout_combobox_axes)

        layout.addLayout(layout_combobox)

        layout.addWidget(UpdateButton)

        self.container_plot =QtWidgets.QWidget()
        self.container_plot.setLayout(layout)
        #self.data.create_db()

        self.setCentralWidget(self.container_plot)

    def set_combobox_axes(self):

        self.combobox_ax1=QtWidgets.QComboBox(self)
        self.combobox_ax1.addItems(self.data.cols)
        self.combobox_ax1.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)

        self.combobox_ax2=QtWidgets.QComboBox(self)
        self.combobox_ax2.addItems(self.data.cols)
        self.combobox_ax2.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)

    def set_combobox_id(self):

        self.combobox_id=QtWidgets.QComboBox(self)
        self.combobox_id.addItems([str(id) for id in self.data.ids])
        self.combobox_id.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)

    def plot_current(self):

        id = self.combobox_id.currentText()
        X = self.combobox_ax1.currentText()
        Y = self.combobox_ax2.currentText()

        X_data=self.data.grab_data(id,X)
        Y_data=self.data.grab_data(id,Y)

        self.canvas.dataplot(X_data,Y_data)

    def update(self):

        self.canvas.ax.cla()
        self.data.data_update()
        self.canvas.dataplot(self.data)
        self.canvas.draw()
        print("Data updated and drawan")

    def closeEvent(self,event):

        if hasattr(self.data,'cur'):
            self.data.cur.close()

        if hasattr(self.data,'con'):
            print('closing DB')
            self.data.con.close()

        print('Have a nice day!!')


class Data():

    def __init__(self,db_path='./database.db'):

        try:
            self.con = sqlite3.connect(db_path)
            self.cur=self.con.cursor()
        except Error as e:
            print(e)
            stop

    def grab_db_info(self):

        cols=self.cur.execute("SELECT * FROM DATA").description
        cols=np.array(cols)
        cols=cols[cols!=None]
        cols=cols[cols!='id']

        ids=self.cur.execute("SELECT id FROM DATA").fetchall()
        ids=np.array(ids).reshape(1,len(ids))
        ids=ids[0]

        self.ids=ids
        self.cols=cols

    def grab_data(self,id,ax):

        self.cur.execute("SELECT {} FROM DATA WHERE id is {}".format(ax,id))
        ax_data=self.cur.fetchall()
        ax_data=json.loads(ax_data[0][0])
        return ax_data

    def create_db(self):

        self.cur.execute("""CREATE TABLE IF NOT EXISTS data
                        (id INTEGER PRIMARY KEY,
                        arrayX BLOB,arrayY BLOB)""")

        X=np.linspace(0,10,50)
        for i in range(0,20):
            Y=np.random.random(50)
            self.cur.execute("INSERT INTO data VALUES (?,?,?)",
                       (None, json.dumps(X.tolist()), json.dumps(Y.tolist())))
        self.con.commit()


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width,height), dpi=dpi)
        self.ax =  fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


    def dataplot(self,X_data,Y_data):
        self.ax.cla()
        self.ax.plot(X_data,Y_data)
        self.draw()


def main():

    print("Openning application")


    window = MainWindow()
    window.show()

    app.exec_()

if __name__ == "__main__":
    main()

