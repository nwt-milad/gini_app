from flask import Flask, render_template, request
import sqlite3 as sql
import datetime
import io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app = Flask(__name__)

conn = sql.connect('database.db')
conn.execute('CREATE TABLE IF NOT EXISTS wagers (name TEXT, wage REAL, date text)')


def connect_db():   
   #conectar db
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   cur = con.cursor()
   return cur
def from_db_to_array():
      #seleccionar y extraer la columna que necesitamos
   cur.execute("select wage from wagers")
   rows = cur.fetchall()
   #convertir columna en lista y luego en np.array
   b = []
   for row in rows:   
      b.append(row[0])
   X = np.array(b)
   return X
   


@app.route('/')
def home():
   return render_template('home.html')

@app.route('/addata',methods = ['POST', 'GET'])
def addrec():
   #Trasladar datos introducidos en formulario y guardarlos en db.
   if request.method == 'POST':
      try:
         nm = request.form['nm']
         wg = request.form['wg']
         now = datetime.datetime(2009,5,5)
         str_now = now.date().isoformat()
         
         with sql.connect("database.db") as con:
            now = datetime.datetime.utcnow()
            cur = con.cursor()
            cur.execute("INSERT INTO wagers (name,wage,date) VALUES (?,?,?)",(nm,wg,now.strftime('%Y-%m-%d %H:%M:%S')))
            con.commit()
            msg = "Enformación introducida correctamente."
      except:
         con.rollback()
         msg = "Error al introducir la información. Intentelo de nuevo!"
      
      finally:
         return render_template("person.html",msg=msg ) 
         con.close()
   return render_template('person.html')      

@app.route('/list')
def list():
   #Extraer la tabla entera de la db y desplegarla.
   cur = connect_db()
   cur.execute("select * from wagers")
   rows = cur.fetchall(); 
   return render_template("list.html",rows = rows) 


@app.route('/index-graph')

def gini_index():
   #conectar db
   cur = connect_db()
   #seleccionar y extraer la columna que necesitamos
   cur.execute("select wage from wagers")
   rows = cur.fetchall()
   #convertir columna en lista y luego en np.array
   b = []
   for row in rows:   
      b.append(row[0])
   X = np.array(b)
   #ordenar array y calcular el indice.
   sorted_X = X.copy()
   sorted_X.sort()
   n = X.size
   coef_ = 2. / n
   const_ = (n + 1.) / n
   weighted_sum = sum([(i+1)*yi for i, yi in enumerate(sorted_X)])
   indice = coef_*weighted_sum/(sorted_X.sum()) - const_
   #importar grafico de la siguiente funcion(plot_points) y deplegarlo.
   plot = plot_points()
   return render_template("result.html",indice=indice,plot=plot)
   con.close()


def plot_points():
   """Extraer datos de la DB, situar puntos y mostrar grafico """
    #conectar db
   cur = connect_db()
    #extraer columna de db.
   cur.execute("select wage from wagers")
   rows = cur.fetchall()
    #convertir columna en lista y luego en np.array, y ordenarlo.
   b = []
   for row in rows:   
      b.append(row[0])
   X = np.array(b)
   X.sort()
    #calcular los puntos de la curva
   X_lorenz = X.cumsum() / X.sum()
   X_lorenz = np.insert(X_lorenz, 0, 0)
   X_lorenz[0], X_lorenz[-1] 
    #crear marco y parametros de la figura
   fig = Figure()
   FigureCanvas(fig)
   ax = fig.add_subplot()
   fig, ax = plt.subplots(figsize=[5,5])
    #situar puntos en el grafico
   ax.scatter(np.arange(X_lorenz.size)/(X_lorenz.size-1), X_lorenz, 
           marker=".", color='darkgreen', s=100)
   ax.plot([0,1], [0,1], color='g')
   #ax.set_xlabel('x')
   #ax.set_ylabel('y')
   ax.set_title('Lorenz curve', fontsize= 11)
   ax.grid(True)
    #Cargar imagen en la ram ya que no es un archivo estatico. 
   img = io.StringIO()
   fig.savefig(img, format='svg')
    #clip off the xml headers from the image
   svg_img = '<svg' + img.getvalue().split('<svg')[1]
    
   return svg_img

if __name__ == '__main__':
   app.run(debug = True)

