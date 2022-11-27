import sqlite3
import json
from sqlite3 import Error
import numpy as np

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

