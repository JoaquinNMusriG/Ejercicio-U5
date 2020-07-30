from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import hashlib

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Usuarios, Productos, Pedidos, ItemsPedidos

@app.route('/', methods = ['GET','POST'])
def inicio():
	if request.method == 'POST':
		if (not request.form['dni']) or (not request.form['clave']):
			return render_template('error.html', error="Por favor ingrese los datos requeridos")
		else:
			usuario_actual = Usuarios.query.filter_by(DNI = request.form['dni']).first()
			if usuario_actual is None:
				return render_template('error.html', error="El dni no está registrado")
			else:
				contraseña = hashlib.md5(bytes(request.form['clave'], encoding='utf-8'))
				if contraseña.hexdigest() == usuario_actual.Clave:
					if usuario_actual.Tipo == 'Mozo':
						return redirect(url_for('Mozo', usuarioDNI=usuario_actual.DNI))
					else:
						return redirect(url_for('Cocinero', usuarioDNI=usuario_actual.DNI))
				else:
					return render_template('error.html', error="La contraseña es incorrecta")
	else:
		return render_template('inicio.html')

@app.route('/Mozo/<usuarioDNI>', methods = ['GET','POST'])
def Mozo(usuarioDNI):
	import sqlite3

	conn = sqlite3.connect('data.db')
	cur = conn.cursor()

	items = ItemsPedidos.query.filter_by(NumPedido = None).all()
	for item_anulados in items:
		cur.execute('DELETE FROM ItemsPedidos WHERE NumItem = ?', (item_anulados.NumItem, ))
	conn.commit()

	cur.close()

	return render_template('funciones_mozo.html', usuario = usuarioDNI)

@app.route('/Cocinero/<usuarioDNI>', methods = ['GET','POST'])
def Cocinero(usuarioDNI):
	if request.method == 'POST':
		for i in request.form:
			item = ItemsPedidos.query.filter_by(NumItem=i).first()
			item.Estado="Listo"
			db.session.commit()
	validos = []
	for pedido in Pedidos.query.all():
		if pedido.items.filter_by(Estado="Pendiente").all():
			validos.append(pedido)
	return render_template('funcion_cocinero.html', usuario = usuarioDNI, pedidos = validos)

@app.route("/Mozo/<usuarioDNI>/Pedido", methods=['GET','POST'])
def nuevo_pedido(usuarioDNI):
	if request.method == 'POST':
		if request.form['item'] != 'Terminar Pedido':
			if request.form['item'] != 'Confirmar':
				producto=Productos.query.filter_by(NumProducto = request.form['item']).first()
				item = ItemsPedidos(Estado = 'Pendiente', NumProducto = producto.NumProducto, Precio = producto.PrecioUnitario)
				db.session.add(item)
				db.session.commit()
				return render_template('nuevo_pedido.html', usuario = usuarioDNI, productos = Productos.query.all(), pedido = ItemsPedidos.query.filter_by(NumPedido = None).all(), mesa = request.form['Mesa'])
			else:
				total_compra = 0
				items = ItemsPedidos.query.filter_by(NumPedido = None).all()
				for item_pedidos in items:
					total_compra += float(item_pedidos.Precio)
				pedido=Pedidos(Fecha=datetime.today(), Mesa=request.form["Mesa"], DNIMozo=usuarioDNI, Cobrado='False', Total = total_compra)
				db.session.add(pedido)
				db.session.commit()
				id=Pedidos.query.all()[-1].NumPedido
				items = ItemsPedidos.query.filter_by(NumPedido = None).all()
				for item_pedidos in items:
					item_pedidos.NumPedido = id
					db.session.add(item_pedidos)
				db.session.commit()
				return render_template('agregar_observacion.html', usuario = usuarioDNI)
		else:
			pedido_final=Pedidos.query.all()[-1]
			pedido_final.Observacion = request.form['observaciones']
			db.session.add(pedido_final)
			db.session.commit()
			return render_template('funciones_mozo.html', usuario = usuarioDNI)
	else:
		return render_template('nuevo_pedido.html', usuario = usuarioDNI, productos = Productos.query.all())

@app.route("/Mozo/<usuarioDNI>/Listado", methods=['GET','POST'])
def listar_pedidos(usuarioDNI):
	#validos = []
	#for pedido in Pedidos.query.all():
	#	if (pedido.Fecha.date() == datetime.today().date()):         Pedidos del dia de hoy
	#		validos.append(pedido)
	#enviar validos por el argumento pedidos   - sino enviar Pedidos.query.filter_by(Cobrado='False').all()
	return render_template('listar_pedidos.html', usuario = usuarioDNI, pedidos = Pedidos.query.filter_by(Cobrado='False').all())

if __name__ == '__main__':
	db.create_all()
	app.run(debug = True)
