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

        UpdateButton = QtWidgets.QPushButton('Update',self)
        UpdateButton.clicked.connect(self.update)

        self.canvas = MplCanvas(self)
        self.data = Data(testing=True)
        self.canvas.dataplot(self.data)

        layout.addWidget(self.canvas)
        layout.addWidget(UpdateButton)

        self.container_plot =QtWidgets.QWidget()
        self.container_plot.setLayout(layout)
        #self.data.create_db()
        self.data.grab_db_info()

        self.setCentralWidget(self.container_plot)

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

    def __init__(self,testing=True,db_path='./database.db'):

        try:
            self.con = sqlite3.connect(db_path)
            self.cur=self.con.cursor()
        except Error as e:
            print(e)
            stop

        if testing:
            self.x=np.linspace(0,10,100)
            self.y=np.sin(self.x)

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


    def data_update(self):
        self.y=self.y*0


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width,height), dpi=dpi)
        self.ax =  fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


    def dataplot(self,data):
        self.ax.plot(data.x,data.y)


def main():

    print("Openning application")


    window = MainWindow()
    window.show()

    app.exec_()

if __name__ == "__main__":
    main()

